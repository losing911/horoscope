# 🌟 Tarot Yorum - Yeni Özellikler Kılavuzu

## 📋 Genel Bakış

Bu dokümantasyon, Tarot Yorum platformuna eklenen yeni özellikleri açıklar.

## ✨ Yeni Özellikler

### 1. 📱 Ana Sayfa Güncellemeleri

#### Günlük Burç Yorumları
- Ana sayfada 6 burcun günlük yorumlarının önizlemeleri gösteriliyor
- Her burç kartında:
  - Burç sembolü
  - Burç adı ve tarih aralığı
  - Günlük yorum özeti (ilk 20 kelime)
  - Aşk ve iş puanları
  - Detay sayfasına link
- "Tüm Burç Yorumları" butonu ile tam listeye erişim

#### Herkese Açık Tarot Okumaları
- Ana sayfada son 6 tarot okuması gösteriliyor
- Her okuma kartında:
  - Kullanıcı avatarı ve adı
  - Okuma tarihi (kaç zaman önce)
  - Yayılım adı
  - Soru özeti
  - Kart sayısı
  - Kullanılan AI provider
  - "Okumayı Gör" butonu

### 2. 🌙 Astroloji Modülü Geliştirmeleri

#### Yeni Modeller

**MoonSign (Ay Burcu)**
- Kullanıcı ay burcu hesaplaması
- Doğum tarihi, saati ve yeri ile hesaplama
- Enlem/boylam desteği
- AI destekli yorum

**Ascendant (Yükselen Burç)**
- Kullanıcı yükselen burcu hesaplaması
- Doğum saati ve konumu gerektirir
- AI destekli detaylı yorum

**PersonalHoroscope (Kişisel Burç Profili)**
- Güneş + Ay + Yükselen burç kombinasyonu
- Kullanıcıya özel tam burç profili
- OneToOne ilişkisi ile her kullanıcıya bir profil
- AI destekli genel yorum

#### Admin Paneli Güncellemeleri
- Tüm yeni modeller admin paneline eklendi
- Detaylı liste görünümleri
- Filtreleme ve arama özellikleri
- Fieldset'lerle organize edilmiş form yapısı

### 3. 🎨 Gemini 2.5 Flash Görsel Üretimi

#### ImageGenerationService Sınıfı
Yeni `ImageGenerationService` sınıfı `tarot/services.py` dosyasına eklendi.

**Özellikler:**
1. **Tarot Kartı Görselleri**
   ```python
   service = ImageGenerationService()
   image = service.generate_tarot_card_image(
       card_name="The Fool",
       card_meaning="Yeni başlangıçlar...",
       style="mystical"
   )
   ```

2. **Burç Sembol Görselleri**
   ```python
   image = service.generate_zodiac_symbol_image(
       zodiac_name="Koç",
       element="fire",
       traits="Cesur, enerjik..."
   )
   ```

3. **Arka Plan Görselleri**
   ```python
   image = service.generate_reading_background_image(
       theme="mystical night"
   )
   ```

**Kullanım:**
- Gemini 2.5 Flash API'yi kullanır
- SiteSettings'den API anahtarını alır
- Base64 image data döndürür
- Hata durumunda None döner
- Detaylı logging ile takip

### 4. 💰 Google AdSense Entegrasyonu

#### Reklam Alanları
Ana sayfa template'ine 5 farklı reklam alanı eklendi:

1. **Üst Banner** (728x90 veya 970x90)
   - Hero section'dan hemen sonra
   - Geniş ekranlara optimize

2. **Orta Rectangle** (300x250)
   - İçerik ortasında
   - Popüler yayılımlar sonrası

3. **Yan Skyscraper** (160x600)
   - Sağ tarafta sticky
   - Sadece büyük ekranlarda (>1400px)
   - Scroll ile sabit kalır

4. **Alt Banner** (728x90)
   - Sayfa sonunda
   - Footer'dan önce

5. **Mobil Banner** (Responsive)
   - Tüm boyutlarda responsive

#### Base.html Güncellemeleri
- Google AdSense script header'a eklendi
- Google Analytics hazır (yorum satırında)
- Ad client ID placeholder: `ca-pub-XXXXXXXXX`

#### CSS Stilleri
`main.css` dosyasına reklam stilleri eklendi:
- `.ad-container`: Reklam kutusu stil
- `.ad-placeholder`: Test/placeholder görünümü
- Responsive tasarım desteği
- Dark mode uyumlu

### 5. 🎭 Fake Hesaplar ve Örnek Okumalar

#### Management Command
Yeni command: `tarot/management/commands/create_fake_readings.py`

**Kullanım:**
```bash
python manage.py create_fake_readings
```

**Ne Yapar:**
- 6 fake kullanıcı oluşturur:
  - zeynep_yildiz
  - mehmet_ay
  - ayse_guneş
  - ali_deniz
  - fatma_yilmaz
  - ahmet_kara
  
- Her kullanıcı için 2-3 tarot okuması oluşturur
- Toplam ~15-18 örnek okuma
- Tüm okumalar herkese açık (is_public=True)
- Gerçekçi sorular ve AI yorumları
- Rastgele kartlar ve pozisyonlar

