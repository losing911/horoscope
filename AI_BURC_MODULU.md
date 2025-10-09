# 🤖 AI Entegrasyonu - Burç Modülü

## ✅ Mevcut AI Özellikleri

### 1. **Günlük Burç Yorumları** (Otomatik Gemini)
- **Fonksiyon**: `generate_daily_horoscope()`
- **Model**: `DailyHoroscope`
- **Özellikler**:
  - 5 bölüm: Genel, Aşk, Kariyer, Sağlık, Finans
  - Otomatik oluşturma (sayfa yüklendiğinde)
  - Şanslı sayı ve renk
  - Ruh hali skoru (1-10)

### 2. **Haftalık Burç Yorumları** (YENİ)
- **Fonksiyon**: `generate_weekly_horoscope()`
- **Model**: `WeeklyHoroscope`
- **Özellikler**:
  - 6 bölüm: Genel, Aşk, Kariyer, Sağlık, Finans, Önemli Günler
  - Haftalık trendler ve öneriler
  - Detaylı analiz (4-5 cümle/bölüm)

### 3. **Aylık Burç Yorumları** (YENİ)
- **Fonksiyon**: `generate_monthly_horoscope()`
- **Model**: `MonthlyHoroscope`
- **Özellikler**:
  - 7 bölüm: Genel, Aşk, Kariyer, Sağlık, Finans, Önemli Tarihler, Tavsiyeler
  - Aylık astrolojik trendler
  - Kapsamlı yorum (5-6 cümle/bölüm)

### 4. **Burç Uyumu Analizi**
- **Fonksiyon**: `generate_compatibility()`
- **Model**: `CompatibilityReading`
- **Özellikler**:
  - 5 bölüm: Aşk, Arkadaşlık, İş, Zorluklar, Tavsiyeler
  - Element bazlı uyum skoru (0-100)
  - Çift burç karşılaştırması

### 5. **AI Burç Asistanı** (YENİ - İnteraktif)
- **URL**: `/zodiac/ai-assistant/`
- **View**: `ai_zodiac_assistant()`
- **Özellikler**:
  - Kullanıcı serbest soru sorabilir
  - Burç seçimi ile kişiselleştirme
  - Gemini AI ile doğal dil yanıtları
  - Kayıtlı kullanıcı gerekli

### 6. **AI Görsel Üretimi** (Gemini 2.5 Flash)
- **Service**: `ImageGenerationService.generate_zodiac_symbol_image()`
- **Özellikler**:
  - Burç sembolü görselleri
  - Element bazlı renk şemaları
  - Mistik/cosmic stil
  - İsteğe bağlı (`?generate_image=1`)

## 🔧 Teknik Detaylar

### AI Service Kullanımı

```python
from tarot.services import AIService, ImageGenerationService

# Metin yorumu için
ai_service = AIService()
response = ai_service.generate_interpretation(
    question=prompt,
    cards=[],
    spread_name="Burç Yorumu"
)

# Görsel üretimi için
image_service = ImageGenerationService()
image_data = image_service.generate_zodiac_symbol_image(
    zodiac_name="Koç",
    element="Ateş",
    traits="Cesur, Enerjik, Lider..."
)
```

### Prompt Yapısı

Tüm AI promptları şu yapıyı takip eder:

```
1. Rol tanımı: "Sen profesyonel bir astrologsun..."
2. Context: Burç özellikleri, tarih, vb.
3. İstek: Spesifik görev
4. Format: Bölümler ve uzunluk
5. Ton: Pozitif, yapıcı, motive edici
```

### Response Parsing

`parse_horoscope_response()` fonksiyonu:
- BÜYÜK HARFLE başlıkları tespit eder
- Her bölümü dictionary'ye ayırır
- Key: başlık, Value: içerik

## 📊 Veri Akışı

```
Kullanıcı İsteği
    ↓
View Fonksiyonu (views.py)
    ↓
AI Prompt Oluşturma
    ↓
AIService.generate_interpretation()
    ↓
Gemini API (gemini-2.0-flash-exp)
    ↓
Response Parsing
    ↓
Model Kayıt (Database)
    ↓
Template Render
    ↓
Kullanıcıya Sonuç
```

## 🎯 Kullanım Senaryoları

### Senaryo 1: Günlük Yorum Otomatik
```python
# zodiac/daily/ sayfası ziyaret edilir
# View tüm burçları kontrol eder
# Bugün için yorum yoksa:
horoscope = generate_daily_horoscope(sign, today)
# Yorum oluşturulur ve kaydedilir
```

