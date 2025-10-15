# AI İçerik Çoklu Dil Desteği Rehberi

## 📋 Genel Bakış

Bu dokümantasyon, tarot falı ve burç yorumları gibi AI tarafından üretilen içeriklerin kullanıcının seçtiği dilde (Türkçe, İngilizce, Almanca, Fransızca) sunulması için yapılan değişiklikleri açıklamaktadır.

## ✅ Tamamlanan Değişiklikler

### 1. Tarot Servisleri (`tarot/services.py`)

#### AIService Sınıfı

**`generate_interpretation()` Metodu:**
```python
def generate_interpretation(self, question, cards, spread_name, language='tr'):
    """
    Tarot yorumu üret
    
    Args:
        question: Kullanıcının sorusu
        cards: Seçilen kartlar listesi
        spread_name: Yayılım adı
        language: Yorum dili ('tr', 'en', 'de', 'fr')  # YENİ PARAMETRE
    """
```

**`_create_prompt()` Metodu:**
```python
def _create_prompt(self, question, cards, spread_name, language='tr'):
    """AI için prompt oluştur"""
    # Dil talimatları
    language_instructions = {
        'tr': 'Türkçe yanıt ver. ',
        'en': 'Respond in English. ',
        'de': 'Antworte auf Deutsch. ',
        'fr': 'Répondez en français. '
    }
    
    lang_instruction = language_instructions.get(language, language_instructions['tr'])
    prompt = f"""{lang_instruction}Sen profesyonel bir tarot yorumcususun..."""
```

**`_generate_fallback_interpretation()` Metodu:**
- API hatası durumunda bile dil desteği sağlanır
- Fallback mesajları 4 dilde hazır (TR, EN, DE, FR)

#### DailyCardService Sınıfı

**`generate_daily_interpretation()` Metodu:**
```python
def generate_daily_interpretation(self, card, is_reversed=False, language='tr'):
    """Günlük kart için özel yorum üret"""
    # Dil bazlı çeviriler
    language_map = {
        'tr': {
            'instruction': 'Türkçe yanıt ver. ',
            'direction_upright': 'Düz',
            'direction_reversed': 'Ters'
        },
        'en': {
            'instruction': 'Respond in English. ',
            'direction_upright': 'Upright',
            'direction_reversed': 'Reversed'
        },
        # ... de, fr
    }
```

### 2. Tarot Görünümleri (`tarot/views.py`)

**Tarot Falı Görünümü:**
```python
def tarot_reading_view(request):
    # Kullanıcının seçili dilini al
    from django.utils.translation import get_language
    current_language = get_language()
    
    ai_service = AIService()
    interpretation = ai_service.generate_interpretation(
        question=question,
        cards=ai_cards,
        spread_name=spread.name,
        language=current_language  # DİL PARAMETRESİ EKLENDI
    )
```

**Günlük Kart Görünümü:**
```python
@login_required
def daily_card(request):
    # Kullanıcının seçili dilini al
    from django.utils.translation import get_language
    current_language = get_language()
    
    daily_service = DailyCardService()
    interpretation = daily_service.generate_daily_interpretation(
        random_card, 
        is_reversed,
        language=current_language  # DİL PARAMETRESİ EKLENDI
    )
```

### 3. Burç Servisleri (`zodiac/services.py`)

#### ZodiacAIService Sınıfı

**`generate_daily_horoscope()` Metodu:**
```python
def generate_daily_horoscope(self, zodiac_sign, date, language='tr'):
    """Günlük burç yorumu oluştur"""
    # Dil talimatı
    language_instructions = {
        'tr': 'Türkçe yanıt ver. ',
        'en': 'Respond in English. ',
        'de': 'Antworte auf Deutsch. ',
        'fr': 'Répondez en français. '
    }
    lang_instruction = language_instructions.get(language, language_instructions['tr'])
    
    prompt = f"""{lang_instruction}Sen profesyonel bir astrolog..."""
```

**`generate_weekly_horoscope()` Metodu:**
- Haftalık yorumlar için dil parametresi eklendi
- Prompt'a dil talimatı eklendi

