# EPROLO Kategori Bazlı Senkronizasyon Sistemi

## 📋 Genel Bakış

Sisteminiz artık **kategori bazlı EPROLO entegrasyonu** destekliyor. Her kategori için ayrı ayrı EPROLO ürünlerini senkronize edebilirsiniz.

## 🎯 Nasıl Çalışır?

### 1. Kategori Ayarları

Her kategoride şu EPROLO ayarları var:

- **EPROLO Senkronizasyonu**: Bu kategoriye EPROLO ürünleri gelsin mi?
- **EPROLO Kategori ID/Adı**: EPROLO'daki hangi kategoriden ürünler çekilecek? (örn: "Electronics", "Fashion", "Home")
- **Ürünleri Otomatik Aktif Et**: Gelen ürünler otomatik aktif olsun mu yoksa manuel onay mı?
- **Özel Kar Marjı**: Bu kategori için özel kar marjı (opsiyonel)

### 2. Senkronizasyon Türleri

#### A) Tek Kategori Senkronizasyonu
```python
from shop.services import EproloService

service = EproloService()

# Kategori ID 1'deki ürünleri senkronize et
result = service.sync_products_by_category(category_id=1)

# Sonuç:
# {
#     'success': True,
#     'category': 'Elektronik',
#     'total': 50,
#     'success': 48,
#     'failed': 2,
#     'log_id': 123
# }
```

#### B) Tüm Kategorileri Senkronize Et
```python
# Sadece EPROLO senkronizasyonu aktif kategorileri işle
result = service.sync_all_categories()

# Sonuç:
# {
#     'total_categories': 3,
#     'categories': [
#         {'category': 'Elektronik', 'total': 50, 'success': 48, 'failed': 2},
#         {'category': 'Giyim', 'total': 30, 'success': 30, 'failed': 0},
#         {'category': 'Ev Eşyaları', 'total': 20, 'success': 19, 'failed': 1}
#     ],
#     'total_products': 100,
#     'total_success': 97,
#     'total_failed': 3
# }
```

#### C) Kategori Bazlı Stok Güncelleme
```python
# Sadece belirli bir kategorideki ürünlerin stoklarını güncelle
result = service.update_stock_by_category(category_id=1)
```

#### D) Kategori Bazlı Fiyat Güncelleme
```python
# Kategorideki tüm ürünlerin fiyatlarını yeni kar marjı ile güncelle
result = service.update_prices_by_category(
    category_id=1,
    new_margin=35  # %35 kar marjı
)
```

### 3. Kategori Durum Kontrolü
```python
# Kategorinin senkronizasyon durumunu öğren
status = service.get_category_sync_status(category_id=1)

# Sonuç:
# {
#     'category': 'Elektronik',
#     'total_products': 48,
#     'active_products': 45,
#     'total_stock': 1250,
#     'low_stock_count': 5,
#     'last_sync': datetime(...),
#     'recent_logs': [...]
# }
```

## 💡 Senaryolar

### Senaryo 1: Farklı Tedarikçilerden Ürünler

```
Kategoriler:
├── Elektronik
│   ├── EPROLO Kategori: "Electronics"
│   ├── Kar Marjı: %30
│   └── Otomatik Aktif: Hayır (manuel kontrol)
│
├── Giyim
│   ├── EPROLO Kategori: "Fashion"
│   ├── Kar Marjı: %40
│   └── Otomatik Aktif: Evet
│
└── El Yapımı (EPROLO YOK)
    ├── Manuel ürünler
    └── EPROLO Senkronizasyonu: Kapalı
```

### Senaryo 2: Aynı Üründen Farklı Kategorilere

EPROLO'da bir ürün birden fazla kategoride olabilir. Siz hangi kategoriye eklemek istediğinize karar verirsiniz:

```python
# Elektronik kategorisine senkronize et
service.sync_products_by_category(category_id=1)  # Elektronik

# Aynı EPROLO ürünü farklı kategoriye de eklenebilir
# (farklı fiyat/marj ile)
```

## 🎨 Admin Panel Kullanımı

### 1. Kategori Ayarlarını Yapın

Django Admin'den kategori düzenleyin:
```
http://127.0.0.1:8000/admin/shop/category/1/change/

✅ EPROLO Senkronizasyonu: Aktif
📝 EPROLO Kategori Adı: Electronics
✅ Ürünleri Otomatik Aktif Et: Kapalı
💰 Özel Kar Marjı %: 35.00
```

### 2. Custom Admin'den Senkronize Edin

```
http://127.0.0.1:8000/shop/manage/eprolo/

1. "Kategori Senkronizasyonu" butonuna tıklayın
2. Senkronize edilecek kategoriyi seçin
3. "Senkronize Et" butonuna basın
```

### 3. Sonuçları İnceleyin

Senkronizasyon logları otomatik kaydedilir:
- Hangi kategoriden kaç ürün çekildi
- Kaç tanesi başarılı
- Hangi ürünlerde hata var
- Toplam süre

## 📊 Örnek İş Akışı

