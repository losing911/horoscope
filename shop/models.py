from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils import timezone
from decimal import Decimal
import json

User = get_user_model()


class Category(models.Model):
    """Ürün kategorileri"""
    name = models.CharField('Kategori Adı', max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField('Açıklama', blank=True)
    icon = models.CharField('İkon (Font Awesome)', max_length=50, default='fa-shopping-bag', help_text='Örnek: fa-gem, fa-star, fa-ring')
    image = models.URLField('Resim URL', blank=True, null=True)
    is_active = models.BooleanField('Aktif', default=True)
    order = models.IntegerField('Sıralama', default=0)
    
    # EPROLO Entegrasyonu
    enable_eprolo_sync = models.BooleanField('EPROLO Senkronizasyonu', default=False, help_text='Bu kategoriye EPROLO ürünleri senkronize edilsin mi?')
    eprolo_category_id = models.CharField('EPROLO Kategori ID', max_length=100, blank=True, null=True, help_text='EPROLO\'daki kategori ID veya adı')
    eprolo_category_name = models.CharField('EPROLO Kategori Adı', max_length=200, blank=True, null=True, help_text='EPROLO\'daki kategori adı (örn: Electronics, Fashion, Home)')
    auto_activate_products = models.BooleanField('Ürünleri Otomatik Aktif Et', default=False, help_text='EPROLO\'dan gelen ürünler otomatik olarak aktif edilsin mi?')
    custom_profit_margin = models.DecimalField('Özel Kar Marjı %', max_digits=5, decimal_places=2, blank=True, null=True, help_text='Bu kategori için özel kar marjı (boş bırakılırsa genel ayar kullanılır)')
    
    created_at = models.DateTimeField('Oluşturulma', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Kategori'
        verbose_name_plural = 'Kategoriler'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)
    
    @property
    def eprolo_product_count(self):
        """Bu kategorideki EPROLO ürün sayısı"""
        return self.products.filter(source='eprolo').count()
    
    @property
    def total_stock_value(self):
        """Bu kategorideki toplam stok değeri"""
        from django.db.models import Sum, F
        result = self.products.filter(is_active=True).aggregate(
            total=Sum(F('stock') * F('price'))
        )
        return result['total'] or Decimal('0.00')


class Product(models.Model):
    """Ürünler"""
    STOCK_STATUS = [
        ('in_stock', 'Stokta'),
        ('low_stock', 'Stok Az'),
        ('out_of_stock', 'Stok Yok'),
        ('pre_order', 'Ön Sipariş'),
    ]
    
    SOURCE_CHOICES = [
        ('manual', 'Manuel Eklendi'),
        ('eprolo', 'EPROLO'),
    ]
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='Kategori')
    name = models.CharField('Ürün Adı', max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField('Açıklama')
    short_description = models.CharField('Kısa Açıklama', max_length=250, blank=True)
    
    # EPROLO Bilgileri
    source = models.CharField('Kaynak', max_length=20, choices=SOURCE_CHOICES, default='manual')
    eprolo_product_id = models.CharField('EPROLO Ürün ID', max_length=100, blank=True, null=True, db_index=True)
    eprolo_variant_id = models.CharField('EPROLO Varyant ID', max_length=100, blank=True, null=True)
    eprolo_sku = models.CharField('EPROLO SKU', max_length=100, blank=True, null=True)
    eprolo_supplier = models.CharField('EPROLO Tedarikçi', max_length=200, blank=True, null=True)
    eprolo_warehouse = models.CharField('EPROLO Depo', max_length=100, blank=True, null=True)
    eprolo_last_sync = models.DateTimeField('Son EPROLO Senkronizasyonu', blank=True, null=True)
    eprolo_data = models.JSONField('EPROLO Ham Veri', blank=True, null=True, help_text='EPROLO\'dan gelen ham JSON verisi')
    
    # Fiyat
    price = models.DecimalField('Fiyat (TL)', max_digits=10, decimal_places=2, help_text='USD fiyat girerseniz otomatik TL\'ye çevrilir')
    price_usd = models.DecimalField('Fiyat (USD)', max_digits=10, decimal_places=2, blank=True, null=True, help_text='Opsiyonel: USD fiyat')
    original_price = models.DecimalField('İndirimli Fiyat (TL)', max_digits=10, decimal_places=2, blank=True, null=True)
    discount_percentage = models.IntegerField('İndirim %', default=0, blank=True)
    usd_to_try_rate = models.DecimalField('USD/TL Kuru', max_digits=6, decimal_places=2, default=Decimal('34.00'), help_text='Kayıt sırasındaki kur')
    profit_margin = models.DecimalField('Kar Marjı %', max_digits=5, decimal_places=2, default=Decimal('30.00'), help_text='Satış fiyatına eklenecek kar oranı')
    cost_price = models.DecimalField('Maliyet Fiyatı (TL)', max_digits=10, decimal_places=2, blank=True, null=True, help_text='EPROLO\'dan gelen tedarikçi fiyatı')
    
    # Stok
    stock = models.IntegerField('Stok Miktarı', default=0)
    stock_status = models.CharField('Stok Durumu', max_length=20, choices=STOCK_STATUS, default='in_stock')
    
    # Görseller
    image = models.URLField('Ana Resim URL', blank=True, null=True)
    image_2 = models.URLField('Resim 2 URL', blank=True, null=True)
    image_3 = models.URLField('Resim 3 URL', blank=True, null=True)
    
    # Özellikler
    features = models.TextField('Özellikler (Her satıra bir özellik)', blank=True, help_text='Her satıra bir özellik yazın')
    zodiac_signs = models.CharField('Uygun Burçlar', max_length=200, blank=True, help_text='Örnek: Koç, Aslan, Yay')
    
    # SEO
    meta_description = models.CharField('Meta Açıklama', max_length=160, blank=True)
    
    # Durum
    is_featured = models.BooleanField('Öne Çıkan', default=False)
    is_active = models.BooleanField('Aktif', default=True)
    
    # İstatistikler
    views = models.IntegerField('Görüntülenme', default=0)
    sales_count = models.IntegerField('Satış Sayısı', default=0)
    
    created_at = models.DateTimeField('Oluşturulma', auto_now_add=True)
    updated_at = models.DateTimeField('Güncellenme', auto_now=True)
    
    class Meta:
        verbose_name = 'Ürün'
        verbose_name_plural = 'Ürünler'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        
        # USD/TL dönüşümü - eğer price_usd varsa TL'ye çevir
        if self.price_usd and self.price_usd > 0:
            self.price = self.price_usd * self.usd_to_try_rate
        
        # İndirim hesaplama
        if self.original_price and self.original_price > self.price:
            self.discount_percentage = int(((self.original_price - self.price) / self.original_price) * 100)
        
        # Stok durumu otomatik güncelleme
        if self.stock == 0:
            self.stock_status = 'out_of_stock'
        elif self.stock < 5:
            self.stock_status = 'low_stock'
        else:
            self.stock_status = 'in_stock'
        
        super().save(*args, **kwargs)
    
    @property
    def has_discount(self):
        return self.original_price and self.original_price > self.price
    
    @property
    def is_in_stock(self):
        return self.stock > 0
    
    @property
    def total_revenue(self):
        """Bu üründen elde edilen toplam gelir (sadece ödenmişler)"""
        from django.db.models import Sum
        revenue = self.orderitem_set.filter(
            order__is_paid=True
        ).aggregate(
            total=Sum('product_price')
        )['total']
        return revenue or Decimal('0.00')
    
    @property
    def total_sales_quantity(self):
        """Bu üründen satılan toplam adet (sadece ödenmişler)"""
        from django.db.models import Sum
        quantity = self.orderitem_set.filter(
            order__is_paid=True
        ).aggregate(
            total=Sum('quantity')
        )['total']
        return quantity or 0


class Cart(models.Model):
    """Alışveriş Sepeti"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts', verbose_name='Kullanıcı', null=True, blank=True)
    session_key = models.CharField('Oturum Anahtarı', max_length=100, blank=True, null=True)
    created_at = models.DateTimeField('Oluşturulma', auto_now_add=True)
    updated_at = models.DateTimeField('Güncellenme', auto_now=True)
    
    class Meta:
        verbose_name = 'Sepet'
        verbose_name_plural = 'Sepetler'
    
    def __str__(self):
        if self.user:
            return f"{self.user.username} - Sepet"
        return f"Anonim Sepet ({self.session_key})"
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())
    
    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())
    
    @property
    def shipping_cost(self):
        # 500 TL üzeri ücretsiz kargo
        if self.subtotal >= 500:
            return Decimal('0.00')
        return Decimal('50.00')
    
    @property
    def total(self):
        return self.subtotal + self.shipping_cost


class CartItem(models.Model):
    """Sepet Ürünleri"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name='Sepet')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Ürün')
    quantity = models.IntegerField('Adet', default=1)
    added_at = models.DateTimeField('Eklenme', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Sepet Ürünü'
        verbose_name_plural = 'Sepet Ürünleri'
        unique_together = ['cart', 'product']
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    @property
    def total_price(self):
        return self.product.price * self.quantity


class Order(models.Model):
    """Siparişler"""
    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('confirmed', 'Onaylandı'),
        ('preparing', 'Hazırlanıyor'),
        ('shipped', 'Kargoya Verildi'),
        ('delivered', 'Teslim Edildi'),
        ('cancelled', 'İptal Edildi'),
    ]
    
    PAYMENT_METHOD = [
        ('cash_on_delivery', 'Kapıda Ödeme'),
        ('credit_card', 'Kredi Kartı'),
        ('bank_transfer', 'Havale/EFT'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='Kullanıcı')
    order_number = models.CharField('Sipariş No', max_length=20, unique=True)
    status = models.CharField('Durum', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Adres Bilgileri
    full_name = models.CharField('Ad Soyad', max_length=200)
    email = models.EmailField('E-posta')
    phone = models.CharField('Telefon', max_length=20)
    address = models.TextField('Adres')
    city = models.CharField('Şehir', max_length=100)
    postal_code = models.CharField('Posta Kodu', max_length=10, blank=True)
    
    # Fiyat Bilgileri
    subtotal = models.DecimalField('Ara Toplam', max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField('Kargo Ücreti', max_digits=10, decimal_places=2, default=Decimal('50.00'))
    total = models.DecimalField('Toplam', max_digits=10, decimal_places=2)
    
    # Ödeme
    payment_method = models.CharField('Ödeme Yöntemi', max_length=20, choices=PAYMENT_METHOD, default='cash_on_delivery')
    is_paid = models.BooleanField('Ödendi', default=False)
    paid_at = models.DateTimeField('Ödeme Tarihi', blank=True, null=True)
    
    # Notlar
    notes = models.TextField('Sipariş Notu', blank=True)
    admin_notes = models.TextField('Admin Notu', blank=True)
    
    # Tarihler
    created_at = models.DateTimeField('Sipariş Tarihi', auto_now_add=True)
    updated_at = models.DateTimeField('Güncellenme', auto_now=True)
    
    class Meta:
        verbose_name = 'Sipariş'
        verbose_name_plural = 'Siparişler'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Sipariş #{self.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            import random
            import string
            self.order_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        
        # Ödeme durumu değişimi kontrolü
        if self.pk:  # Eğer güncelleme ise
            old_order = Order.objects.filter(pk=self.pk).first()
            if old_order and not old_order.is_paid and self.is_paid:
                # Ödeme yapıldı, satış sayılarını güncelle
                for item in self.items.all():
                    if item.product:
                        item.product.sales_count += item.quantity
                        item.product.save(update_fields=['sales_count'])
        
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """Sipariş Ürünleri"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Sipariş')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name='Ürün')
    product_name = models.CharField('Ürün Adı', max_length=200)
    product_price = models.DecimalField('Ürün Fiyatı', max_digits=10, decimal_places=2)
    quantity = models.IntegerField('Adet')
    
    class Meta:
        verbose_name = 'Sipariş Ürünü'
        verbose_name_plural = 'Sipariş Ürünleri'
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
    
    @property
    def total_price(self):
        return self.product_price * self.quantity


class EproloSyncLog(models.Model):
    """EPROLO Senkronizasyon Logları"""
    SYNC_TYPE_CHOICES = [
        ('product_import', 'Ürün İçe Aktarma'),
        ('product_update', 'Ürün Güncelleme'),
        ('price_update', 'Fiyat Güncelleme'),
        ('stock_update', 'Stok Güncelleme'),
        ('order_create', 'Sipariş Oluşturma'),
        ('order_update', 'Sipariş Güncelleme'),
    ]
    
    STATUS_CHOICES = [
        ('success', 'Başarılı'),
        ('failed', 'Başarısız'),
        ('partial', 'Kısmi Başarılı'),
    ]
    
    sync_type = models.CharField('Senkronizasyon Tipi', max_length=20, choices=SYNC_TYPE_CHOICES)
    status = models.CharField('Durum', max_length=20, choices=STATUS_CHOICES)
    
    # İstatistikler
    total_items = models.IntegerField('Toplam Öğe', default=0)
    successful_items = models.IntegerField('Başarılı Öğe', default=0)
    failed_items = models.IntegerField('Başarısız Öğe', default=0)
    
    # Detaylar
    message = models.TextField('Mesaj', blank=True)
    error_details = models.TextField('Hata Detayları', blank=True, null=True)
    sync_data = models.JSONField('Senkronizasyon Verisi', blank=True, null=True)
    
    # İlişkili kayıtlar
    affected_products = models.ManyToManyField(Product, blank=True, related_name='sync_logs', verbose_name='Etkilenen Ürünler')
    
    # Zaman
    started_at = models.DateTimeField('Başlangıç', auto_now_add=True)
    completed_at = models.DateTimeField('Tamamlanma', blank=True, null=True)
    duration_seconds = models.IntegerField('Süre (saniye)', blank=True, null=True)
    
    # Kullanıcı
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='İşlem Yapan')
    
    class Meta:
        verbose_name = 'EPROLO Senkronizasyon Logu'
        verbose_name_plural = 'EPROLO Senkronizasyon Logları'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.get_sync_type_display()} - {self.get_status_display()} ({self.started_at.strftime('%Y-%m-%d %H:%M')})"
    
    def save(self, *args, **kwargs):
        if self.completed_at and self.started_at:
            self.duration_seconds = int((self.completed_at - self.started_at).total_seconds())
        super().save(*args, **kwargs)
    
    @property
    def success_rate(self):
        """Başarı oranı"""
        if self.total_items > 0:
            return round((self.successful_items / self.total_items) * 100, 2)
        return 0


class EproloSettings(models.Model):
    """EPROLO Ayarları (Singleton model - tek kayıt)"""
    
    # API Bilgileri
    api_key = models.CharField('API Key', max_length=200, blank=True)
    api_secret = models.CharField('API Secret', max_length=200, blank=True)
    use_mock = models.BooleanField('Mock Modu Kullan', default=True, help_text='Test için mock veriler kullan')
    
    # Fiyatlandırma
    usd_to_try_rate = models.DecimalField('USD/TL Kuru', max_digits=6, decimal_places=2, default=Decimal('34.50'))
    default_profit_margin = models.DecimalField('Varsayılan Kar Marjı %', max_digits=5, decimal_places=2, default=Decimal('30.00'))
    auto_update_prices = models.BooleanField('Fiyatları Otomatik Güncelle', default=False)
    
    # Stok
    auto_update_stock = models.BooleanField('Stokları Otomatik Güncelle', default=False)
    low_stock_threshold = models.IntegerField('Düşük Stok Eşiği', default=5)
    out_of_stock_threshold = models.IntegerField('Stok Yok Eşiği', default=0)
    
    # Sipariş
    auto_create_eprolo_orders = models.BooleanField('EPROLO\'ya Otomatik Sipariş Gönder', default=False)
    order_status_for_auto_send = models.CharField('Otomatik Gönderim İçin Sipariş Durumu', max_length=20, default='confirmed', help_text='Bu duruma gelen siparişler otomatik EPROLO\'ya gönderilir')
    
    # Kategori
    default_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Varsayılan Kategori', help_text='EPROLO ürünleri için varsayılan kategori')
    
    # Senkronizasyon
    last_product_sync = models.DateTimeField('Son Ürün Senkronizasyonu', blank=True, null=True)
    last_stock_sync = models.DateTimeField('Son Stok Senkronizasyonu', blank=True, null=True)
    last_price_sync = models.DateTimeField('Son Fiyat Senkronizasyonu', blank=True, null=True)
    
    # Bildirimler
    notify_on_sync_complete = models.BooleanField('Senkronizasyon Tamamlandığında Bildir', default=True)
    notify_on_sync_error = models.BooleanField('Senkronizasyon Hatasında Bildir', default=True)
    notification_email = models.EmailField('Bildirim E-postası', blank=True)
    
    created_at = models.DateTimeField('Oluşturulma', auto_now_add=True)
    updated_at = models.DateTimeField('Güncellenme', auto_now=True)
    
    class Meta:
        verbose_name = 'EPROLO Ayarları'
        verbose_name_plural = 'EPROLO Ayarları'
    
    def __str__(self):
        return 'EPROLO Ayarları'
    
    def save(self, *args, **kwargs):
        # Singleton pattern - sadece bir kayıt olsun
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Ayarları getir (singleton)"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
