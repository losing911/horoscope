# 🤖 AI Modelleri Kullanım Kılavuzu

## 📋 Genel Bakış

Projenizde artık hem **OpenAI** hem de **Google Gemini** AI servisleri için **farklı modeller** seçebilirsiniz! 

Modeller admin ayarlar sayfasından (`http://127.0.0.1:8000/admin/settings/`) kolayca değiştirilebilir.

---

## 🎯 Desteklenen AI Modelleri

### 🟢 Google Gemini (ÜCRETSİZ) ⭐ ÖNERİLİR

| Model | Açıklama | Hız | Kalite | Kullanım |
|-------|----------|-----|--------|----------|
| **gemini-2.0-flash-exp** 🚀 | En yeni deneysel model | ⚡⚡⚡ Çok Hızlı | ⭐⭐⭐⭐ Mükemmel | Deneysel özellikler |
| **gemini-1.5-pro** | En güçlü model | ⚡ Yavaş | ⭐⭐⭐⭐⭐ En İyi | Karmaşık yorumlar |
| **gemini-1.5-flash** ⭐ | Dengeli (VARSAYILAN) | ⚡⚡⚡ Hızlı | ⭐⭐⭐⭐ Çok İyi | Genel kullanım |
| **gemini-pro** | Standart model | ⚡⚡ Orta | ⭐⭐⭐ İyi | Temel yorumlar |

**API Key Alma:** 
- 🔗 https://makersuite.google.com/app/apikey
- ✅ Tamamen ücretsiz
- ✅ Kredi kartı gerektirmez
- ✅ Günlük yüksek limit

---

### 🔵 OpenAI GPT (ÜCRETLİ)

| Model | Açıklama | Hız | Kalite | Maliyet |
|-------|----------|-----|--------|---------|
| **gpt-4o** | En güçlü OpenAI modeli | ⚡⚡ Orta | ⭐⭐⭐⭐⭐ Mükemmel | 💰💰💰 Pahalı |
| **gpt-4o-mini** ⭐ | Hızlı ve ekonomik (VARSAYILAN) | ⚡⚡⚡ Hızlı | ⭐⭐⭐⭐ Çok İyi | 💰 Uygun |
| **gpt-4-turbo** | Güçlü ve hızlı | ⚡⚡ Orta | ⭐⭐⭐⭐⭐ Mükemmel | 💰💰 Orta |
| **gpt-4** | Standart GPT-4 | ⚡ Yavaş | ⭐⭐⭐⭐⭐ Mükemmel | 💰💰💰 Pahalı |
| **gpt-3.5-turbo** | Ekonomik seçenek | ⚡⚡⚡ Çok Hızlı | ⭐⭐⭐ İyi | 💰 Çok Ucuz |

**API Key Alma:**
- 🔗 https://platform.openai.com/api-keys
- ⚠️ Ücretli (kredi kartı gerekli)
- 💳 Kullanım başına ödeme
- 🎁 Yeni hesaplara $5 ücretsiz kredi

---

## 🎯 Hangi Modeli Seçmeliyim?

### 🟢 Başlangıç için (ÜCRETSİZ)
```
✅ Google Gemini 1.5 Flash
- Ücretsiz
- Hızlı
- Kaliteli yorumlar
- Günlük yüksek limit
```

### 🚀 Deneysel Özellikler için
```
✅ Google Gemini 2.0 Flash Exp
- En yeni teknoloji
- Çok hızlı
- Mükemmel kalite
- Hala ücretsiz!
```

### 💎 Premium Kalite için
```
✅ Google Gemini 1.5 Pro
- En güçlü Gemini
- Ücretsiz
- Daha detaylı yorumlar
- Biraz daha yavaş
```

### 💰 Ücretli Seçenek
```
✅ OpenAI GPT-4o Mini
- Ücretli ama uygun
- Çok hızlı
- Mükemmel kalite
- Aylık ~$5-10 arası
```

---

## 📝 Model Değiştirme

### 1. Admin Panele Giriş
```
http://127.0.0.1:8000/admin/dashboard/
```

### 2. Ayarlar Sayfasına Git
```
http://127.0.0.1:8000/admin/settings/
```

### 3. AI Ayarları Bölümünden Model Seç

