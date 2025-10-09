# Gemini API Quota Aşımı Sorunu ve Çözümleri

## 🔴 Sorun

Admin panelden günlük yorum oluştururken her burç için "Bugün sizin için güzel bir gün olacak" gibi genel/fallback içerik oluşuyor.

### Hata Mesajı

```
❌ 429 You exceeded your current quota
Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests
Limit: 50 requests per day
Please retry in 24 hours
```

### Neden Oluyor?

1. **Gemini Free Tier Limiti**: Günde 50 istek
2. **Her Burç = 1 İstek**: 12 burç = 12 istek
3. **Test ve Geliştirme**: Bugün zaten 50+ istek yapılmış
4. **Quota Doldu**: Yeni istek yapılamıyor
5. **Fallback Çalışıyor**: Exception handler devreye giriyor

## ✅ Çözüm 1: 24 Saat Bekle (Otomatik)

### Ne Zaman?
- **Her gece 00:00'da** (UTC) quota sıfırlanır
- Yarın aynı saatte tekrar 50 istek hakkınız olur

### Nasıl Kontrol Edilir?
```bash
# Sonraki quota sıfırlama zamanını görmek için
python manage.py shell -c "from datetime import datetime, timezone; import pytz; now = datetime.now(pytz.UTC); next_reset = now.replace(hour=0, minute=0, second=0, microsecond=0); print(f'Sonraki sıfırlama: {next_reset}')"
```

### Öneriler
- **Sabah erken** yorum oluşturun (quota dolu olmadan)
- Günlük **tek seferlik** çalıştırın
- **Test için** başka API key kullanın

## ✅ Çözüm 2: Ücretli Plan (Kalıcı Çözüm)

### Fiyatlandırma

**Free Tier:**
- 50 istek/gün
- ❌ Üretim için yetersiz

**Pay As You Go:**
- $0.00025 / istek (Gemini 2.0 Flash)
- 12 burç x $0.00025 = **$0.003 / gün**
- **~$0.09 / ay** (çok ucuz!)
- ✅ Sınırsız istek

### Nasıl Aktive Edilir?

1. **Google Cloud Console**'a girin:
   https://console.cloud.google.com/

2. **Billing** bölümünü açın

3. **Kredi kartı** ekleyin

4. **Gemini API** için billing aktive edin

5. **API Key** değişmez, otomatik ücretli plana geçer

### Aylık Maliyet Tahmini

```
Senaryo 1: Sadece Günlük Yorumlar
- 12 burç x 30 gün = 360 istek
- 360 x $0.00025 = $0.09/ay

Senaryo 2: Haftalık + Aylık + Günlük
- Günlük: 360 istek
- Haftalık: 12 x 4 = 48 istek
- Aylık: 12 x 1 = 12 istek
- Toplam: 420 istek = $0.105/ay

Senaryo 3: AI Asistan + Yorumlar
- Otomatik yorumlar: 420 istek
- Kullanıcı soruları: ~100 istek
- Toplam: 520 istek = $0.13/ay
```

**Sonuç**: Ayda **$0.10-0.15** gibi çok düşük bir maliyet!

## ✅ Çözüm 3: Yeni API Key (Geçici)

### Test İçin Yeni Key

1. **Başka Google hesabı** açın
2. https://aistudio.google.com/apikey adresine gidin
3. **Yeni API key** oluşturun
4. `settings.py` dosyasına ekleyin:

```python
# Test API Key (günlük 50 istek)
GOOGLE_API_KEY_TEST = "your-new-api-key-here"

# Production API Key
GOOGLE_API_KEY = "your-main-api-key-here"
```

### Avantajları
- ✅ Hemen kullanılabilir
- ✅ Bedava 50 istek daha
- ✅ Test ve production ayrımı

### Dezavantajları
- ❌ Geçici çözüm
- ❌ Yine günlük 50 limit
- ❌ Sürdürülebilir değil

## ✅ Çözüm 4: Caching Sistemi (EN İYİ ÇÖZÜM)

### Django Cache ile Quota Tasarrufu

Bir kez oluşturulan yorumları cache'leyin, tekrar API çağrısı yapmayın.

### Implementasyon

#### 1. Cache Backend Ekle

`settings.py`:
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
    }
}
```

Veya Redis için:
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

#### 2. Cache Table Oluştur

```bash
python manage.py createcachetable
```

#### 3. generate_daily_horoscope'u Güncelle

`zodiac/views.py`:
```python
from django.core.cache import cache
from django.utils import timezone

def generate_daily_horoscope(zodiac_sign, date):
    """AI ile günlük burç yorumu oluştur - Cache'li versiyon"""
    
    # Cache key oluştur
    cache_key = f'daily_horoscope_{zodiac_sign.id}_{date}'
    
    # Önce cache'e bak
    cached_horoscope = cache.get(cache_key)
    if cached_horoscope:
        print(f"✅ Cache HIT: {zodiac_sign.name} için cache'den alındı")
        return cached_horoscope
    
    # Cache'de yoksa veritabanına bak
    existing = DailyHoroscope.objects.filter(
        zodiac_sign=zodiac_sign,
        date=date
    ).first()
    
    if existing:
        # Veritabanından alıp cache'e kaydet
        cache.set(cache_key, existing, 86400)  # 24 saat
        print(f"✅ DB HIT: {zodiac_sign.name} için veritabanından alındı")
        return existing
    
    # Hiçbir yerde yoksa AI ile oluştur
    print(f"🤖 API CALL: {zodiac_sign.name} için yeni yorum oluşturuluyor")
    try:
        # ... (mevcut AI çağrısı kodu) ...
        horoscope = DailyHoroscope.objects.create(...)
        
        # Cache'e kaydet
        cache.set(cache_key, horoscope, 86400)  # 24 saat
        return horoscope
        
    except Exception as e:
        # Fallback...
