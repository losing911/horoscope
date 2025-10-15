from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from decimal import Decimal
from .models import Product, Category, Cart, CartItem, Order, OrderItem


def product_list(request):
    """Tüm ürünler"""
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)
    
    # Kategori filtresi
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    # Arama
    search = request.GET.get('search')
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(zodiac_signs__icontains=search)
        )
    
    # Sıralama
    sort = request.GET.get('sort', '-created_at')
    if sort in ['price', '-price', 'name', '-name', '-created_at', '-sales_count']:
        products = products.order_by(sort)
    
    context = {
        'products': products,
        'categories': categories,
        'featured_products': Product.objects.filter(is_featured=True, is_active=True)[:4],
    }
    return render(request, 'shop/product_list.html', context)


def product_detail(request, slug):
    """Ürün detay sayfası"""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    
    # Görüntülenme sayısını artır
    product.views += 1
    product.save(update_fields=['views'])
    
    # İlgili ürünler
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'shop/product_detail.html', context)


def get_or_create_cart(request):
    """Kullanıcı veya session için sepet al/oluştur"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


def add_to_cart(request, product_id):
    """Sepete ürün ekle"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    if product.stock <= 0:
        messages.error(request, 'Bu ürün stokta yok.')
        return redirect('shop:product_detail', slug=product.slug)
    
    cart = get_or_create_cart(request)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f'{product.name} sepete eklendi.')
        else:
            messages.warning(request, 'Stok yetersiz.')
    else:
        messages.success(request, f'{product.name} sepete eklendi.')
    
    return redirect(request.META.get('HTTP_REFERER', 'shop:product_list'))


def update_cart_item(request, item_id):
    """Sepet ürün miktarını güncelle"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart = get_or_create_cart(request)
    
    if cart_item.cart != cart:
        messages.error(request, 'Bu işlemi yapmaya yetkiniz yok.')
        return redirect('shop:cart')
    
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        cart_item.delete()
        messages.success(request, 'Ürün sepetten kaldırıldı.')
    elif quantity <= cart_item.product.stock:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, 'Sepet güncellendi.')
    else:
        messages.error(request, 'Stok yetersiz.')
    
    return redirect('shop:cart')


def remove_from_cart(request, item_id):
    """Sepetten ürün çıkar"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart = get_or_create_cart(request)
    
    if cart_item.cart != cart:
        messages.error(request, 'Bu işlemi yapmaya yetkiniz yok.')
        return redirect('shop:cart')
    
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'{product_name} sepetten kaldırıldı.')
    
    return redirect('shop:cart')


def cart_view(request):
    """Sepet görünümü"""
    cart = get_or_create_cart(request)
    
    context = {
        'cart': cart,
        'cart_items': cart.items.select_related('product').all(),
    }
    return render(request, 'shop/cart.html', context)


@login_required
def checkout(request):
    """Ödeme sayfası"""
    cart = get_or_create_cart(request)
    
    if cart.items.count() == 0:
        messages.warning(request, 'Sepetiniz boş.')
        return redirect('shop:product_list')
    
    # GÜVENLİK: Sipariş öncesi stok kontrolü
    for item in cart.items.select_related('product').all():
        if item.quantity > item.product.stock:
            messages.error(request, f'{item.product.name} için yeterli stok yok. Maksimum {item.product.stock} adet alabilirsiniz.')
            return redirect('shop:cart')
        if not item.product.is_active:
            messages.error(request, f'{item.product.name} artık satışta değil.')
            item.delete()
            return redirect('shop:cart')
    
    if request.method == 'POST':
        # GÜVENLİK: Input validation
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        
        # Zorunlu alanlar kontrolü
        if not all([full_name, email, phone, address, city]):
            messages.error(request, 'Lütfen tüm zorunlu alanları doldurun.')
            return render(request, 'shop/checkout.html', {'cart': cart})
        
        # Uzunluk kontrolü
        if len(full_name) > 100 or len(email) > 100 or len(phone) > 20:
            messages.error(request, 'Girilen bilgiler çok uzun.')
            return render(request, 'shop/checkout.html', {'cart': cart})
        
        # GÜVENLİK: Transaction içinde sipariş oluştur (atomik işlem)
        from django.db import transaction
        
        try:
            with transaction.atomic():
                # Sipariş oluştur
                order = Order.objects.create(
                    user=request.user,
                    full_name=full_name,
                    email=email,
                    phone=phone,
                    address=address,
                    city=city,
                    postal_code=request.POST.get('postal_code', '').strip(),
                    subtotal=cart.subtotal,
                    shipping_cost=cart.shipping_cost,
                    total=cart.total,
                    payment_method=request.POST.get('payment_method', 'cash_on_delivery'),
                    notes=request.POST.get('notes', '').strip(),
                )
                
                # Sipariş ürünlerini oluştur ve stoktan düş
                for item in cart.items.all():
                    # GÜVENLİK: Son kez stok kontrolü
                    if item.quantity > item.product.stock:
                        raise ValueError(f'{item.product.name} için stok yetersiz.')
                    
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        product_name=item.product.name,
                        product_price=item.product.price,
                        quantity=item.quantity
                    )
                    
                    # Stok güncelle
                    item.product.stock -= item.quantity
                    item.product.sales_count += item.quantity
                    item.product.save()
                
                # Sepeti temizle
                cart.items.all().delete()
                
                messages.success(request, f'Siparişiniz alındı! Sipariş No: {order.order_number}')
                return redirect('shop:order_detail', order_number=order.order_number)
                
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('shop:cart')
        except Exception as e:
            messages.error(request, 'Sipariş oluşturulurken bir hata oluştu. Lütfen tekrar deneyin.')
            return redirect('shop:cart')
    
    context = {
        'cart': cart,
        'cart_items': cart.items.select_related('product').all(),
    }
    return render(request, 'shop/checkout.html', context)


@login_required
def order_list(request):
    """Kullanıcının siparişleri"""
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    
    context = {
        'orders': orders,
    }
    return render(request, 'shop/order_list.html', context)


@login_required
def order_detail(request, order_number):
    """Sipariş detayı"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    context = {
        'order': order,
    }
    return render(request, 'shop/order_detail.html', context)