### Yeni Mağaza Kurulumu

```bash
1. Kategorileri Oluştur
   ├── Elektronik
   ├── Giyim
   └── Aksesuar

2. Her Kategori İçin EPROLO Ayarlarını Yap
   ├── EPROLO kategori adını gir
   ├── Kar marjını belirle
   └── Otomatik aktif etme durumunu seç

3. İlk Senkronizasyonu Çalıştır
   └── service.sync_all_categories()

4. Gelen Ürünleri İncele
   ├── Manuel onay gerekliyse aktif et
   ├── Fiyatları kontrol et
   └── Açıklamaları düzenle

5. Stok ve Fiyat Güncellemelerini Otomatikleştir
   ├── Günlük stok senkronizasyonu
   └── Haftalık fiyat güncellemesi
```

## 🔄 Otomatik Senkronizasyon

Django Management Command ile cron job kurabilirsiniz:

```bash
# Her gün saat 03:00'te tüm kategorileri senkronize et
0 3 * * * cd /home/django/horoscope && python manage.py sync_eprolo_categories

# Her saat başı stokları güncelle
0 * * * * cd /home/django/horoscope && python manage.py sync_eprolo_stock
```

## 🛡️ Güvenlik ve Kontrol

### Önlemler:

1. **Manuel Onay**: Ürünler pasif gelir, siz aktif edersiniz
2. **Log Takibi**: Her işlem kaydedilir
3. **Hata Yönetimi**: Hatalı senkronlar tekrar denenebilir
4. **Kar Marjı Kontrolü**: Her kategori için ayrı marj
5. **Stok Eşikleri**: Düşük stok uyarıları

### İzleme:

```python
# Son senkronizasyon loglarını görüntüle
from shop.models import EproloSyncLog

logs = EproloSyncLog.objects.filter(
    sync_type='product'
).order_by('-started_at')[:10]

for log in logs:
    print(f"{log.started_at}: {log.details}")
    print(f"Başarı oranı: %{log.success_rate}")
```

## 💾 Veri Yapısı

### Category Model
```python
class Category(models.Model):
    name = models.CharField(max_length=100)
    enable_eprolo_sync = models.BooleanField(default=False)
    eprolo_category_id = models.CharField(max_length=100, blank=True)
    eprolo_category_name = models.CharField(max_length=200, blank=True)
    auto_activate_products = models.BooleanField(default=False)
    custom_profit_margin = models.DecimalField(max_digits=5, decimal_places=2, null=True)
```

### Product Model (EPROLO alanları)
```python
class Product(models.Model):
    source = models.CharField(max_length=20, choices=[('manual', 'Manuel'), ('eprolo', 'EPROLO')])
    eprolo_product_id = models.CharField(max_length=100, null=True)
    eprolo_sku = models.CharField(max_length=100, null=True)
    eprolo_supplier = models.CharField(max_length=200, null=True)
    eprolo_warehouse = models.CharField(max_length=100, null=True)
    eprolo_last_sync = models.DateTimeField(null=True)
    eprolo_data = models.JSONField(null=True)  # Ham EPROLO verisi
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    profit_margin = models.DecimalField(max_digits=5, decimal_places=2, default=30.00)
```

## 🚀 İleri Seviye Özellikler

### 1. Kategoriye Özel Filtreleme

```python
# Sadece belirli fiyat aralığındaki ürünleri çek
# (Custom implementation gerekli)
service.sync_products_by_category(
    category_id=1,
    filters={
        'min_price': 10.00,
        'max_price': 100.00,
        'min_rating': 4.0
    }
)
```

### 2. Toplu İşlemler

```python
# Tüm kategorilerdeki EPROLO ürünlerinin fiyatlarını %10 artır
for category in Category.objects.filter(enable_eprolo_sync=True):
    products = category.products.filter(source='eprolo')
    for product in products:
        product.price = product.price * Decimal('1.10')
        product.save()
```

### 3. Raporlama

```python
# Kategori bazlı performans raporu
from django.db.models import Sum, Avg, Count

report = Category.objects.filter(
    enable_eprolo_sync=True
).annotate(
    total_products=Count('products', filter=Q(products__source='eprolo')),
    total_stock=Sum('products__stock', filter=Q(products__source='eprolo')),
    avg_price=Avg('products__price', filter=Q(products__source='eprolo')),
    total_sales=Sum('products__sales_count', filter=Q(products__source='eprolo'))
)
```

## 📞 Destek

Sorularınız için:
- GitHub Issues
- E-posta: support@yourstore.com
- Dokümantasyon: /docs/eprolo/

## 🎉 Özet

✅ Her kategori için ayrı EPROLO senkronizasyonu
✅ Kategori bazlı kar marjı ayarlama
✅ Manuel/otomatik ürün aktivasyonu
✅ Detaylı log ve raporlama
✅ Stok ve fiyat güncelleme
✅ Hata yönetimi ve retry mekanizması

Artık mağazanızda **farklı tedarikçilerden farklı kategorilere** ürün ekleyebilirsiniz! 🚀
