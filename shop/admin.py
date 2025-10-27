from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Avg
from .models import Category, Product, Cart, CartItem, Order, OrderItem, EproloSyncLog, EproloSettings, PrintifySyncLog, PrintifySettings


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'order', 'eprolo_sync_enabled', 'printify_sync_enabled', 'created_at']
    list_filter = ['is_active', 'enable_eprolo_sync', 'enable_printify_sync']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'slug', 'description', 'icon', 'image', 'is_active', 'order')
        }),
        ('🌐 EPROLO Entegrasyonu', {
            'fields': ('enable_eprolo_sync', 'eprolo_category_id', 'eprolo_category_name', 'auto_activate_products', 'custom_profit_margin'),
            'classes': ('collapse',),
        }),
        ('🖨️ Printify Entegrasyonu', {
            'fields': ('enable_printify_sync', 'printify_category_mapping', 'printify_auto_activate', 'printify_profit_margin'),
            'classes': ('collapse',),
        }),
    )
    
    @admin.display(description='EPROLO Sync', boolean=True)
    def eprolo_sync_enabled(self, obj):
        return obj.enable_eprolo_sync
    
    @admin.display(description='Printify Sync', boolean=True)  
    def printify_sync_enabled(self, obj):
        return obj.enable_printify_sync


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['thumbnail', 'name', 'category', 'source_display', 'display_price', 'stock', 'stock_status', 'sales_count', 'display_revenue', 'eprolo_sync_status', 'is_active']
    list_filter = ['source', 'category', 'stock_status', 'is_featured', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'zodiac_signs', 'eprolo_product_id', 'eprolo_sku']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['views', 'sales_count', 'discount_percentage', 'display_revenue', 'display_sales_quantity', 'eprolo_last_sync', 'eprolo_sync_detail', 'printify_last_sync', 'created_at', 'updated_at']
    list_per_page = 50
    actions = ['mark_as_featured', 'mark_as_not_featured', 'update_from_eprolo']
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('category', 'name', 'slug', 'description', 'short_description', 'is_active')
        }),
        ('🌐 EPROLO Entegrasyonu', {
            'fields': ('source', 'eprolo_product_id', 'eprolo_variant_id', 'eprolo_sku', 'eprolo_supplier', 'eprolo_warehouse', 'eprolo_last_sync', 'eprolo_sync_detail'),
            'classes': ('collapse',),
            'description': 'EPROLO ile senkronize edilen ürünler için otomatik doldurulur.'
        }),
        ('🖨️ Printify Entegrasyonu', {
            'fields': ('printify_product_id', 'printify_shop_id', 'printify_variant_id', 'printify_blueprint_id', 'printify_print_provider_id', 'printify_status', 'printify_last_sync'),
            'classes': ('collapse',),
            'description': 'Printify ile senkronize edilen ürünler için otomatik doldurulur.'
        }),
        ('Fiyat ve Maliyet', {
            'fields': ('cost_price', 'profit_margin', 'price_usd', 'usd_to_try_rate', 'price', 'original_price', 'discount_percentage'),
            'description': 'Maliyet fiyatı ve kar marjı ile otomatik satış fiyatı hesaplanır. USD fiyat girerseniz otomatik TL\'ye çevrilir.'
        }),
        ('Stok', {
            'fields': ('stock', 'stock_status')
        }),
        ('Görseller', {
            'fields': ('image', 'image_2', 'image_3')
        }),
        ('Özellikler', {
            'fields': ('features', 'zodiac_signs', 'is_featured')
        }),
        ('SEO', {
            'fields': ('meta_description',),
            'classes': ('collapse',)
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
    
    @admin.display(description='Görsel')
    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />', obj.image)
        return '📦'
    
    @admin.display(description='Kaynak', ordering='source')
    def source_display(self, obj):
        if obj.source == 'eprolo':
            return format_html(
                '<span style="background: #e3f2fd; color: #1976d2; padding: 2px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">🌐 EPROLO</span>'
            )
        elif obj.source == 'printify':
            return format_html(
                '<span style="background: #f3e5f5; color: #7b1fa2; padding: 2px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">🖨️ PRINTIFY</span>'
            )
        return format_html(
            '<span style="background: #f5f5f5; color: #666; padding: 2px 8px; border-radius: 3px; font-size: 11px;">✏️ Manuel</span>'
        )
    
    @admin.display(description='EPROLO Senkronizasyon')
    def eprolo_sync_status(self, obj):
        if obj.source != 'eprolo':
            return '-'
        
        if not obj.eprolo_last_sync:
            return format_html('<span style="color: #999; font-size: 11px;">Henüz senkronize edilmedi</span>')
        
        # Son senkronizasyondan bu yana geçen süre
        from django.utils import timezone
        now = timezone.now()
        diff = now - obj.eprolo_last_sync
        
        if diff.days > 7:
            color = '#f44336'
            status = f'{diff.days} gün önce ⚠️'
        elif diff.days > 1:
            color = '#ff9800'
            status = f'{diff.days} gün önce'
        else:
            color = '#4caf50'
            status = 'Güncel ✓'
        
        return format_html(
            '<div style="color: {}; font-size: 11px; font-weight: bold;">{}</div>',
            color, status
        )
    
    @admin.display(description='EPROLO Detayı')
    def eprolo_sync_detail(self, obj):
        if obj.source != 'eprolo':
            return 'Bu ürün manuel eklenmiştir.'
        
        parts = []
        parts.append(f'<div style="margin-bottom: 8px;"><strong>EPROLO Ürün ID:</strong> {obj.eprolo_product_id or "N/A"}</div>')
        parts.append(f'<div style="margin-bottom: 8px;"><strong>SKU:</strong> {obj.eprolo_sku or "N/A"}</div>')
        parts.append(f'<div style="margin-bottom: 8px;"><strong>Tedarikçi:</strong> {obj.eprolo_supplier or "N/A"}</div>')
        parts.append(f'<div style="margin-bottom: 8px;"><strong>Depo:</strong> {obj.eprolo_warehouse or "N/A"}</div>')
        
        if obj.eprolo_last_sync:
            parts.append(f'<div style="margin-bottom: 8px;"><strong>Son Senkronizasyon:</strong> {obj.eprolo_last_sync.strftime("%Y-%m-%d %H:%M:%S")}</div>')
        else:
            parts.append('<div style="margin-bottom: 8px;"><strong>Son Senkronizasyon:</strong> <span style="color: #f44336;">Henüz yapılmadı</span></div>')
        
        return format_html(''.join(parts))
    
    # Actions
    @admin.action(description='⭐ Öne Çıkan Olarak İşaretle')
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} ürün öne çıkan olarak işaretlendi.')
    
    @admin.action(description='Öne Çıkanlıktan Kaldır')
    def mark_as_not_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} ürün öne çıkanlıktan kaldırıldı.')
    
    @admin.action(description='🔄 EPROLO\'dan Güncelle')
    def update_from_eprolo(self, request, queryset):
        eprolo_products = queryset.filter(source='eprolo')
        count = eprolo_products.count()
        
        if count == 0:
            from django.contrib import messages
            self.message_user(request, 'Seçili ürünlerde EPROLO ürünü bulunamadı.', level=messages.WARNING)
            return
        
        # TODO: EPROLO API ile senkronizasyon
        from django.contrib import messages
        self.message_user(request, f'{count} EPROLO ürünü senkronize ediliyor... (Bu özellik yakında aktif olacak)', level=messages.INFO)


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