**Fake Sorular:**
- İş hayatı
- Aşk hayatı
- Mali durum
- Aile ilişkileri
- Kariyer
- Sağlık
- Arkadaşlıklar

## 🚀 Kurulum ve Kullanım

### 1. Database Migration
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Fake Data Oluşturma
```bash
python manage.py create_fake_readings
```

### 3. Google AdSense Kurulumu
1. `templates/base.html` dosyasını açın
2. `ca-pub-XXXXXXXXX` yerine kendi AdSense ID'nizi yazın
3. Her reklam bloğunda `data-ad-slot` değerlerini güncelleyin

### 4. Gemini API Kurulumu
1. Admin paneline giriş yapın
2. Site Settings'e gidin
3. Gemini API Key'inizi girin
4. Gemini Model: `gemini-2.5-flash` olarak ayarlayın

### 5. Sunucu Başlatma
```bash
# Virtual environment aktif etme
.venv\Scripts\activate

# Sunucu başlatma
python manage.py runserver
```

## 📂 Dosya Yapısı

```
djtarot/
├── tarot/
│   ├── services.py                 # ✨ ImageGenerationService eklendi
│   ├── views.py                    # 📊 Ana sayfa güncellendi
│   ├── templates/
│   │   └── tarot/
│   │       └── index.html          # 🎨 Yeni bölümler eklendi
│   └── management/
│       └── commands/
│           └── create_fake_readings.py  # 🆕 Yeni command
│
├── zodiac/
│   ├── models.py                   # 🌙 3 yeni model eklendi
│   └── admin.py                    # 🔧 Admin paneli güncellemesi
│
├── templates/
│   └── base.html                   # 💰 AdSense eklendi
│
└── static/
    └── css/
        └── main.css                # 🎨 Reklam stilleri eklendi
```

## 🔧 API Anahtarları

### Gerekli API Anahtarları:
1. **Google Gemini API** 
   - Tarot/burç yorumları için
   - Görsel üretimi için
   - [AI Studio](https://makersuite.google.com/app/apikey)

2. **Google AdSense**
   - Reklam geliri için
   - [AdSense Paneli](https://www.google.com/adsense)

3. **Google Analytics** (Opsiyonel)
   - Ziyaretçi analizi için
   - [Analytics Dashboard](https://analytics.google.com)

## 📊 Özellik Durumları

| Özellik | Durum | Açıklama |
|---------|-------|----------|
| Günlük Burç Yorumları | ✅ Tamamlandı | Ana sayfada önizleme |
| Fake Tarot Okumaları | ✅ Tamamlandı | Command ile oluşturma |
| Ay Burcu Modülü | ✅ Tamamlandı | Model ve admin hazır |
| Yükselen Burç | ✅ Tamamlandı | Model ve admin hazır |
| Gemini Görsel Üretimi | ✅ Tamamlandı | Service sınıfı hazır |
| Google AdSense | ✅ Tamamlandı | Tüm sayfalara entegre |

## 🎯 Sonraki Adımlar

### View ve Template İhtiyaçları:
1. **Ay Burcu Hesaplama Sayfası**
   - Form: Doğum tarihi, saati, yeri
   - Konum API entegrasyonu
   - Hesaplama ve sonuç gösterimi

2. **Yükselen Burç Hesaplama Sayfası**
   - Form: Doğum bilgileri
   - Hesaplama algoritması
   - Detaylı yorum gösterimi

3. **Kişisel Profil Sayfası**
   - Güneş + Ay + Yükselen birleşik görünüm
   - Grafik ve görselleştirme
   - AI destekli tam analiz

4. **Görsel Galeri**
   - Üretilen görselleri kaydetme
   - Galeri sayfası
   - Görsel paylaşma

## 🐛 Bilinen Sorunlar

1. **Görsel Üretimi**
   - Gemini 2.5 Flash henüz görsel üretimi desteklemiyor olabilir
   - Alternatif: Imagen 3 API kullanılabilir
   - Geçici çözüm: Placeholder görseller

2. **Ay Burcu Hesaplama**
   - Astronomik hesaplama kütüphanesi gerekli
   - Önerilen: `ephem` veya `skyfield` kütüphanesi

3. **AdSense Onayı**
   - Site içerik ve trafik şartlarını sağlamalı
   - Onay süreci 1-2 hafta sürebilir

## 💡 İpuçları

1. **Test Modu**
   - AdSense test reklamları için Auto ads kullanın
   - Production'da gerçek slot ID'leri girin

2. **Performans**
   - Fake okumalar sadece test için
   - Production'da gerçek kullanıcı içeriği tercih edin

3. **AI Maliyetleri**
   - Gemini API kullanımını monitör edin
   - Rate limiting ekleyin
   - Cache mekanizması kullanın

## 📞 Destek

Sorularınız için:
- GitHub Issues
- Email: info@tarotyorum.com
- Dokümantasyon: Bu dosya

---

**Son Güncelleme:** 6 Ekim 2025
**Versiyon:** 2.0.0
**Geliştirici:** AI Assistant