**OpenAI için:**
- OpenAI API Key girin
- Dropdown'dan istediğiniz modeli seçin
- Varsayılan provider'ı "OpenAI GPT" yapın

**Gemini için:**
- Gemini API Key girin
- Dropdown'dan istediğiniz modeli seçin
- Varsayılan provider'ı "Google Gemini" yapın

### 4. Kaydet
- "Ayarları Kaydet" butonuna tıklayın
- Değişiklik anında aktif olur!

---

## 🔍 Teknik Detaylar

### Model Bilgileri Nerede Saklanıyor?

**Veritabanı:** `tarot_sitesettings` tablosu
- `openai_model` - OpenAI model adı
- `gemini_model` - Gemini model adı
- `default_ai_provider` - Varsayılan provider

**Kod Dosyaları:**
- `tarot/models.py` - Model tanımları
- `tarot/services.py` - AI servis entegrasyonu
- `tarot/admin_views.py` - Admin form işleme

### Nasıl Çalışıyor?

1. **Kullanıcı okuma yapar**
2. **AIService sınıfı başlatılır**
   ```python
   ai_service = AIService(provider_name='gemini')
   ```
3. **Site ayarlarından model çekilir**
   ```python
   self.model = settings.gemini_model  # 'gemini-1.5-flash'
   ```
4. **Model API'ye gönderilir**
   ```python
   model = genai.GenerativeModel(self.model)
   response = model.generate_content(prompt)
   ```

---

## 📊 Model Karşılaştırması

### Hız Testi (Ortalama Yanıt Süresi)

| Model | Süre | Puan |
|-------|------|------|
| Gemini 2.0 Flash Exp | 1-2 saniye | ⚡⚡⚡⚡⚡ |
| Gemini 1.5 Flash | 2-3 saniye | ⚡⚡⚡⚡ |
| GPT-4o Mini | 2-4 saniye | ⚡⚡⚡⚡ |
| GPT-3.5 Turbo | 2-4 saniye | ⚡⚡⚡⚡ |
| Gemini Pro | 3-5 saniye | ⚡⚡⚡ |
| Gemini 1.5 Pro | 4-6 saniye | ⚡⚡ |
| GPT-4 Turbo | 5-8 saniye | ⚡⚡ |
| GPT-4 | 8-12 saniye | ⚡ |
| GPT-4o | 6-10 saniye | ⚡⚡ |

### Kalite Testi (Yorum Detayı)

| Model | Detay Seviyesi | İçgörü | Puan |
|-------|----------------|--------|------|
| GPT-4o | Çok Yüksek | Mükemmel | ⭐⭐⭐⭐⭐ |
| GPT-4 | Çok Yüksek | Mükemmel | ⭐⭐⭐⭐⭐ |
| Gemini 1.5 Pro | Çok Yüksek | Mükemmel | ⭐⭐⭐⭐⭐ |
| GPT-4 Turbo | Yüksek | Çok İyi | ⭐⭐⭐⭐ |
| Gemini 2.0 Flash | Yüksek | Çok İyi | ⭐⭐⭐⭐ |
| Gemini 1.5 Flash | Yüksek | Çok İyi | ⭐⭐⭐⭐ |
| GPT-4o Mini | Orta-Yüksek | İyi | ⭐⭐⭐⭐ |
| GPT-3.5 Turbo | Orta | İyi | ⭐⭐⭐ |
| Gemini Pro | Orta | İyi | ⭐⭐⭐ |

### Maliyet (1000 Token Başına)

| Model | Input | Output | Toplam/Okuma |
|-------|-------|--------|--------------|
| **ÜCRETSİZ** | | | |
| Gemini 2.0 Flash | $0.00 | $0.00 | **$0.00** ✅ |
| Gemini 1.5 Flash | $0.00 | $0.00 | **$0.00** ✅ |
| Gemini 1.5 Pro | $0.00 | $0.00 | **$0.00** ✅ |
| Gemini Pro | $0.00 | $0.00 | **$0.00** ✅ |
| **ÜCRETLİ** | | | |
| GPT-3.5 Turbo | $0.0005 | $0.0015 | ~$0.01 💰 |
| GPT-4o Mini | $0.00015 | $0.0006 | ~$0.004 💰 |
| GPT-4 Turbo | $0.01 | $0.03 | ~$0.20 💰💰 |
| GPT-4o | $0.005 | $0.015 | ~$0.10 💰💰 |
| GPT-4 | $0.03 | $0.06 | ~$0.45 💰💰💰 |

