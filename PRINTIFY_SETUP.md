# 🖨️ Printify Print-on-Demand Entegrasyonu Belgesi

**Son Güncelleme:** 27 Ekim 2025

## 📋 İçindekiler

1. [Genel Bakış](#genel-bakış)
2. [Kurulum](#kurulum)
3. [Kullanım](#kullanım)
4. [Ayarlar](#ayarlar)
5. [Senkronizasyon](#senkronizasyon)
6. [Hata Giderme](#hata-giderme)
7. [API Referansı](#api-referansı)

## 🎯 Genel Bakış

Printify entegrasyonu, Django e-ticaret sistemine **print-on-demand (POD)** yetenekleri ekler. Bu sistemle:

- 📦 Printify kataloğundan ürünleri otomatik al
- 💰 Fiyatları USD'den TL'ye dönüştür
- 🎨 Tişört, poster, telefon kılıfı vb. özel ürünler ekle
- 📊 Senkronizasyon geçmişini takip et
- 🤖 Siparişleri otomatik gönder
- 🔔 Webhook ile güncellemeleri al

## 🚀 Kurulum

### Adım 1: Database Migrasyonları

```bash
python manage.py migrate shop
```

Bu komut şunları oluşturur:
- `PrintifySettings` modeli
- `PrintifySyncLog` modeli
- Product modeline Printify alanları
- Category modeline Printify ayarları

### Adım 2: Printify API Credentials

Printify'dan API Token ve Shop ID alın:

1. https://printify.com adresine git
2. Hesabına giriş yap
3. Settings → Apps & API
4. Yeni app oluştur veya mevcut olanı seç
5. API Token'ı kopyala
6. Shop ID'sini not et

### Adım 3: Settings Oluştur

Django Admin'de (`/admin/shop/printifysettings/`):

```
✓ API Token: [Token'ınızı yapıştırın]
✓ Shop ID: [Shop ID'nizi yapıştırın]
✓ Sandbox Modu: ☐ (Devre dışı = Canlı)
✓ USD/TL Kuru: 34.50
✓ Varsayılan Kar Marjı: 30.00
```

### Adım 4: Test Etme

```bash
python manage.py sync_printify_products --test-connection
```

Output:
```
Printify API bağlantısı test ediliyor...
✓ Printify API bağlantısı başarılı!
```

## 💻 Kullanım

### Custom Admin Panel

Admin panelinin Printify bölümünü kullan: `/shop/manage/printify/`

**Dashboard:**
- Ürün sayıları
- Senkronizasyon istatistikleri
- Hızlı aksiyonlar

**Ayarlar:**
- API yapılandırması
- Fiyatlandırma
- Otomasyonlar
- Bildirimler

**Senkronizasyon:**
- Ürün içe aktar
- API test et
- Log geçmişi

### Management Command

Terminal'den senkronizasyon yapın:

```bash
# Temel senkronizasyon
python manage.py sync_printify_products

# Kategori belirt
python manage.py sync_printify_products --category-id=1

# Limit ayarla
python manage.py sync_printify_products --limit=100

# Sadece test et
python manage.py sync_printify_products --test-connection
```

## 📊 Ayarlar

### Printify Settings Alanları

| Alan | Tür | Açıklama |
|------|-----|----------|
| `api_token` | String | Printify API token |
| `shop_id` | String | Printify mağaza ID |
| `use_sandbox` | Boolean | Sandbox modu (test) |
| `default_profit_margin` | Decimal | Kar marjı (%) |
| `auto_update_prices` | Boolean | Fiyatları otomatik güncelle |
| `usd_to_try_rate` | Decimal | USD/TL kuru |
| `auto_import_products` | Boolean | Ürünleri otomatik içe al |
| `auto_publish_products` | Boolean | Ürünleri otomatik yayınla |
| `auto_submit_orders` | Boolean | Siparişleri otomatik gönder |
| `order_status_for_auto_submit` | String | Hangi durumdaki siparişler gönderilsin |
| `sync_interval_hours` | Integer | Senkronizasyon aralığı (saat) |
| `notify_on_sync_complete` | Boolean | Tamamlama bildirimi gönder |
| `notify_on_sync_error` | Boolean | Hata bildirimi gönder |
| `notification_email` | Email | Bildirim alacak e-posta |
| `webhook_url` | URL | Webhook endpoint URL |
| `webhook_secret` | String | Webhook güvenlik anahtarı |

### Kategori Ayarları

Her kategori için Printify desteğini açabilirsiniz:

```python
category.enable_printify_sync = True          # Senkronizasyonu aç
category.printify_auto_activate = True        # Ürünleri otomatik aktif et
category.printify_profit_margin = 25.00       # Özel kar marjı
category.printify_category_mapping = {...}    # Kategori eşleştirmesi
```

## 🔄 Senkronizasyon

### Nasıl Çalışır?

1. **API Bağlantısı:** Printify API'sine bağlanır
2. **Ürünleri Al:** Shop'taki ürünleri listeler
3. **Fiyat Hesapla:** USD → TL dönüşümü
4. **Kar Marjı Ekle:** Satış fiyatını belirle
5. **İçe Aktar:** Database'e kaydet
6. **Log Kaydı:** Senkronizasyon sonuçlarını kaydet

### Fiyat Hesaplaması

```
Satış Fiyatı = (Printify Fiyatı USD × USD/TL Kuru × (1 + Kar Marjı%))
```

**Örnek:**
```
$25.00 × 34.50 × 1.30 = 1,121.25 TL
```

Kategoriye göre farklı kar marjı kullanılabilir.

### Log Kayıtları

Her senkronizasyonda kaydedilir:

- Tarih/Saat
- Senkronizasyon türü (ürün, stok, sipariş)
- Durum (tamamlandı, başarısız, devam ediyor)
- Toplam ürün sayısı
- Başarılı/Başarısız sayıları
- Başarı oranı
- İşlem süresi
- Hata mesajları (varsa)

Logları görüntüleyin: `/admin/shop/printifysynclog/`

## 📦 Ürün Model

Senkronize edilen ürünler şu alanları içerir:

```python
Product(
    source='printify',              # Kaynak
    name='Tişört',                  # Ürün adı
    description='...',               # Açıklama
    price=450.00,                    # Satış fiyatı TL
    price_usd=13.05,                 # Orijinal USD fiyat
    image='https://...',             # Ürün resmi
    stock_quantity=999,              # Sınırsız stok
    stock_status='in_stock',         # Durum
    
    # Printify Spesifik
    printify_product_id='123456',
    printify_shop_id='789',
    printify_variant_id='456',
    printify_blueprint_id='tshirt',
    printify_print_provider_id='12',
    printify_status='published',
    printify_last_sync=datetime.now(),
    printify_data={...},             # Ham JSON
)
```

## 🎯 Otomasyonlar

### Otomatik Ürün Import

Settings'de aktif edin:
```
auto_import_products = True
```

Bu sayede yeni ürünler otomatik alınır.

### Otomatik Yayınlama

```
auto_publish_products = True
```

İçe alınan ürünler otomatik olarak sitenizde yayınlanır.

### Otomatik Sipariş Gönderimi

```
auto_submit_orders = True
order_status_for_auto_submit = 'confirmed'
```

Onaylanan siparişler otomatik Printify'a gönderilir.

## 🔗 Webhooks

Printify'dan gerçek zamanlı bildirim almak için:

1. Webhook URL'sini Settings'e girin
2. Webhook Secret'ı girin
3. Printify Dashboard'ta webhook'u etkinleştir

Webhook olayları:
- Ürün güncellemeleri
- Sipariş durumu değişiklikleri
- Ödeme bildirileri
- Kargo tracking

## 🐛 Hata Giderme

### API Bağlantı Hatası

**Problem:** "API bağlantısı başarısız"

**Çözüm:**
1. API Token'ı doğrula
2. Shop ID'sini doğrula
3. Sandbox modu kontrol et
4. Firewall ayarlarını kontrol et

```bash
# Test et
python manage.py sync_printify_products --test-connection
```

### Fiyatlar Hatalı

**Problem:** Fiyatlar yanlış hesaplanıyor

**Çözüm:**
1. USD/TL kurunu güncelle: `34.50` gibi
2. Kar marjını kontrol et: `30.00` gibi
3. Ürün fiyatını manuel düzenle

### Senkronizasyon Başarısız

**Problem:** "Senkronizasyon başarısız oldu"

**Çözüm:**
1. Admin panel'de hata mesajını oku
2. Log kayıtlarında detayları kontrol et
3. API Rate Limit'ini kontrol et
4. Network bağlantısını kontrol et

### Hiçbir Ürün İçe Almadı

**Problem:** Senkronizasyon başarılı ama ürün yok

**Çözüm:**
1. Printify'da ürün olduğunu doğrula
2. Kategori seçimini kontrol et
3. `printify_auto_activate` ayarını kontrol et
4. Admin panel'den ürünleri kontrol et

## 🔌 API Referansı

### PrintifyAPI Sınıfı

```python
from shop.printify_service import PrintifyAPI

api = PrintifyAPI()

# Test connection
api.test_connection()  # Returns: bool

# Get shops
shops = api.get_shops()  # Returns: list

# Get products
products = api.get_shop_products(shop_id='123')
# Returns: {data: [...], pagination: {...}}

# Get single product
product = api.get_product_details(shop_id='123', product_id='456')

# Create product
new_product = api.create_product(shop_id='123', product_data={...})

# Update product
updated = api.update_product(shop_id='123', product_id='456', {...})

# Publish product
api.publish_product(shop_id='123', product_id='456')
```

### PrintifyService Sınıfı

```python
from shop.printify_service import PrintifyService

service = PrintifyService()

# Sync products
sync_log = service.sync_products_from_printify(
    category_id=1,  # Optional
    limit=50
)

# Check result
if sync_log.status == 'completed':
    print(f"Başarılı: {sync_log.successful_items}")
    print(f"Başarısız: {sync_log.failed_items}")
    print(f"Başarı Oranı: {sync_log.success_rate}%")
```

## 📈 İstatistikler

### Senkronizasyon İstatistikleri

Dashboard'ta görüntüleyin:
- Toplam Printify ürünü sayısı
- Aktif ürün sayısı
- Son 30 gün senkronizasyon sayısı
- Ortalama başarı oranı

### Ürün İstatistikleri

Admin panel'de:
- Toplam ürün sayısı
- Kategori başına ürün
- Satış durumu
- Gelir hesaplamaları

## 📚 Kaynaklar

- [Printify API Dokümantasyonu](https://printify.com/api/)
- [Django Belgeleri](https://docs.djangoproject.com/)
- [Proje README](./README.md)

## 📞 İletişim

Sorular veya sorunlar için:
1. Log dosyalarını kontrol edin
2. Admin panel'deki hata mesajlarını okuyun
3. Printify destek forumuna bakın

---

**Versiyon:** 1.0  
**Tarih:** 27 Ekim 2025  
**Durum:** ✅ Üretim Hazır
