# OpenAI Model Seçim Kılavuzu

## 🎯 Hangi Model Ne Zaman Kullanılmalı?

### GPT-4o (Şu An Aktif) ⭐
**Ne Zaman:**
- Tarot yorumları (detaylı ve içgörülü)
- Astroloji analizleri
- Kullanıcı soruları (AI Asistan)
- Premium içerik

**Avantajlar:**
- ✅ En güçlü multimodal model
- ✅ Yüksek kalite yorumlar
- ✅ Dengeli hız/performans
- ✅ Güncel bilgi (2024'e kadar)

**Maliyet:**
- $0.01-0.02 / yorum (orta)

### GPT-o1 (Yeni - Reasoning) 🧠
**Ne Zaman:**
- Çok karmaşık tarot spreads (10+ kart)
- Derin psikolojik analiz
- Felsefik sorular
- Karar verme desteği

**Avantajlar:**
- ✅ En akıllı model (akıl yürütme)
- ✅ Derin analiz
- ✅ Mantıksal bağlantılar
- ✅ Karmaşık problemler

**Dezavantajlar:**
- ❌ Daha yavaş (10-30 saniye)
- ❌ Daha pahalı ($0.08-0.10/yorum)

### GPT-4o Mini (Ekonomik) 💰
**Ne Zaman:**
- Basit tarot okumaları (1-3 kart)
- Günlük burç yorumları
- Hızlı yanıtlar
- Yüksek trafik

**Avantajlar:**
- ✅ Çok ucuz ($0.001/yorum)
- ✅ Çok hızlı (2-5 saniye)
- ✅ Yeterli kalite
- ✅ Yüksek limit

**Kullanım Önerisi:**
```python
# Basit okumalar için mini
if len(cards) <= 3:
    model = 'gpt-4o-mini'
else:
    model = 'gpt-4o'
```

### Gemini 1.5 Flash (Google) 🔵
**Ne Zaman:**
- Burç yorumları (günlük/haftalık/aylık)
- Yüksek hacimli işlemler
- Bütçe kısıtlı projeler
- Test ve geliştirme

**Avantajlar:**
- ✅ Free tier (50 istek/gün)
- ✅ Çok ucuz ($0.09/ay tüm burçlar)
- ✅ Hızlı
- ✅ Türkçe desteği iyi

**Kullanım:**
- Burç yorumları için ideal
- Tarot için GPT-4o tercih edilir

## 📊 Senaryolar

### Senaryo 1: Karma Strateji (Önerilen) ⭐

**Tarot Okumaları:**
- 1-3 kart: GPT-4o Mini ($0.001)
- 4-9 kart: GPT-4o ($0.015)
- 10+ kart: GPT-o1 ($0.08)

**Astroloji:**
- Günlük burç: Gemini Flash (bedava)
- Haftalık burç: GPT-4o Mini ($0.001)
- Aylık burç: GPT-4o ($0.015)
- Doğum haritası: GPT-4o ($0.02)

**Aylık Tahmini Maliyet:**
- 100 tarot: $1.50
- 360 günlük burç: $0 (Gemini free)
- 48 haftalık burç: $0.05
- 12 aylık burç: $0.18
- **TOPLAM: ~$2/ay**

### Senaryo 2: Full Premium (En Kaliteli)

**Hepsi GPT-4o:**
- 100 tarot: $1.50
- 360 günlük burç: $5.40
- 48 haftalık burç: $0.72
- 12 aylık burç: $0.18
- **TOPLAM: ~$8/ay**

**Avantajları:**
- En yüksek kalite
- Tutarlı format
- Tek provider

### Senaryo 3: Budget Mode (Ekonomik)

**Hepsi GPT-4o Mini veya Gemini:**
- 100 tarot: $0.10 (mini)
- 360 günlük burç: $0 (Gemini free)
- 48 haftalık burç: $0.05 (mini)
- 12 aylık burç: $0.01 (mini)
- **TOPLAM: ~$0.16/ay**

**Kısıtları:**
- Daha basit yorumlar
- Bazı nüanslar kaçabilir

## 🔄 Dinamik Model Seçimi

### Implementasyon Örneği

`tarot/views.py` içine ekleyin:

```python
def select_optimal_model(card_count, question_complexity, user_tier='free'):
    """
    İş yükü ve kullanıcı seviyesine göre en uygun modeli seç
    """
    # Premium kullanıcılar için
    if user_tier == 'premium':
        if card_count >= 10 or question_complexity == 'high':
            return 'openai', 'o1'
        else:
            return 'openai', 'gpt-4o'
    
    # Free kullanıcılar için
    if card_count <= 3:
        return 'openai', 'gpt-4o-mini'
    elif card_count <= 7:
        return 'openai', 'gpt-4o'
    else:
        return 'openai', 'gpt-4o'  # Limit

def create_reading(request):
    # ...
    card_count = len(selected_cards)
    user_tier = request.user.profile.tier if hasattr(request.user, 'profile') else 'free'
    
    provider, model = select_optimal_model(card_count, 'medium', user_tier)
    
    # Özel model ile AI servis başlat
    site_settings = SiteSettings.load()
    old_provider = site_settings.default_ai_provider
    old_model = site_settings.openai_model
    
    # Geçici olarak değiştir
    site_settings.default_ai_provider = provider
    if provider == 'openai':
        site_settings.openai_model = model
    
    ai = AIService()
    interpretation = ai.generate_interpretation(question, cards, spread_name)
    
    # Eski ayarlara dön
    site_settings.default_ai_provider = old_provider
    site_settings.openai_model = old_model
    # ...
```

### Burç Yorumları için Özel Seçim

`zodiac/views.py` içinde:

```python
def generate_daily_horoscope(zodiac_sign, date):
    """Gemini ile günlük burç yorumu (ekonomik)"""
    ai_service = AIService(provider_name='gemini')  # Gemini zorla
    # ...

def generate_birth_chart_analysis(birth_data):
    """GPT-4o ile doğum haritası (detaylı)"""
    ai_service = AIService(provider_name='openai')
    # Geçici olarak GPT-4o'ya geç
    ai_service.model = 'gpt-4o'
    # ...
```

## 🎛️ Admin Panelden Hızlı Değiştirme

### Günlük İşlemler İçin

1. **Admin Panel** → http://127.0.0.1:8000/admin/
2. **TAROT** → **Site settings**
3. Model değiştir:
   - Sabah: `gpt-4o-mini` (trafik yüksek, ekonomik)
   - Akşam: `gpt-4o` (trafik düşük, kaliteli)
4. **Kaydet**

### A/B Test İçin

İki farklı SiteSettings profili:

```python
# Morning profile (8:00-18:00)
morning_settings = {
    'default_ai_provider': 'openai',
    'openai_model': 'gpt-4o-mini',
}

# Evening profile (18:00-8:00)
evening_settings = {
    'default_ai_provider': 'openai',
    'openai_model': 'gpt-4o',
}

# Cron job ile otomatik değiştir
# 0 8 * * * python manage.py switch_ai_profile morning
# 0 18 * * * python manage.py switch_ai_profile evening
```

## 📈 Performans Metrikleri

### GPT-4o
- Yanıt süresi: 3-8 saniye
- Token/saniye: ~60
- Başarı oranı: %99.9

### GPT-o1
- Yanıt süresi: 10-30 saniye
- Token/saniye: ~20 (düşünme süresi dahil)
- Başarı oranı: %99.5

### GPT-4o Mini
- Yanıt süresi: 1-3 saniye
- Token/saniye: ~100
- Başarı oranı: %99.8

### Gemini 1.5 Flash
- Yanıt süresi: 2-5 saniye
- Token/saniye: ~80
- Başarı oranı: %98 (bazen format hataları)

## 💡 En İyi Pratikler

### 1. Monitoring Ekleyin
```python
import time

start = time.time()
result = ai.generate_interpretation(...)
duration = time.time() - start

# Log at
logger.info(f"⏱️ Yanıt süresi: {duration:.2f}s - Model: {ai.model}")
```

### 2. Fallback Stratejisi
```python
try:
    ai = AIService(provider_name='openai')
    result = ai.generate_interpretation(...)
except Exception as e:
    logger.error(f"OpenAI başarısız, Gemini'ye geçiliyor: {e}")
    ai = AIService(provider_name='gemini')
    result = ai.generate_interpretation(...)
```

### 3. User Feedback
```python
# Her yorumdan sonra
if reading.user_rating >= 4:
    # Kullanılan modeli logla (başarılı)
    analytics.log_success(model=ai.model, rating=reading.user_rating)
else:
    # Model iyileştirmesi gerekebilir
    analytics.log_improvement_needed(model=ai.model)
```

## 🎓 Model Seçim Cheat Sheet

| Durum | Model | Maliyet | Kalite | Hız |
|-------|-------|---------|--------|-----|
| 1-3 Kart Tarot | gpt-4o-mini | $ | ⭐⭐⭐⭐ | ⚡⚡⚡ |
| 4-9 Kart Tarot | gpt-4o | $$ | ⭐⭐⭐⭐⭐ | ⚡⚡ |
| 10+ Kart Tarot | o1 | $$$$ | ⭐⭐⭐⭐⭐ | ⚡ |
| Günlük Burç | Gemini | FREE | ⭐⭐⭐⭐ | ⚡⚡⚡ |
| Doğum Haritası | gpt-4o | $$ | ⭐⭐⭐⭐⭐ | ⚡⚡ |
| AI Sohbet | gpt-4o-mini | $ | ⭐⭐⭐⭐ | ⚡⚡⚡ |
| Karmaşık Analiz | o1 | $$$$ | ⭐⭐⭐⭐⭐ | ⚡ |

---

**Önerilen Başlangıç Konfigürasyonu:**
- Default: `gpt-4o` (dengeli)
- Burç yorumları: `gemini` (ekonomik)
- Upgrade yolu: Kullanıcı geri bildirimine göre

🚀 **Sistem hazır, istediğiniz modeli kullanabilirsiniz!**
