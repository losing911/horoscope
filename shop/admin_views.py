from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum, Count, Q, F, Avg
from django.utils import timezone
from datetime import timedelta
from .models import Order, OrderItem, Product, Category, Cart, CartItem


@staff_member_required
def shop_dashboard(request):
    """Mağaza ana dashboard - İstatistikler ve özet bilgiler"""
    
    # Bugün ve bu ay filtreleri
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    
    # Sipariş istatistikleri
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    completed_orders = Order.objects.filter(status='completed').count()
    cancelled_orders = Order.objects.filter(status='cancelled').count()
    
    # Bu ay siparişleri
    this_month_orders = Order.objects.filter(created_at__gte=this_month_start).count()
    last_month_orders = Order.objects.filter(
        created_at__gte=last_month_start,
        created_at__lt=this_month_start
    ).count()
    
    # Gelir istatistikleri
    total_revenue = Order.objects.filter(
        status__in=['completed', 'shipped']
    ).aggregate(total=Sum('total'))['total'] or 0
    
    this_month_revenue = Order.objects.filter(
        created_at__gte=this_month_start,
        status__in=['completed', 'shipped']
    ).aggregate(total=Sum('total'))['total'] or 0
    
    last_month_revenue = Order.objects.filter(
        created_at__gte=last_month_start,
        created_at__lt=this_month_start,
        status__in=['completed', 'shipped']
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Ürün istatistikleri
    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()
    low_stock_products = Product.objects.filter(stock__lte=F('stock') * 0.2, stock__gt=0).count()
    out_of_stock = Product.objects.filter(stock=0).count()
    
    # En çok satan ürünler (son 30 gün)
    thirty_days_ago = today - timedelta(days=30)
    top_products = OrderItem.objects.filter(
        order__created_at__gte=thirty_days_ago,
        order__status__in=['completed', 'shipped']
    ).values('product__name', 'product__id').annotate(
        total_sold=Sum('quantity'),
        revenue=Sum(F('quantity') * F('product_price'))
    ).order_by('-total_sold')[:5]
    
    # Son siparişler
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
    
    # Kategori bazlı satışlar
    category_sales = OrderItem.objects.filter(
        order__status__in=['completed', 'shipped']
    ).values('product__category__name').annotate(
        total_sold=Sum('quantity'),
        revenue=Sum(F('quantity') * F('product_price'))
    ).order_by('-revenue')[:5]
    
    # Aktif sepetler
    active_carts = Cart.objects.filter(
        items__isnull=False
    ).distinct().count()
    
    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'cancelled_orders': cancelled_orders,
        'this_month_orders': this_month_orders,
        'last_month_orders': last_month_orders,
        'total_revenue': total_revenue,
        'this_month_revenue': this_month_revenue,
        'last_month_revenue': last_month_revenue,
        'total_products': total_products,
        'active_products': active_products,
        'low_stock_products': low_stock_products,
        'out_of_stock': out_of_stock,
        'top_products': top_products,
        'recent_orders': recent_orders,
        'category_sales': category_sales,
        'active_carts': active_carts,
    }
    
    return render(request, 'shop/admin/dashboard.html', context)


@staff_member_required
def order_management(request):
    """Sipariş yönetimi - Tüm siparişleri listele ve filtrele"""
    
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('q', '')
    
    orders = Order.objects.select_related('user').prefetch_related('items__product')
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if search_query:
        orders = orders.filter(
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(shipping_address__icontains=search_query)
        )
    
    orders = orders.order_by('-created_at')
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': Order.STATUS_CHOICES,
    }
    
    return render(request, 'shop/admin/order_management.html', context)


@staff_member_required
def order_detail_admin(request, order_id):
    """Sipariş detayı ve durum güncelleme"""
    
    order = get_object_or_404(
        Order.objects.select_related('user').prefetch_related('items__product'),
        id=order_id
    )
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Sipariş durumu "{order.get_status_display()}" olarak güncellendi.')
            return redirect('shop:order_detail_admin', order_id=order.id)
    
    context = {
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
    }
    
    return render(request, 'shop/admin/order_detail.html', context)