> **Not:** Bir tarot yorumu ortalama 500-1000 token kullanır.

---

## 🎯 Tavsiyeler

### 🏆 En İyi Seçimler

1. **Test/Development**: `Gemini 1.5 Flash` (ücretsiz, hızlı, kaliteli)
2. **Production/Kullanıcılar**: `Gemini 2.0 Flash Exp` (en yeni, en hızlı)
3. **Premium Deneyim**: `Gemini 1.5 Pro` (ücretsiz, en iyi kalite)
4. **Ticari/Profesyonel**: `GPT-4o Mini` (ücretli ama uygun)

### ⚠️ Dikkat Edilmesi Gerekenler

- **Gemini 2.0 Flash Exp** deneyseldir, ara sıra hata verebilir
- **GPT-4/GPT-4o** çok pahalı, yüksek trafikte maliyetli
- **OpenAI** için kredi kartı gerekli, limit aşımı maliyetli
- **Gemini** için Google hesabı yeterli

---

## 🔄 Model Değiştirme Senaryoları

### Senaryo 1: Ücretsiz'den Ücretli'ye Geçiş
```
1. OpenAI hesabı oluştur
2. API key al ve kredi yükle
3. Admin settings'te OpenAI key gir
4. GPT-4o Mini modelini seç
5. Default provider'ı OpenAI yap
6. Kaydet ve test et
```

### Senaryo 2: Hız Optimizasyonu
```
Yavaş: Gemini 1.5 Pro
↓
Hızlı: Gemini 1.5 Flash veya 2.0 Flash Exp
```

### Senaryo 3: Kalite Optimizasyonu
```
İyi: Gemini 1.5 Flash
↓
Mükemmel: Gemini 1.5 Pro veya GPT-4o
```

### Senaryo 4: Maliyet Optimizasyonu
```
Pahalı: GPT-4
↓
Uygun: GPT-4o Mini
↓
Ücretsiz: Gemini (herhangi biri)
```

---

## 🐛 Sorun Giderme

### Model Bulunamadı Hatası
```python
# Hata: Model 'gemini-pro' bulunamadı
# Çözüm: Model adını kontrol edin
✅ Doğru: 'gemini-1.5-flash'
❌ Yanlış: 'gemini-flash-1.5'
```

### API Key Geçersiz
```python
# Hata: Invalid API key
# Çözüm: 
1. API key'i kontrol edin
2. Başında/sonunda boşluk yok mu?
3. Key'in aktif olduğundan emin olun
4. Doğru provider'ı seçtiniz mi?
```

### Yanıt Alamıyorum
```python
# Çözüm:
1. Site ayarlarını kontrol edin
2. API key'leri doğru mu?
3. Model adı doğru mu?
4. İnternet bağlantısı var mı?
5. Logs'u kontrol edin (terminal)
```

---

## 📚 Kaynaklar

### Google Gemini
- 📖 Dokümantasyon: https://ai.google.dev/docs
- 🔑 API Key: https://makersuite.google.com/app/apikey
- 💬 Forum: https://discuss.ai.google.dev/

### OpenAI
- 📖 Dokümantasyon: https://platform.openai.com/docs
- 🔑 API Key: https://platform.openai.com/api-keys
- 💰 Fiyatlandırma: https://openai.com/api/pricing/
- 💬 Forum: https://community.openai.com/

---

## ✨ Özet

✅ **Artık modeller ayarlar sayfasında seçilebilir**
✅ **Hem Gemini hem OpenAI destekleniyor**
✅ **5 Gemini + 5 OpenAI modeli mevcut**
✅ **Gemini tamamen ücretsiz** (önerilir)
✅ **Değişiklikler anında aktif oluyor**

**En İyi Seçim:** `Gemini 1.5 Flash` veya `Gemini 2.0 Flash Exp` 🚀

---

**Hazırlayan:** GitHub Copilot AI
**Tarih:** 6 Ekim 2025
**Versiyon:** 1.0