**`generate_monthly_horoscope()` Metodu:**
- Aylık yorumlar için dil parametresi eklendi
- Prompt'a dil talimatı eklendi

**`generate_compatibility_analysis()` Metodu:**
- Burç uyumluluk analizi için dil parametresi eklendi
- Prompt'a dil talimatı eklendi

### 4. Burç Görünümleri (`zodiac/views.py`)

**`generate_daily_horoscope()` Fonksiyonu:**
```python
def generate_daily_horoscope(zodiac_sign, date, language='tr'):
    """AI ile günlük burç yorumu oluştur"""
    # Cache sadece Türkçe için kullanılıyor
    existing = DailyHoroscope.objects.filter(
        zodiac_sign=zodiac_sign,
        date=date
    ).first()
    
    if existing and language == 'tr':  # Sadece Türkçe için cache
        return existing
    
    # Yeni yorum oluştur
    ai_service = ZodiacAIService()
    result = ai_service.generate_daily_horoscope(zodiac_sign, date, language)
```

**`zodiac_sign_detail()` Görünümü:**
```python
def zodiac_sign_detail(request, sign_slug):
    from django.utils.translation import get_language
    
    current_language = get_language()
    
    # Yoksa oluştur (dil-aware)
    if not daily_horoscope or (daily_horoscope and current_language != 'tr'):
        daily_horoscope = generate_daily_horoscope(zodiac_sign, today, current_language)
```

**`daily_horoscopes()` Görünümü:**
```python
def daily_horoscopes(request):
    from django.utils.translation import get_language
    
    current_language = get_language()
    
    # Yoksa oluştur (dil-aware)
    if not horoscope or (horoscope and current_language != 'tr'):
        horoscope = generate_daily_horoscope(sign, today, current_language)
```

## 🎯 Nasıl Çalışır?

### 1. Dil Algılama
```python
from django.utils.translation import get_language
current_language = get_language()  # 'tr', 'en', 'de', 'fr'
```

### 2. AI'ya Dil Talimatı Gönderme
```python
language_instructions = {
    'tr': 'Türkçe yanıt ver. ',
    'en': 'Respond in English. ',
    'de': 'Antworte auf Deutsch. ',
    'fr': 'Répondez en français. '
}

prompt = f"{language_instructions[language]}Sen profesyonel bir tarot yorumcususun..."
```

### 3. AI Yanıt Verme
- OpenAI GPT-4o veya Google Gemini prompt'taki dil talimatını okur
- İstenen dilde yanıt üretir
- Fallback durumunda bile hazır çeviriler kullanılır

## 📊 Desteklenen Diller

| Dil       | Kod | Bayrak | Durum |
|-----------|-----|--------|-------|
| Türkçe    | tr  | 🇹🇷    | ✅ Aktif |
| İngilizce | en  | 🇬🇧    | ✅ Aktif |
| Almanca   | de  | 🇩🇪    | ✅ Aktif |
| Fransızca | fr  | 🇫🇷    | ✅ Aktif |

## 🔍 Değişiklik Yapılan Dosyalar

### Tarot Modülü
- ✅ `tarot/services.py` - AIService ve DailyCardService
- ✅ `tarot/views.py` - Tarot falı ve günlük kart görünümleri

### Zodiac Modülü
- ✅ `zodiac/services.py` - ZodiacAIService
- ✅ `zodiac/views.py` - Burç detayı ve günlük yorumlar

## 🎨 Örnek Kullanım

### Tarot Falı (İngilizce)
```python
# Kullanıcı dil seçiciyi 🇬🇧 English'e çevirir
# Tarot falı çeker
ai_service.generate_interpretation(
    question="What does my future hold?",
    cards=[...],
    spread_name="Three Card Spread",
    language='en'  # get_language() otomatik olarak 'en' döner
)

# AI Yanıtı (İngilizce):
# "The Three of Cups suggests celebration and friendship in your near future..."
```