@staff_member_required
def product_management(request):
    """Ürün yönetimi - Ürünleri listele, stok kontrolü"""
    
    category_filter = request.GET.get('category', '')
    stock_filter = request.GET.get('stock', '')
    search_query = request.GET.get('q', '')
    
    products = Product.objects.select_related('category')
    
    if category_filter:
        products = products.filter(category_id=category_filter)
    
    if stock_filter == 'low':
        products = products.filter(stock__lte=F('stock') * 0.2, stock__gt=0)
    elif stock_filter == 'out':
        products = products.filter(stock=0)
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    products = products.order_by('-created_at')
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'category_filter': category_filter,
        'stock_filter': stock_filter,
        'search_query': search_query,
    }
    
    return render(request, 'shop/admin/product_management.html', context)


@staff_member_required
def update_product_stock(request, product_id):
    """Ürün stoğu güncelleme"""
    
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        new_stock = request.POST.get('stock')
        
        try:
            new_stock = int(new_stock)
            if new_stock < 0:
                messages.error(request, 'Stok miktarı negatif olamaz.')
            else:
                product.stock = new_stock
                product.save()
                messages.success(request, f'{product.name} ürününün stoğu {new_stock} olarak güncellendi.')
        except ValueError:
            messages.error(request, 'Geçerli bir stok miktarı giriniz.')
    
    return redirect('shop:product_management')


@staff_member_required
def sales_statistics(request):
    """Satış istatistikleri ve raporlar"""
    
    # Tarih aralığı filtreleri
    period = request.GET.get('period', '30days')
    
    today = timezone.now().date()
    
    if period == '7days':
        start_date = today - timedelta(days=7)
    elif period == '30days':
        start_date = today - timedelta(days=30)
    elif period == '90days':
        start_date = today - timedelta(days=90)
    elif period == 'year':
        start_date = today - timedelta(days=365)
    else:
        start_date = today - timedelta(days=30)
    
    # Günlük satışlar
    daily_sales = Order.objects.filter(
        created_at__date__gte=start_date,
        status__in=['completed', 'shipped']
    ).extra(
        select={'day': 'DATE(created_at)'}
    ).values('day').annotate(
        orders=Count('id'),
        revenue=Sum('total')
    ).order_by('day')
    
    # Kategori bazlı satışlar
    category_stats = OrderItem.objects.filter(
        order__created_at__date__gte=start_date,
        order__status__in=['completed', 'shipped']
    ).values('product__category__name').annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum(F('quantity') * F('product_price')),
        order_count=Count('order', distinct=True)
    ).order_by('-total_revenue')
    
    # En çok satan ürünler
    top_selling_products = OrderItem.objects.filter(
        order__created_at__date__gte=start_date,
        order__status__in=['completed', 'shipped']
    ).values('product__name', 'product__id').annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum(F('quantity') * F('product_price')),
        order_count=Count('order', distinct=True)
    ).order_by('-total_quantity')[:10]
    
    # Toplam istatistikler
    total_stats = Order.objects.filter(
        created_at__date__gte=start_date,
        status__in=['completed', 'shipped']
    ).aggregate(
        total_orders=Count('id'),
        total_revenue=Sum('total'),
        avg_order_value=Avg('total')
    )
    
    context = {
        'period': period,
        'start_date': start_date,
        'daily_sales': list(daily_sales),
        'category_stats': category_stats,
        'top_selling_products': top_selling_products,
        'total_stats': total_stats,
    }
    
    return render(request, 'shop/admin/sales_statistics.html', context)


@staff_member_required
def customer_list(request):
    """Müşteri listesi ve sipariş geçmişi"""
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    customers = User.objects.annotate(
        order_count=Count('orders'),
        total_spent=Sum('orders__total', filter=Q(orders__status__in=['completed', 'shipped']))
    ).filter(order_count__gt=0).order_by('-total_spent')
    
    context = {
        'customers': customers,
    }
    
    return render(request, 'shop/admin/customer_list.html', context)