@admin.register(EproloSyncLog)
class EproloSyncLogAdmin(admin.ModelAdmin):
    """EPROLO Senkronizasyon Logları Admin"""
    list_display = ['sync_type_badge', 'status_badge', 'stats_display', 'duration_display', 'user', 'started_at']
    list_filter = ['sync_type', 'status', 'started_at']
    search_fields = ['message', 'error_details']
    readonly_fields = ['sync_type', 'status', 'total_items', 'successful_items', 'failed_items', 'message', 'error_details', 'started_at', 'completed_at', 'duration_seconds', 'user', 'success_rate_display']
    filter_horizontal = ['affected_products']
    date_hierarchy = 'started_at'
    list_per_page = 50
    
    fieldsets = (
        ('Genel Bilgiler', {
            'fields': ('sync_type', 'status', 'user', 'started_at', 'completed_at', 'duration_seconds')
        }),
        ('İstatistikler', {
            'fields': ('total_items', 'successful_items', 'failed_items', 'success_rate_display')
        }),
        ('Detaylar', {
            'fields': ('message', 'error_details'),
            'classes': ('collapse',)
        }),
        ('Etkilenen Ürünler', {
            'fields': ('affected_products',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    @admin.display(description='Senkronizasyon Tipi')
    def sync_type_badge(self, obj):
        colors = {
            'product_import': '#4caf50',
            'product_update': '#2196f3',
            'price_update': '#ff9800',
            'stock_update': '#9c27b0',
            'order_create': '#00bcd4',
            'order_update': '#3f51b5',
        }
        
        color = colors.get(obj.sync_type, '#999')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.get_sync_type_display()
        )
    
    @admin.display(description='Durum')
    def status_badge(self, obj):
        if obj.status == 'success':
            color = '#4caf50'
            icon = '✓'
        elif obj.status == 'failed':
            color = '#f44336'
            icon = '✗'
        else:
            color = '#ff9800'
            icon = '⚠'
        
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; border-radius: 3px; font-size: 11px; font-weight: bold;">{} {}</span>',
            color, icon, obj.get_status_display()
        )
    
    @admin.display(description='İstatistikler')
    def stats_display(self, obj):
        return format_html(
            '<div><strong>Toplam:</strong> {}</div>'
            '<div style="color: green;"><strong>Başarılı:</strong> {}</div>'
            '<div style="color: red;"><strong>Başarısız:</strong> {}</div>'
            '<div style="font-size: 11px; color: #999;">Başarı Oranı: %{}</div>',
            obj.total_items, obj.successful_items, obj.failed_items, obj.success_rate
        )
    
    @admin.display(description='Süre')
    def duration_display(self, obj):
        if obj.duration_seconds:
            return f'{obj.duration_seconds} saniye'
        return '-'
    
    @admin.display(description='Başarı Oranı')
    def success_rate_display(self, obj):
        rate = obj.success_rate
        if rate >= 90:
            color = '#4caf50'
        elif rate >= 70:
            color = '#ff9800'
        else:
            color = '#f44336'
        
        return format_html(
            '<span style="color: {}; font-weight: bold; font-size: 16px;">%{}</span>',
            color, rate
        )


@admin.register(EproloSettings)
class EproloSettingsAdmin(admin.ModelAdmin):
    """EPROLO Ayarları Admin (Singleton)"""
    
    fieldsets = (
        ('📡 API Bilgileri', {
            'fields': ('api_key', 'api_secret', 'use_mock'),
            'description': '🔑 EPROLO API bağlantı ayarları. Test için Mock modu kullanabilirsiniz.'
        }),
        ('💰 Fiyatlandırma Ayarları', {
            'fields': ('usd_to_try_rate', 'default_profit_margin', 'auto_update_prices')
        }),
        ('📦 Stok Ayarları', {
            'fields': ('auto_update_stock', 'low_stock_threshold', 'out_of_stock_threshold')
        }),
        ('📋 Sipariş Ayarları', {
            'fields': ('auto_create_eprolo_orders', 'order_status_for_auto_send')
        }),
        ('🗂️ Kategori Ayarları', {
            'fields': ('default_category',)
        }),
        ('🔄 Senkronizasyon Bilgileri', {
            'fields': ('last_product_sync', 'last_stock_sync', 'last_price_sync'),
            'classes': ('collapse',)
        }),
        ('🔔 Bildirim Ayarları', {
            'fields': ('notify_on_sync_complete', 'notify_on_sync_error', 'notification_email'),
            'classes': ('collapse',)
        }),
        ('⏰ Tarihler', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['last_product_sync', 'last_stock_sync', 'last_price_sync', 'created_at', 'updated_at']
    
    def has_add_permission(self, request):
        # Singleton - sadece bir kayıt olabilir
        return not EproloSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PrintifySyncLog)
class PrintifySyncLogAdmin(admin.ModelAdmin):
    """Printify Senkronizasyon Logları Admin"""
    list_display = ['sync_type_badge', 'status_badge', 'stats_display', 'duration_display', 'started_at']
    list_filter = ['sync_type', 'status', 'started_at']
    search_fields = ['error_message']
    readonly_fields = ['sync_type', 'status', 'total_items', 'successful_items', 'failed_items', 'error_message', 'started_at', 'completed_at', 'duration_seconds', 'success_rate_display']
    date_hierarchy = 'started_at'
    list_per_page = 50
    
    fieldsets = (
        ('Genel Bilgiler', {
            'fields': ('sync_type', 'status', 'started_at', 'completed_at', 'duration_seconds')
        }),
        ('İstatistikler', {
            'fields': ('total_items', 'successful_items', 'failed_items', 'success_rate_display')
        }),
        ('Detaylar', {
            'fields': ('error_message', 'log_data'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    @admin.display(description='Senkronizasyon Tipi')
    def sync_type_badge(self, obj):
        colors = {
            'products': '#4caf50',
            'stock': '#ff9800', 
            'orders': '#2196f3',
            'webhooks': '#9c27b0',
        }
        
        color = colors.get(obj.sync_type, '#999')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; border-radius: 3px; font-size: 11px; font-weight: bold;">🖨️ {}</span>',
            color, obj.get_sync_type_display()
        )
    
    @admin.display(description='Durum')
    def status_badge(self, obj):
        if obj.status == 'completed':
            color = '#4caf50'
            icon = '✓'
        elif obj.status == 'failed':
            color = '#f44336'
            icon = '✗'
        elif obj.status == 'in_progress':
            color = '#2196f3'
            icon = '🔄'
        else:
            color = '#ff9800'
            icon = '⏳'
        
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; border-radius: 3px; font-size: 11px; font-weight: bold;">{} {}</span>',
            color, icon, obj.get_status_display()
        )
    
    @admin.display(description='İstatistikler')
    def stats_display(self, obj):
        return format_html(
            '<div><strong>Toplam:</strong> {}</div>'
            '<div style="color: green;"><strong>Başarılı:</strong> {}</div>'
            '<div style="color: red;"><strong>Başarısız:</strong> {}</div>'
            '<div style="font-size: 11px; color: #999;">Başarı Oranı: %{}</div>',
            obj.total_items, obj.successful_items, obj.failed_items, obj.success_rate
        )
    
    @admin.display(description='Süre')
    def duration_display(self, obj):
        if obj.duration_seconds:
            return f'{obj.duration_seconds} saniye'
        return '-'
    
    @admin.display(description='Başarı Oranı')
    def success_rate_display(self, obj):
        rate = obj.success_rate
        if rate >= 90:
            color = '#4caf50'
        elif rate >= 70:
            color = '#ff9800'
        else:
            color = '#f44336'
        
        return format_html(
            '<span style="color: {}; font-weight: bold; font-size: 16px;">%{}</span>',
            color, rate
        )


@admin.register(PrintifySettings)
class PrintifySettingsAdmin(admin.ModelAdmin):
    """Printify Ayarları Admin (Singleton)"""
    
    fieldsets = (
        ('🖨️ API Bilgileri', {
            'fields': ('api_token', 'shop_id', 'use_sandbox'),
            'description': '🔑 Printify API bağlantı ayarları. Test için sandbox modu kullanabilirsiniz.'
        }),
        ('💰 Fiyatlandırma Ayarları', {
            'fields': ('default_profit_margin', 'auto_update_prices', 'usd_to_try_rate')
        }),
        ('📦 Ürün Yönetimi', {
            'fields': ('auto_import_products', 'auto_publish_products', 'default_category')
        }),
        ('📋 Sipariş Ayarları', {
            'fields': ('auto_submit_orders', 'order_status_for_auto_submit')
        }),
        ('🔗 Webhook Ayarları', {
            'fields': ('webhook_url', 'webhook_secret'),
            'classes': ('collapse',)
        }),
        ('🔄 Senkronizasyon Bilgileri', {
            'fields': ('last_product_sync', 'last_order_sync', 'sync_interval_hours'),
            'classes': ('collapse',)
        }),
        ('🔔 Bildirim Ayarları', {
            'fields': ('notify_on_sync_complete', 'notify_on_sync_error', 'notification_email'),
            'classes': ('collapse',)
        }),
        ('⏰ Tarihler', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['last_product_sync', 'last_order_sync', 'created_at', 'updated_at']
    
    def has_add_permission(self, request):
        # Singleton - sadece bir kayıt olabilir
        return not PrintifySettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False
