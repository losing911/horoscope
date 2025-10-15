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
    list_display = ['name', 'category', 'price', 'stock', 'stock_status', 'is_featured', 'is_active', 'sales_count', 'views']
    list_filter = ['category', 'stock_status', 'is_featured', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'zodiac_signs']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['views', 'sales_count', 'discount_percentage', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('category', 'name', 'slug', 'description', 'short_description')
        }),
        ('Fiyat ve Stok', {
            'fields': ('price', 'original_price', 'discount_percentage', 'stock', 'stock_status')
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
            'fields': ('views', 'sales_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


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
    list_display = ['order_number', 'user', 'full_name', 'status', 'total', 'payment_method', 'is_paid', 'created_at']
    list_filter = ['status', 'payment_method', 'is_paid', 'created_at']
    search_fields = ['order_number', 'user__username', 'full_name', 'email', 'phone']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    
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
            'fields': ('payment_method', 'is_paid', 'paid_at')
        }),
        ('Notlar', {
            'fields': ('notes', 'admin_notes')
        }),
        ('Tarihler', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
