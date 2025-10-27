"""
Özel Mağaza Admin Paneli Views
Modern, sidebar'lı admin panel - Django Admin'den bağımsız
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q, F, Avg, Max, Min
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from datetime import timedelta
from decimal import Decimal
import json

from .models import (
    Order, OrderItem, Product, Category, Cart, CartItem,
    EproloSyncLog, EproloSettings, PrintifySyncLog, PrintifySettings
)
from .eprollo_service import EprolloAPIService
from .printify_service import PrintifyService


@staff_member_required
def admin_dashboard(request):
    """Ana Dashboard - İstatistikler ve grafikler"""
    
    # Tarih aralıkları
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_7_days = today - timedelta(days=7)
    last_30_days = today - timedelta(days=30)
    
    # Sipariş istatistikleri
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    confirmed_orders = Order.objects.filter(status='confirmed').count()
    shipped_orders = Order.objects.filter(status='shipped').count()
    delivered_orders = Order.objects.filter(status='delivered').count()
    
    # Bu ay vs geçen ay karşılaştırması
    this_month_orders = Order.objects.filter(created_at__gte=this_month_start).count()
    last_month_orders = Order.objects.filter(
        created_at__gte=last_month_start,
        created_at__lt=this_month_start
    ).count()
    
    # Gelir istatistikleri (sadece ödenenler)
    total_revenue = Order.objects.filter(is_paid=True).aggregate(
        total=Sum('total')
    )['total'] or Decimal('0')
    
    this_month_revenue = Order.objects.filter(
        created_at__gte=this_month_start,
        is_paid=True
    ).aggregate(total=Sum('total'))['total'] or Decimal('0')
    
    last_month_revenue = Order.objects.filter(
        created_at__gte=last_month_start,
        created_at__lt=this_month_start,
        is_paid=True
    ).aggregate(total=Sum('total'))['total'] or Decimal('0')
    
    # Ürün istatistikleri
    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()
    eprolo_products = Product.objects.filter(source='eprolo').count()
    low_stock = Product.objects.filter(stock_status='low_stock').count()
    out_of_stock = Product.objects.filter(stock_status='out_of_stock').count()
    
    # Günlük satış grafiği (Son 7 gün)
    daily_sales = []
    for i in range(7):
        date = today - timedelta(days=6-i)
        revenue = Order.objects.filter(
            created_at__date=date,
            is_paid=True
        ).aggregate(total=Sum('total'))['total'] or Decimal('0')
        orders = Order.objects.filter(created_at__date=date).count()
        
        daily_sales.append({
            'date': date.strftime('%d/%m'),
            'revenue': float(revenue),
            'orders': orders
        })
    
    # En çok satan ürünler (Son 30 gün)
    top_products = Product.objects.annotate(
        recent_sales=Sum(
            'orderitem__quantity',
            filter=Q(
                orderitem__order__created_at__gte=last_30_days,
                orderitem__order__is_paid=True
            )
        ),
        recent_revenue=Sum(
            F('orderitem__quantity') * F('orderitem__product_price'),
            filter=Q(
                orderitem__order__created_at__gte=last_30_days,
                orderitem__order__is_paid=True
            )
        )
    ).filter(recent_sales__gt=0).order_by('-recent_sales')[:5]
    
    # Son siparişler
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:8]
    
    # Kategori bazlı satışlar
    category_sales = Category.objects.annotate(
        sales_count=Count(
            'products__orderitem',
            filter=Q(products__orderitem__order__is_paid=True)
        ),
        revenue=Sum(
            F('products__orderitem__quantity') * F('products__orderitem__product_price'),
            filter=Q(products__orderitem__order__is_paid=True)
        )
    ).filter(sales_count__gt=0).order_by('-revenue')[:5]
    
    # EPROLO istatistikleri
    eprolo_stats = {
        'total_products': eprolo_products,
        'active_products': Product.objects.filter(source='eprolo', is_active=True).count(),
        'out_of_stock': Product.objects.filter(source='eprolo', stock_status='out_of_stock').count(),
        'last_sync': EproloSyncLog.objects.filter(status='success').order_by('-completed_at').first(),
        'pending_syncs': EproloSyncLog.objects.filter(status='partial').count(),
    }
    
    # Yüzde değişimler
    order_change = ((this_month_orders - last_month_orders) / last_month_orders * 100) if last_month_orders > 0 else 0
    revenue_change = ((this_month_revenue - last_month_revenue) / last_month_revenue * 100) if last_month_revenue > 0 else 0
    
    context = {
        # Özet kartlar
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_products': total_products,
        'active_products': active_products,
        
        # Sipariş durumları
        'pending_orders': pending_orders,
        'confirmed_orders': confirmed_orders,
        'shipped_orders': shipped_orders,
        'delivered_orders': delivered_orders,
        
        # Bu ay istatistikleri
        'this_month_orders': this_month_orders,
        'this_month_revenue': this_month_revenue,
        'order_change': round(order_change, 1),
        'revenue_change': round(revenue_change, 1),
        
        # Stok uyarıları
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        
        # Grafikler ve listeler
        'daily_sales': json.dumps(daily_sales),
        'top_products': top_products,
        'recent_orders': recent_orders,
        'category_sales': category_sales,
        
        # EPROLO
        'eprolo_stats': eprolo_stats,
        'eprolo_products': eprolo_products,
    }
    
    return render(request, 'shop/custom_admin/dashboard.html', context)


@staff_member_required
def admin_products(request):
    """Ürün Yönetimi"""
    
    # Filtreler
    search = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    source = request.GET.get('source', '')
    stock_status = request.GET.get('stock_status', '')
    status = request.GET.get('status', '')
    
    products = Product.objects.select_related('category').all()
    
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(eprolo_sku__icontains=search)
        )
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    if source:
        products = products.filter(source=source)
    
    if stock_status:
        products = products.filter(stock_status=stock_status)
    
    if status == 'active':
        products = products.filter(is_active=True)
    elif status == 'inactive':
        products = products.filter(is_active=False)
    
    # Sıralama
    sort = request.GET.get('sort', '-created_at')
    products = products.order_by(sort)
    
    # Sayfalama
    paginator = Paginator(products, 20)
    page = request.GET.get('page', 1)
    products_page = paginator.get_page(page)
    
    categories = Category.objects.all()
    
    context = {
        'products': products_page,
        'categories': categories,
        'search': search,
        'category_id': category_id,
        'source': source,
        'stock_status': stock_status,
        'status': status,
        'sort': sort,
    }
    
    return render(request, 'shop/custom_admin/products.html', context)


@staff_member_required
def admin_product_edit(request, product_id=None):
    """Ürün Düzenleme/Ekleme"""
    
    if product_id:
        product = get_object_or_404(Product, id=product_id)
    else:
        product = None
    
    if request.method == 'POST':
        # Form işleme
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        short_description = request.POST.get('short_description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        is_active = request.POST.get('is_active') == 'on'
        is_featured = request.POST.get('is_featured') == 'on'
        
        if product:
            product.name = name
            product.category_id = category_id
            product.description = description
            product.short_description = short_description
            product.price = price
            product.stock = stock
            product.is_active = is_active
            product.is_featured = is_featured
            product.save()
            messages.success(request, 'Ürün başarıyla güncellendi.')
        else:
            product = Product.objects.create(
                name=name,
                category_id=category_id,
                description=description,
                short_description=short_description,
                price=price,
                stock=stock,
                is_active=is_active,
                is_featured=is_featured,
                source='manual'
            )
            messages.success(request, 'Ürün başarıyla eklendi.')
        
        return redirect('shop:admin_products')
    
    categories = Category.objects.all()
    
    context = {
        'product': product,
        'categories': categories,
    }
    
    return render(request, 'shop/custom_admin/product_edit.html', context)


@staff_member_required
def admin_orders(request):
    """Sipariş Yönetimi"""
    
    # Filtreler
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    payment_method = request.GET.get('payment_method', '')
    is_paid = request.GET.get('is_paid', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    orders = Order.objects.select_related('user').prefetch_related('items__product').all()
    
    if search:
        orders = orders.filter(
            Q(order_number__icontains=search) |
            Q(user__username__icontains=search) |
            Q(full_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )
    
    if status:
        orders = orders.filter(status=status)
    
    if payment_method:
        orders = orders.filter(payment_method=payment_method)
    
    if is_paid == 'yes':
        orders = orders.filter(is_paid=True)
    elif is_paid == 'no':
        orders = orders.filter(is_paid=False)
    
    if date_from:
        orders = orders.filter(created_at__date__gte=date_from)
    
    if date_to:
        orders = orders.filter(created_at__date__lte=date_to)
    
    # Sıralama
    orders = orders.order_by('-created_at')
    
    # Sayfalama
    paginator = Paginator(orders, 20)
    page = request.GET.get('page', 1)
    orders_page = paginator.get_page(page)
    
    # İstatistikler
    stats = {
        'total': Order.objects.count(),
        'pending': Order.objects.filter(status='pending').count(),
        'confirmed': Order.objects.filter(status='confirmed').count(),
        'shipped': Order.objects.filter(status='shipped').count(),
        'delivered': Order.objects.filter(status='delivered').count(),
        'cancelled': Order.objects.filter(status='cancelled').count(),
        'unpaid': Order.objects.filter(is_paid=False).count(),
    }
    
    context = {
        'orders': orders_page,
        'stats': stats,
        'search': search,
        'status_filter': status,
        'payment_method': payment_method,
        'is_paid': is_paid,
        'date_from': date_from,
        'date_to': date_to,
        'status_choices': Order.STATUS_CHOICES,
        'payment_choices': Order.PAYMENT_METHOD,
    }
    
    return render(request, 'shop/custom_admin/orders.html', context)


@staff_member_required
def admin_order_detail(request, order_id):
    """Sipariş Detay ve Düzenleme"""
    
    order = get_object_or_404(
        Order.objects.select_related('user').prefetch_related('items__product'),
        id=order_id
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_status':
            new_status = request.POST.get('status')
            order.status = new_status
            order.save()
            messages.success(request, f'Sipariş durumu "{order.get_status_display()}" olarak güncellendi.')
        
        elif action == 'mark_paid':
            order.is_paid = True
            order.paid_at = timezone.now()
            order.save()
            messages.success(request, 'Sipariş ödendi olarak işaretlendi.')
        
        elif action == 'update_notes':
            order.admin_notes = request.POST.get('admin_notes')
            order.save()
            messages.success(request, 'Admin notları güncellendi.')
        
        return redirect('shop:admin_order_detail', order_id=order.id)
    
    context = {
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
    }
    
    return render(request, 'shop/custom_admin/order_detail.html', context)


@staff_member_required
def admin_categories(request):
    """Kategori Yönetimi"""
    
    categories = Category.objects.annotate(
        product_count=Count('products'),
        active_product_count=Count('products', filter=Q(products__is_active=True))
    ).order_by('order', 'name')
    
    # İstatistikler
    total_categories = categories.count()
    active_categories = categories.filter(is_active=True).count()
    total_products = Product.objects.count()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            name = request.POST.get('name')
            description = request.POST.get('description')
            icon = request.POST.get('icon')
            order = request.POST.get('order', 0)
            
            Category.objects.create(
                name=name,
                description=description,
                icon=icon,
                order=order
            )
            messages.success(request, 'Kategori başarıyla eklendi.')
        
        elif action == 'edit':
            category_id = request.POST.get('category_id')
            category = get_object_or_404(Category, id=category_id)
            category.name = request.POST.get('name')
            category.description = request.POST.get('description')
            category.icon = request.POST.get('icon')
            category.order = request.POST.get('order', 0)
            category.is_active = request.POST.get('is_active') == 'on'
            category.save()
            messages.success(request, 'Kategori başarıyla güncellendi.')
        
        elif action == 'delete':
            category_id = request.POST.get('category_id')
            category = get_object_or_404(Category, id=category_id)
            if category.products.count() == 0:
                category.delete()
                messages.success(request, 'Kategori silindi.')
            else:
                messages.error(request, 'Bu kategoride ürünler var. Önce ürünleri başka kategoriye taşıyın.')
        
        return redirect('shop:admin_categories')
    
    context = {
        'categories': categories,
        'total_categories': total_categories,
        'active_categories': active_categories,
        'total_products': total_products,
    }
    
    return render(request, 'shop/custom_admin/categories.html', context)


@staff_member_required
def admin_eprolo(request):
    """EPROLO Yönetim Paneli"""
    
    # EPROLO Ayarları
    settings = EproloSettings.get_settings()
    
    # İstatistikler
    eprolo_products = Product.objects.filter(source='eprolo')
    stats = {
        'total': eprolo_products.count(),
        'active': eprolo_products.filter(is_active=True).count(),
        'out_of_stock': eprolo_products.filter(stock_status='out_of_stock').count(),
        'needs_sync': eprolo_products.filter(
            Q(eprolo_last_sync__isnull=True) |
            Q(eprolo_last_sync__lt=timezone.now() - timedelta(days=7))
        ).count(),
    }
    
    # Son senkronizasyon logları
    sync_logs = EproloSyncLog.objects.order_by('-started_at')[:10]
    
    # EPROLO ürünleri
    products = eprolo_products.select_related('category').order_by('-eprolo_last_sync')[:20]
    
    # Kategoriler (senkronizasyon için)
    categories = Category.objects.all().order_by('name')
    
    context = {
        'settings': settings,
        'stats': stats,
        'sync_logs': sync_logs,
        'products': products,
        'categories': categories,
        'total_eprolo_products': stats['total'],
        'active_eprolo_products': stats['active'],
        'out_of_stock_eprolo': stats['out_of_stock'],
        'total_eprolo_sales': eprolo_products.aggregate(Sum('sales_count'))['sales_count__sum'] or 0,
    }
    
    return render(request, 'shop/custom_admin/eprolo.html', context)


@staff_member_required
def admin_eprolo_settings(request):
    """EPROLO Ayarları"""
    
    settings = EproloSettings.get_settings()
    
    if request.method == 'POST':
        settings.api_key = request.POST.get('api_key', '')
        settings.api_secret = request.POST.get('api_secret', '')
        settings.use_mock = request.POST.get('use_mock') == 'on'
        settings.usd_to_try_rate = request.POST.get('usd_to_try_rate', '34.50')
        settings.default_profit_margin = request.POST.get('default_profit_margin', '30.00')
        settings.auto_update_prices = request.POST.get('auto_update_prices') == 'on'
        settings.auto_update_stock = request.POST.get('auto_update_stock') == 'on'
        settings.auto_create_eprolo_orders = request.POST.get('auto_create_eprolo_orders') == 'on'
        
        if request.POST.get('default_category'):
            settings.default_category_id = request.POST.get('default_category')
        
        settings.save()
        messages.success(request, 'EPROLO ayarları kaydedildi.')
        return redirect('shop:admin_eprolo')
    
    categories = Category.objects.all()
    
    # Örnek hesaplamalar (template'te mul filtresi olmadığı için)
    example_usd_price = 10.0
    example_cost_try = float(settings.usd_to_try_rate) * example_usd_price
    example_profit_margin = float(settings.default_profit_margin)
    example_sale_price = example_cost_try * (1 + example_profit_margin / 100)
    
    context = {
        'settings': settings,
        'categories': categories,
        'example_usd_price': example_usd_price,
        'example_cost_try': round(example_cost_try, 2),
        'example_sale_price': round(example_sale_price, 2),
    }
    
    return render(request, 'shop/custom_admin/eprolo_settings.html', context)


@staff_member_required
def admin_eprolo_sync(request):
    """EPROLO Senkronizasyon"""
    from .services import EproloService, EproloAPIError
    
    if request.method == 'POST':
        sync_type = request.POST.get('sync_type')
        category_id = request.POST.get('category_id')
        
        try:
            service = EproloService()
            
            if sync_type == 'import_products':
                if not category_id:
                    messages.error(request, 'Lütfen bir kategori seçin.')
                    return redirect('shop:admin_eprolo')
                
                # Kategori bazlı ürün senkronizasyonu başlat
                result = service.sync_products_by_category(int(category_id))
                
                messages.success(request, 
                    f'Senkronizasyon tamamlandı! Kategori: {result["category"]}, '
                    f'Toplam: {result["total"]}, Başarılı: {result["success"]}, '
                    f'Başarısız: {result["failed"]}'
                )
            
            elif sync_type == 'update_prices':
                if not category_id:
                    messages.error(request, 'Lütfen bir kategori seçin.')
                    return redirect('shop:admin_eprolo')
                
                # Fiyat güncelleme
                result = service.update_prices_by_category(int(category_id))
                messages.success(request, 
                    f'Fiyat güncelleme tamamlandı! '
                    f'Kategori: {result["category"]}, Güncellenen: {result["updated"]}'
                )
            
            elif sync_type == 'update_stock':
                if not category_id:
                    messages.error(request, 'Lütfen bir kategori seçin.')
                    return redirect('shop:admin_eprolo')
                
                # Stok güncelleme
                result = service.update_stock_by_category(int(category_id))
                messages.success(request, 
                    f'Stok güncelleme tamamlandı! '
                    f'Kategori: {result["category"]}, Güncellenen: {result["updated"]}'
                )
        
        except EproloAPIError as e:
            messages.error(request, f'Senkronizasyon hatası: {str(e)}')
        except Exception as e:
            messages.error(request, f'Beklenmeyen hata: {str(e)}')
    
    return redirect('shop:admin_eprolo')


@staff_member_required
def admin_statistics(request):
    """İstatistik ve Raporlar"""
    
    period = request.GET.get('period', '30')
    days = int(period)
    
    start_date = timezone.now().date() - timedelta(days=days)
    
    # Günlük satışlar
    daily_stats = []
    for i in range(days):
        date = start_date + timedelta(days=i)
        orders = Order.objects.filter(created_at__date=date)
        revenue = orders.filter(is_paid=True).aggregate(Sum('total'))['total'] or Decimal('0')
        
        daily_stats.append({
            'date': date.strftime('%Y-%m-%d'),
            'orders': orders.count(),
            'revenue': float(revenue),
        })
    
    # Kategori istatistikleri
    category_stats = Category.objects.annotate(
        total_sales=Count(
            'products__orderitem',
            filter=Q(
                products__orderitem__order__created_at__gte=start_date,
                products__orderitem__order__is_paid=True
            )
        ),
        total_revenue=Sum(
            F('products__orderitem__quantity') * F('products__orderitem__product_price'),
            filter=Q(
                products__orderitem__order__created_at__gte=start_date,
                products__orderitem__order__is_paid=True
            )
        )
    ).filter(total_sales__gt=0).order_by('-total_revenue')
    
    # En çok satan ürünler
    top_products = Product.objects.annotate(
        total_sales=Sum(
            'orderitem__quantity',
            filter=Q(
                orderitem__order__created_at__gte=start_date,
                orderitem__order__is_paid=True
            )
        ),
        total_revenue=Sum(
            F('orderitem__quantity') * F('orderitem__product_price'),
            filter=Q(
                orderitem__order__created_at__gte=start_date,
                orderitem__order__is_paid=True
            )
        )
    ).filter(total_sales__gt=0).order_by('-total_sales')[:10]
    
    context = {
        'period': period,
        'daily_stats': json.dumps(daily_stats),
        'category_stats': category_stats,
        'top_products': top_products,
    }
    
    return render(request, 'shop/custom_admin/statistics.html', context)


@staff_member_required
def admin_settings(request):
    """Genel Ayarlar"""
    
    eprolo_settings = EproloSettings.get_settings()
    
    if request.method == 'POST':
        # EPROLO ayarlarını güncelle
        eprolo_settings.usd_to_try_rate = request.POST.get('usd_to_try_rate', '34.50')
        eprolo_settings.default_profit_margin = request.POST.get('default_profit_margin', '30.00')
        eprolo_settings.low_stock_threshold = request.POST.get('low_stock_threshold', 5)
        eprolo_settings.out_of_stock_threshold = request.POST.get('out_of_stock_threshold', 0)
        eprolo_settings.save()
        
        messages.success(request, 'Ayarlar kaydedildi.')
        return redirect('shop:admin_settings')
    
    categories = Category.objects.all()
    
    context = {
        'eprolo_settings': eprolo_settings,
        'categories': categories,
    }
    
    return render(request, 'shop/custom_admin/settings.html', context)


@staff_member_required
def admin_printify(request):
    """Printify Ana Sayfa"""
    
    printify_settings = PrintifySettings.get_settings()
    
    # Son senkronizasyon logları
    recent_syncs = PrintifySyncLog.objects.all()[:10]
    
    # İstatistikler
    total_printify_products = Product.objects.filter(source='printify').count()
    active_printify_products = Product.objects.filter(source='printify', is_active=True).count()
    
    # Son 30 günün sync istatistikleri
    last_30_days = timezone.now() - timedelta(days=30)
    sync_stats = PrintifySyncLog.objects.filter(started_at__gte=last_30_days).aggregate(
        total_syncs=Count('id'),
        successful_syncs=Count('id', filter=Q(status='completed')),
        failed_syncs=Count('id', filter=Q(status='failed')),
    )
    
    context = {
        'printify_settings': printify_settings,
        'recent_syncs': recent_syncs,
        'total_printify_products': total_printify_products,
        'active_printify_products': active_printify_products,
        'sync_stats': sync_stats,
    }
    
    return render(request, 'shop/custom_admin/printify/dashboard.html', context)


@staff_member_required
def admin_printify_settings(request):
    """Printify Ayarları"""
    
    printify_settings = PrintifySettings.get_settings()
    categories = Category.objects.all()
    
    if request.method == 'POST':
        # Ayarları güncelle
        printify_settings.api_token = request.POST.get('api_token', '')
        printify_settings.shop_id = request.POST.get('shop_id', '')
        printify_settings.use_sandbox = request.POST.get('use_sandbox') == 'on'
        printify_settings.default_profit_margin = request.POST.get('default_profit_margin', '30.00')
        printify_settings.auto_update_prices = request.POST.get('auto_update_prices') == 'on'
        printify_settings.usd_to_try_rate = request.POST.get('usd_to_try_rate', '34.50')
        printify_settings.auto_import_products = request.POST.get('auto_import_products') == 'on'
        printify_settings.auto_publish_products = request.POST.get('auto_publish_products') == 'on'
        printify_settings.auto_submit_orders = request.POST.get('auto_submit_orders') == 'on'
        printify_settings.order_status_for_auto_submit = request.POST.get('order_status_for_auto_submit', 'confirmed')
        printify_settings.webhook_url = request.POST.get('webhook_url', '')
        printify_settings.webhook_secret = request.POST.get('webhook_secret', '')
        printify_settings.sync_interval_hours = request.POST.get('sync_interval_hours', 24)
        printify_settings.notify_on_sync_complete = request.POST.get('notify_on_sync_complete') == 'on'
        printify_settings.notify_on_sync_error = request.POST.get('notify_on_sync_error') == 'on'
        printify_settings.notification_email = request.POST.get('notification_email', '')
        
        default_category_id = request.POST.get('default_category')
        if default_category_id:
            printify_settings.default_category_id = default_category_id
        
        printify_settings.save()
        
        messages.success(request, 'Printify ayarları kaydedildi.')
        return redirect('shop:admin_printify_settings')
    
    context = {
        'printify_settings': printify_settings,
        'categories': categories,
    }
    
    return render(request, 'shop/custom_admin/printify/settings.html', context)


@staff_member_required
def admin_printify_sync(request):
    """Printify Senkronizasyon"""
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'sync_products':
            try:
                category_id = request.POST.get('category_id')
                limit = int(request.POST.get('limit', 50))
                
                service = PrintifyService()
                sync_log = service.sync_products_from_printify(
                    category_id=category_id if category_id else None,
                    limit=limit
                )
                
                if sync_log.status == 'completed':
                    messages.success(
                        request,
                        f'Printify senkronizasyonu tamamlandı! '
                        f'{sync_log.successful_items} ürün başarıyla senkronize edildi.'
                    )
                else:
                    messages.error(
                        request,
                        f'Printify senkronizasyonu başarısız: {sync_log.error_message}'
                    )
                    
            except Exception as e:
                messages.error(request, f'Senkronizasyon hatası: {str(e)}')
        
        elif action == 'test_connection':
            try:
                service = PrintifyService()
                if service.api.test_connection():
                    messages.success(request, 'Printify API bağlantısı başarılı!')
                else:
                    messages.error(request, 'Printify API bağlantısı başarısız!')
            except Exception as e:
                messages.error(request, f'Bağlantı test hatası: {str(e)}')
        
        return redirect('shop:admin_printify_sync')
    
    # Son senkronizasyon logları
    sync_logs = PrintifySyncLog.objects.all()[:20]
    categories = Category.objects.filter(enable_printify_sync=True)
    
    # Printify ürün sayıları
    printify_products_count = Product.objects.filter(source='printify').count()
    
    context = {
        'sync_logs': sync_logs,
        'categories': categories,
        'printify_products_count': printify_products_count,
    }
    
    return render(request, 'shop/custom_admin/printify/sync.html', context)
