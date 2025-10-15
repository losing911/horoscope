from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from decimal import Decimal

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


class Product(models.Model):
    """Ürünler"""
    STOCK_STATUS = [
        ('in_stock', 'Stokta'),
        ('low_stock', 'Stok Az'),
        ('out_of_stock', 'Stok Yok'),
        ('pre_order', 'Ön Sipariş'),
    ]
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='Kategori')
    name = models.CharField('Ürün Adı', max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField('Açıklama')
    short_description = models.CharField('Kısa Açıklama', max_length=250, blank=True)
    
    # Fiyat
    price = models.DecimalField('Fiyat', max_digits=10, decimal_places=2)
    original_price = models.DecimalField('İndirimli Fiyat', max_digits=10, decimal_places=2, blank=True, null=True)
    discount_percentage = models.IntegerField('İndirim %', default=0, blank=True)
    
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