```

### Avantajları
- ✅ **90% quota tasarrufu**: Aynı gün için tekrar istek yapmaz
- ✅ **Hızlı yanıt**: Cache'den milisaniyeler içinde döner
- ✅ **Sunucu yükü azalır**: Veritabanı ve API yükü düşer
- ✅ **Maliyet tasarrufu**: Free tier yeterli olabilir

## 📊 Quota Kullanım Takibi

### Manuel Kontrol

Admin action'da quota kontrolü ekleyin:

`zodiac/admin.py`:
```python
def generate_horoscopes_for_today(self, request, queryset):
    # ... (mevcut kod) ...
    
    # Quota tahmini
    estimated_requests = 12  # 12 burç
    remaining_quota = 50 - estimated_requests  # Tahmini
    
    if remaining_quota < 5:
        self.message_user(
            request,
            f"⚠️ UYARI: Quota düşük! Tahmini kalan: {remaining_quota} istek",
            level=messages.WARNING
        )
```

### Otomatik Takip

Quota aşımını yakalayın:

`tarot/services.py`:
```python
def _generate_gemini(self, prompt):
    try:
        response = model.generate_content(prompt)
        # ...
    except ResourceExhausted as e:
        # Quota aşıldı
        logger.error("❌ QUOTA AŞILDI! 24 saat bekleyin veya ücretli plana geçin")
        
        # Admin'e email gönder
        from django.core.mail import mail_admins
        mail_admins(
            'Gemini API Quota Aşıldı',
            'Günlük 50 istek limiti doldu. Ücretli plana geçmeyi düşünün.',
            fail_silently=True
        )
        
        raise
```

## 🎯 Önerilen Strateji

### Kısa Vadede (Hemen)
1. ✅ **Yarın sabah** ilk iş günlük yorumları oluşturun
2. ✅ **Tek sefer** çalıştırın (test etmeyin)
3. ✅ Mevcut yorumları **silmeyin** (zaten oluşturulmuş)

### Orta Vadede (Bu Hafta)
1. ✅ **Caching sistemi** ekleyin (yukarıdaki kod)
2. ✅ **Ücretli plan** aktive edin ($0.10/ay)
3. ✅ **Quota takip** mekanizması ekleyin

### Uzun Vadede (Üretim)
1. ✅ **Redis cache** kullanın (hızlı)
2. ✅ **Celery** ile oto-generate (her gece 00:01)
3. ✅ **Monitoring** ekleyin (Sentry, Logging)
4. ✅ **Fallback içerik** iyileştirin (önceden hazırlanmış yorumlar)

## 🔍 Debug: Bugün Kaç İstek Yapıldı?

Gemini API'de doğrudan "bugün kaç istek yaptım" kontrolü yok, ama:

### Yaklaşık Hesaplama

```bash
# Bugün oluşturulan toplam horoscope sayısı
python manage.py shell -c "from zodiac.models import *; from django.utils import timezone; today = timezone.now().date(); daily_count = DailyHoroscope.objects.filter(created_at__date=today, ai_provider='gemini').count(); weekly_count = WeeklyHoroscope.objects.filter(created_at__date=today, ai_provider='gemini').count(); monthly_count = MonthlyHoroscope.objects.filter(created_at__date=today, ai_provider='gemini').count(); print(f'Bugün yapılan API çağrıları (tahmini): {daily_count + weekly_count + monthly_count}')"
```

### Fallback Kontrolü

```bash
# Bugün kaç tane fallback oluşturulmuş?
python manage.py shell -c "from zodiac.models import DailyHoroscope; from django.utils import timezone; today = timezone.now().date(); fallbacks = DailyHoroscope.objects.filter(created_at__date=today, general__startswith='[FALLBACK]').count(); print(f'Fallback sayısı: {fallbacks}')"
```

## 💡 SSS

### S: Neden hep "Bugün sizin için güzel bir gün olacak" yazıyor?

**C**: Quota doldu, AI çağrısı başarısız, fallback içerik dönüyor.

### S: Admin panel "başarılı" diyor ama içerik genel?

**C**: Kod hata yakalamıyor, fallback ile yeni kayıt oluşturuyor. Bu teknik olarak "başarılı".

### S: Yarın otomatik düzelir mi?

**C**: Evet! Quota sıfırlanınca (00:00 UTC) düzelir.

### S: Ücretli plan ne kadar?

**C**: Ayda ~$0.10-0.15 (çok ucuz!)

### S: Başka AI alternatifi var mı?

**C**: OpenAI, Anthropic (Claude), Cohere kullanılabilir ama hepsi ücretli ve daha pahalı.

## 📚 Referanslar

- [Gemini API Pricing](https://ai.google.dev/pricing)
- [Gemini API Rate Limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- [Django Caching](https://docs.djangoproject.com/en/5.0/topics/cache/)
- [Google Cloud Billing](https://console.cloud.google.com/billing)

---

**Son Güncelleme**: 6 Ekim 2025  
**Durum**: ❌ Quota Aşıldı - 24 saat bekle veya ücretli plana geç