### Senaryo 2: Kullanıcı AI Asistana Soru Sorar
```python
# /zodiac/ai-assistant/ sayfası
# Kullanıcı: "Bu ay kariyer için nasıl?"
# AI: Burcunu kontrol eder, kişiselleştirilmiş yanıt verir
# Yanıt template'de gösterilir
```

### Senaryo 3: Görsel İsteği
```python
# /zodiac/sign/koc/?generate_image=1
# ImageGenerationService çağrılır
# Gemini 2.5 Flash görsel üretir
# Base64 image template'e gönderilir
```

## 🚀 Performans İyileştirmeleri

### Cache Stratejisi (Önerilen)
```python
from django.core.cache import cache

def get_or_generate_horoscope(sign, date):
    cache_key = f'horoscope_{sign.id}_{date}'
    horoscope = cache.get(cache_key)
    
    if not horoscope:
        horoscope = generate_daily_horoscope(sign, date)
        cache.set(cache_key, horoscope, 86400)  # 24 saat
    
    return horoscope
```

### Celery Task (İleri Seviye)
```python
from celery import shared_task

@shared_task
def generate_all_daily_horoscopes():
    """Her gün saat 00:00'da çalışır"""
    today = timezone.now().date()
    signs = ZodiacSign.objects.all()
    
    for sign in signs:
        generate_daily_horoscope(sign, today)
```

## 📈 API Limitleri ve Maliyet

### Gemini API Kullanımı
- Model: `gemini-2.0-flash-exp`
- Free tier: 15 istek/dakika
- Günlük limit: 1500 istek/gün

### Optimizasyon Önerileri
1. **Cache kullan**: Aynı yorumu tekrar üretme
2. **Batch işlemler**: Tüm burçları toplu oluştur
3. **Fallback mekanizması**: API hatası durumunda statik metin
4. **Rate limiting**: API çağrılarını sınırla

## 🔒 Güvenlik ve Sınırlamalar

### Kimlik Doğrulama
- AI Asistan: `@login_required`
- Uyum analizi: `@login_required`
- Görsel üretimi: Herkes (GET parametresi ile)

### Hata Yönetimi
```python
try:
    horoscope = generate_daily_horoscope(sign, today)
except Exception as e:
    print(f"Error: {e}")
    # Fallback: Statik veya önceki yorum
    horoscope = create_fallback_horoscope(sign, today)
```

## 🎨 Frontend Entegrasyonu

### Template Kullanımı
```html
<!-- AI Yorumu Gösterme -->
<div class="ai-response">
    {{ horoscope.general|linebreaks }}
</div>

<!-- AI Badge -->
<span class="badge bg-info">
    <i class="fas fa-robot"></i> AI Yorum
</span>

<!-- Görsel Gösterme -->
{% if zodiac_image %}
<img src="data:image/png;base64,{{ zodiac_image }}" 
     alt="AI Generated" 
     class="img-fluid">
{% endif %}
```

### JavaScript İnteraktiflik (Opsiyonel)
```javascript
// Yorum yenileme
function refreshHoroscope(signId) {
    fetch(`/zodiac/api/refresh/${signId}/`)
        .then(r => r.json())
        .then(data => {
            document.querySelector('.horoscope-content')
                    .innerHTML = data.general;
        });
}
```

## 📚 Ek Özellikler (Planlanan)

### 1. Burç Tahmini
- Kullanıcı davranışlarına göre burç tahmini
- ML model eğitimi

### 2. Çoklu Dil Desteği
- İngilizce, Almanca yorumlar
- `Accept-Language` header kontrolü

### 3. Sesli Yorum
- Text-to-Speech entegrasyonu
- AI yorumlarını sesli dinleme

### 4. Kişisel Takvim
- Aylık burç takvimi PDF export
- İCal formatında önemli tarihler

## 🐛 Bilinen Sorunlar ve Çözümler

### Sorun 1: Unicode hatası (Windows)
```
UnicodeEncodeError: 'charmap' codec can't encode...
```
**Çözüm**: UTF-8 encoding kullan
```python
print(response.encode('utf-8', errors='ignore'))
```

### Sorun 2: API rate limit
```
ResourceExhausted: 429 Quota exceeded
```
**Çözüm**: Exponential backoff veya cache

### Sorun 3: Boş response
```
AI yanıt boş geliyor
```
**Çözüm**: Fallback mekanizması ve loglama

## 📞 İletişim ve Destek

Sorular için:
- GitHub Issues
- Proje wiki
- Developer documentation

---

**Son Güncelleme**: 6 Ekim 2025
**Versiyon**: 2.0
**AI Model**: Google Gemini 2.0 Flash (Experimental)