### Burç Yorumu (Almanca)
```python
# Kullanıcı dil seçiciyi 🇩🇪 Deutsch'a çevirir
# Koç burcunun günlük yorumunu görüntüler
ai_service.generate_daily_horoscope(
    zodiac_sign=aries,
    date=today,
    language='de'  # get_language() otomatik olarak 'de' döner
)

# AI Yanıtı (Almanca):
# "Heute ist ein guter Tag für den Widder. Die Sterne stehen günstig..."
```

## ⚠️ Önemli Notlar

### 1. Cache Stratejisi
- **Türkçe yorumlar** → Veritabanında cache'lenir (performans için)
- **Diğer diller (EN, DE, FR)** → Her seferinde yeni üretilir (güncel AI yanıtı için)

### 2. Fallback Mekanizması
- AI servisi başarısız olursa bile 4 dilde hazır fallback mesajları var
- Kullanıcı deneyimi kesintisiz devam eder

### 3. API Maliyeti
- Türkçe dışındaki diller için her istek yeni API çağrısı yapar
- OpenAI/Gemini quota'larını göz önünde bulundurun

## 🧪 Test Senaryoları

### Test 1: Tarot Falı - 4 Dil
1. ✅ Türkçe seç → Fal çek → Türkçe yorum görmeli
2. ✅ İngilizce seç → Fal çek → İngilizce yorum görmeli
3. ✅ Almanca seç → Fal çek → Almanca yorum görmeli
4. ✅ Fransızca seç → Fal çek → Fransızca yorum görmeli

### Test 2: Günlük Burç Yorumu - 4 Dil
1. ✅ Koç burcu detay sayfası → Türkçe yorum
2. ✅ Dili İngilizce'ye çevir → Sayfayı yenile → İngilizce yorum
3. ✅ Dili Almanca'ya çevir → Sayfayı yenile → Almanca yorum
4. ✅ Dili Fransızca'ya çevir → Sayfayı yenile → Fransızca yorum

### Test 3: API Hatası Durumu
1. ✅ AI API'yi simüle şekilde başarısız yap
2. ✅ Fallback mesajlarının doğru dilde gösterildiğini kontrol et

## 📈 İyileştirme Önerileri

### Gelecek Versiyonlar İçin

1. **Cache İyileştirmesi:**
   ```python
   # Tüm diller için cache
   cache_key = f"horoscope_{zodiac_sign.id}_{date}_{language}"
   cached = cache.get(cache_key)
   ```

2. **Batch İşleme:**
   ```python
   # 12 burcun tümü için tek seferde AI çağrısı
   def generate_all_daily_horoscopes(date, language):
       # Tek prompt'ta 12 burcun hepsini iste
   ```

3. **Çeviri Kalitesi İyileştirme:**
   ```python
   # AI'ya daha detaylı talimatlar
   f"Respond in formal/professional {language} appropriate for astrology."
   ```

## 🚀 Deploy Notları

### Sunucuya Yüklerken:
```bash
# Değişen dosyaları yükle
scp tarot/services.py django@159.89.108.100:/home/django/projects/horoscope/tarot/
scp tarot/views.py django@159.89.108.100:/home/django/projects/horoscope/tarot/
scp zodiac/services.py django@159.89.108.100:/home/django/projects/horoscope/zodiac/
scp zodiac/views.py django@159.89.108.100:/home/django/projects/horoscope/zodiac/

# Sunucuda gunicorn'u yeniden başlat
ssh django@159.89.108.100
sudo systemctl restart gunicorn
```

## 📝 Özet

✅ **Tarot yorumları** artık 4 dilde üretiliyor
✅ **Burç yorumları** artık 4 dilde üretiliyor
✅ **Günlük kart** artık 4 dilde üretiliyor
✅ **Fallback mesajları** 4 dilde hazır
✅ **Dil otomatik algılanıyor** (get_language())
✅ **AI prompt'ları** dil talimatı içeriyor

🎯 **Sonuç:** Kullanıcı hangi dili seçerse AI içerik o dilde sunuluyor!

---

**Hazırlayan:** GitHub Copilot  
**Tarih:** 2025  
**Versiyon:** 1.0
