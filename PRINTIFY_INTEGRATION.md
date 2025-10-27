# Printify Entegrasyonu Kurulum Rehberi

## Genel Bakış

Bu proje artık **Printify** print-on-demand hizmeti ile entegre edilmiştir. Printify entegrasyonu ile:

- Print-on-demand ürünlerini otomatik olarak içe aktarabilirsiniz
- Sipariş yönetimini otomatik hale getirebilirsiniz  
- Geniş ürün kataloğu ve global üretim ağından faydalanabilirsiniz
- EPROLO ile birlikte çift dropshipping çözümü kullanabilirsiniz

## 🆕 Yeni Özellikler

### Printify Entegrasyonu
- ✅ **Ürün Senkronizasyonu**: Printify katalogından otomatik ürün çekme
- ✅ **Fiyat Yönetimi**: USD/TL kuru ile otomatik fiyat hesaplama
- ✅ **Stok Yönetimi**: Print-on-demand için sınırsız stok
- ✅ **Sipariş Entegrasyonu**: Otomatik sipariş iletimi
- ✅ **Admin Panel**: Modern web arayüzü ile kolay yönetim
- ✅ **Webhook Desteği**: Gerçek zamanlı senkronizasyon

### Yeni Database Modelleri
- `PrintifySettings`: API ayarları ve genel konfigürasyon
- `PrintifySyncLog`: Senkronizasyon logları ve hata takibi
- Ürün modelinde Printify-specific alanlar:
  - `printify_product_id`, `printify_shop_id`
  - `printify_variant_id`, `printify_blueprint_id`
  - `printify_print_provider_id`, `printify_status`
  - `printify_last_sync`, `printify_data`

### Yeni Management Commands
- `sync_printify_products`: Printify ürünlerini senkronize et
- `--test-connection`: API bağlantısını test et
- `--category-id`: Belirli kategoriye import
- `--limit`: Maksimum ürün sayısı

## 🚀 Kurulum

### 1. Migration Uygulama
```bash
python manage.py migrate
```

### 2. Printify API Ayarları
1. Admin panel > Printify Settings'e gidin
2. API Token'ınızı girin (Printify hesabınızdan alın)
3. Shop ID'nizi tanımlayın
4. Diğer ayarları yapılandırın

### 3. Kategori Ayarları
1. Admin panel > Categories'e gidin
2. İstediğiniz kategorilerde "Printify Senkronizasyonu" aktif edin
3. Printify kar marjını belirleyin

## 📖 Kullanım

### Ürün Senkronizasyonu
```bash
# Tüm ürünleri senkronize et
python manage.py sync_printify_products

# API bağlantısını test et
python manage.py sync_printify_products --test-connection

# Belirli kategoriye 20 ürün import et
python manage.py sync_printify_products --category-id=1 --limit=20
```

### Web Arayüzü
1. `/shop/manage/printify/` - Dashboard
2. `/shop/manage/printify/settings/` - Ayarlar
3. `/shop/manage/printify/sync/` - Senkronizasyon

## 🔧 Yapılandırma

### Fiyatlandırma
- **USD/TL Kuru**: Otomatik fiyat çevirimi
- **Kar Marjı**: Kategori bazında özelleştirilebilir
- **Otomatik Güncelleme**: Printify fiyat değişikliklerini takip

### Sipariş Yönetimi
- **Otomatik Gönderim**: Belirli sipariş durumunda otomatik Printify'a gönder
- **Durum Takibi**: Sipariş durumlarını senkronize et
- **Webhook**: Gerçek zamanlı güncellemeler

### Kategori Eşleştirme
- Printify kategorilerini site kategorilerinizle eşleştirin
- Kategori bazında otomatik aktifleştirme
- Özel kar marjı tanımlama

## 🎯 Best Practices

### 1. İlk Kurulum
1. ⚙️ Önce ayarları tamamlayın
2. 🔗 API bağlantısını test edin
3. 📁 Kategorileri hazırlayın
4. 🔄 Az miktarda ürün ile test edin

### 2. Ürün Yönetimi
- Print-on-demand ürünleri sınırsız stoklu olarak işaretlenir
- Ürün açıklamaları ve görseller Printify'dan gelir
- Fiyatlar otomatik hesaplanır (USD → TL + kar marjı)

### 3. Performans
- Senkronizasyonu zamanlanmış olarak çalıştırın
- Büyük kataloglar için batch'ler halinde import edin
- Log kayıtlarını düzenli kontrol edin

## 🛠️ Teknik Detaylar

### API Endpoints
- `GET /v1/shops/{shop_id}/products.json` - Ürün listesi
- `GET /v1/shops/{shop_id}/products/{product_id}.json` - Ürün detay
- `POST /v1/shops/{shop_id}/orders.json` - Sipariş oluştur

### Veri Yapısı
```python
# Printify ürün verisi
{
    "id": "5d39109de97ca1000f21f4a4",
    "title": "Awesome Print",
    "description": "Product description",
    "variants": [...],
    "images": [...],
    "blueprint_id": 384,
    "print_provider_id": 1
}
```

### Error Handling
- API hataları yakalanır ve loglanır
- Sync loglarında detaylı hata mesajları
- Başarısız ürünler için retry mekanizması

## 🔄 EPROLO vs Printify

| Özellik | EPROLO | Printify |
|---------|---------|----------|
| **Ürün Tipi** | Genel dropshipping | Print-on-demand |
| **Stok** | Gerçek stok | Sınırsız |
| **Üretim** | Hazır ürünler | Özel baskı |
| **Teslimat** | 7-15 gün | 2-7 gün |
| **Kar Marjı** | Yüksek | Orta |
| **Kalite** | Değişken | Yüksek |

## 🚨 Bilinen Limitler

1. **API Rate Limit**: Printify API dakika başına istek limiti var
2. **Sandbox Mode**: Test için kullanın, production'da kapatın
3. **Webhook**: SSL gerektirir, localhost'ta çalışmaz
4. **Batch Size**: Tek seferde max 100 ürün önerilir

## 🔮 Gelecek Özellikler

- [ ] Otomatik webhook kurulumu
- [ ] Printify Order tracking entegrasyonu
- [ ] Gelişmiş analitik raporlar
- [ ] Bulk ürün düzenleme
- [ ] Custom mockup generator

## 📞 Destek

Printify entegrasyonu ile ilgili sorularınız için:
1. 📋 Sync loglarını kontrol edin
2. 🔧 API ayarlarını doğrulayın
3. 🌐 Printify dökümantasyonunu inceleyin

---

**Not**: Bu entegrasyon EPROLO entegrasyonuna ek olarak çalışır. İki farklı ürün kaynağını aynı anda kullanabilirsiniz.