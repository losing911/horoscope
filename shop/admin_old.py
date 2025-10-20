from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'order', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'display_price', 'stock', 'stock_status', 'sales_count', 'display_revenue', 'is_active']
    list_filter = ['category', 'stock_status', 'is_featured', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'zodiac_signs']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['views', 'sales_count', 'discount_percentage', 'display_revenue', 'display_sales_quantity', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('category', 'name', 'slug', 'description', 'short_description')
        }),
        ('Fiyat ve Stok', {
            'fields': ('price_usd', 'usd_to_try_rate', 'price', 'original_price', 'discount_percentage', 'stock', 'stock_status'),
            'description': 'USD fiyat girerseniz otomatik olarak TL\'ye çevrilir. TL fiyat manuel de girebilirsiniz.'
        }),
        ('Görseller', {
            'fields': ('image', 'image_2', 'image_3')
        }),
        ('Özellikler', {
            'fields': ('features', 'zodiac_signs')
        }),
        ('SEO ve Durum', {
            'fields': ('meta_description', 'is_featured', 'is_active')
        }),
        ('İstatistikler', {
            'fields': ('views', 'sales_count', 'display_sales_quantity', 'display_revenue', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    @admin.display(description='Fiyat', ordering='price')
    def display_price(self, obj):
        from django.utils.html import format_html
        if obj.price_usd:
            return format_html(
                '<span title="USD: ${}">{} TL</span>',
                obj.price_usd,
                obj.price
            )
        return f'{obj.price} TL'
    
    @admin.display(description='Gelir', ordering='sales_count')
    def display_revenue(self, obj):
        from django.utils.html import format_html
        revenue = obj.total_revenue
        if revenue > 0:
            return format_html(
                '<span style="color: green; font-weight: bold;">{} TL</span>',
                revenue
            )
        return '0 TL'
    
    @admin.display(description='Satılan Adet')
    def display_sales_quantity(self, obj):
        quantity = obj.total_sales_quantity
        if quantity != obj.sales_count:
            return f'{quantity} adet (Kayıt: {obj.sales_count})'
        return f'{quantity} adet'


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['added_at']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'total_items', 'subtotal', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'session_key']
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'product_price', 'quantity']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'full_name', 'status', 'total', 'payment_method', 'payment_status_display', 'created_at']
    list_filter = ['status', 'payment_method', 'is_paid', 'created_at']
    search_fields = ['order_number', 'user__username', 'full_name', 'email', 'phone']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'payment_status_display']
    inlines = [OrderItemInline]
    actions = ['mark_as_paid', 'mark_as_confirmed', 'mark_as_preparing', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']
    
    def changelist_view(self, request, extra_context=None):
        """Sipariş listesi üstünde özet istatistikler göster"""
        from django.db.models import Sum, Count
        
        extra_context = extra_context or {}
        
        # Toplam gelir (sadece ödenenler)
        paid_orders = Order.objects.filter(is_paid=True)
        total_revenue = paid_orders.aggregate(Sum('total'))['total__sum'] or 0
        
        # İstatistikler
        stats = {
            'total_orders': Order.objects.count(),
            'paid_orders': paid_orders.count(),
            'pending_orders': Order.objects.filter(is_paid=False).count(),
            'total_revenue': total_revenue,
            'cod_pending': Order.objects.filter(payment_method='cash_on_delivery', is_paid=False).count(),
        }
        
        extra_context['revenue_stats'] = stats
        return super().changelist_view(request, extra_context=extra_context)
    
    fieldsets = (
        ('Sipariş Bilgileri', {
            'fields': ('order_number', 'user', 'status')
        }),
        ('Müşteri Bilgileri', {
            'fields': ('full_name', 'email', 'phone', 'address', 'city', 'postal_code')
        }),
        ('Fiyat Bilgileri', {
            'fields': ('subtotal', 'shipping_cost', 'total')
        }),
        ('Ödeme Bilgileri', {
            'fields': ('payment_method', 'is_paid', 'paid_at', 'payment_status_display'),
            'description': 'Kapıda ödeme siparişleri için "Ödendi" işaretlemesini teslim sonrası yapın.'
        }),
        ('Notlar', {
            'fields': ('notes', 'admin_notes')
        }),
        ('Tarihler', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    @admin.display(description='Ödeme Durumu')
    def payment_status_display(self, obj):
        """Ödeme durumunu renkli göster"""
        from django.utils.html import format_html
        
        if obj.payment_method == 'cash_on_delivery':
            if obj.is_paid:
                return format_html(
                    '<span style="color: green; font-weight: bold;">✓ Kapıda Ödeme Alındı</span>'
                )
            else:
                return format_html(
                    '<span style="color: orange; font-weight: bold;">⏳ Kapıda Ödeme (Ödeme Bekliyor)</span>'
                )
        elif obj.is_paid:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Ödendi</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Ödenmedi</span>'
            )
    
    # Admin Actions
    @admin.action(description='Seçili siparişleri ÖDENDİ olarak işaretle')
    def mark_as_paid(self, request, queryset):
        from django.utils import timezone
        updated = 0
        for order in queryset:
            if not order.is_paid:
                order.is_paid = True
                order.paid_at = timezone.now()
                order.save()
                updated += 1
        
        self.message_user(request, f'{updated} sipariş ödendi olarak işaretlendi.')
    
    @admin.action(description='Siparişi ONAYLANDI olarak işaretle')
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} sipariş onaylandı olarak işaretlendi.')
    
    @admin.action(description='Siparişi HAZIRLANIYOR olarak işaretle')
    def mark_as_preparing(self, request, queryset):
        updated = queryset.update(status='preparing')
        self.message_user(request, f'{updated} sipariş hazırlanıyor olarak işaretlendi.')
    
    @admin.action(description='Siparişi KARGOYA VERİLDİ olarak işaretle')
    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        self.message_user(request, f'{updated} sipariş kargoya verildi olarak işaretlendi.')
    
    @admin.action(description='Siparişi TESLİM EDİLDİ olarak işaretle')
    def mark_as_delivered(self, request, queryset):
        from django.utils import timezone
        updated = 0
        for order in queryset:
            order.status = 'delivered'
            # Kapıda ödeme ise ve henüz ödenmemişse otomatik ödendi yap
            if order.payment_method == 'cash_on_delivery' and not order.is_paid:
                order.is_paid = True
                order.paid_at = timezone.now()
            order.save()
            updated += 1
        
        self.message_user(request, f'{updated} sipariş teslim edildi olarak işaretlendi. Kapıda ödemeler otomatik ödendi yapıldı.')
    
    @admin.action(description='Siparişi İPTAL ET')
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} sipariş iptal edildi.')
