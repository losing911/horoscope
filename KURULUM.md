# 🔮 Django Tarot Sistemi - Kurulum Rehberi

## ✨ Yeni Eklenen Özellikler

### 1. 🤖 AI Yorumlama Sistemi
Sistemimiz artık **gerçek AI** kullanarak tarot yorumları yapıyor!

**Desteklenen AI Sağlayıcıları:**
- ✅ **OpenAI GPT** (GPT-3.5-turbo, GPT-4)
- ✅ **Google Gemini** (Gemini-Pro)

**AI Servisleri:**
- `AIService`: Tarot okumalarının AI ile yorumlanması
- `DailyCardService`: Günlük kartlar için özel yorumlar

### 2. 🃏 Manuel Kart Seçimi
Kullanıcılar artık kartları iki şekilde seçebilir:
- **Otomatik:** Rastgele kart çekimi (varsayılan)
- **Manuel:** Kartları kendileri seçebilirler

**Manuel Seçim Özellikleri:**
- Toggle switch ile kolay geçiş
- Görsel kart grid'i
- Seçili kartların vurgulanması
- Gereken kart sayısı kontrolü

### 3. 🖼️ Tarot Kartı Görselleri
Her tarot kartı için görsel desteği:
- `image` field: Yerel görsel yükleme
- `image_url` field: URL'den görsel gösterme
- Fallback: Görsel yoksa gradient arka plan

## 🚀 Kurulum

### 1. Gereksinimler
```bash
Python 3.10+
Django 5.0.2
OpenAI API veya Google Gemini API key
```

### 2. Bağımlılıkları Yükle
```bash
cd C:\xampp\htdocs\djtarot
pip install -r requirements.txt
```

### 3. Veritabanı Hazırla
```bash
python manage.py migrate
python manage.py populate_initial_data
```

### 4. Admin Kullanıcısı Oluştur
```bash
python manage.py createsuperuser
# Kullanıcı: admin
# Şifre: 123
```

### 5. AI API Anahtarlarını Ayarla

**Yöntem 1: Admin Panel (Önerilen)**
1. http://127.0.0.1:8000/admin/ adresine giriş yap
2. **AI Sağlayıcılar** bölümüne git
3. OpenAI veya Gemini'yi seç
4. API Key'ini gir ve kaydet

**Yöntem 2: .env Dosyası**
```env
OPENAI_API_KEY=sk-your-openai-key-here
GEMINI_API_KEY=your-gemini-key-here
```

### 6. Sunucuyu Başlat
```bash
python manage.py runserver
```

## 📝 Kullanım

### AI Yorumlar Nasıl Çalışır?

1. **Kullanıcı bir fal çeker:**
   - Spread seçer (Tek Kart, Üç Kart, vb.)
   - Sorusunu yazar
   - Kartları çeker (otomatik veya manuel)

2. **AIService devreye girer:**
   ```python
   ai_service = AIService()  # Admin'den ayarlanan provider'ı kullanır
   interpretation = ai_service.generate_interpretation(
       question="Aşk hayatımda ne olacak?",
       cards=[...],  # Seçilen kartlar
       spread_name="Üç Kart Yayılımı"
   )
   ```

3. **AI detaylı yorum üretir:**
   - Her kartın pozisyonunu analiz eder
   - Kartlar arası bağlantıları yorumlar
   - Soruya özel cevap verir
   - Tavsiyeler sunar

### Manuel Kart Seçimi Kullanımı

1. Spread detay sayfasında **"Kartları Kendim Seçmek İstiyorum"** switch'ini aç
2. Kart grid'inden istediğin kartları seç (seçililer sarı border olur)
3. Gereken sayıda kart seçince buton aktif olur
4. **"Seçili Kartlarla Oku"** butonuna tıkla

## 🗂️ Dosya Yapısı

```
tarot/
├── services.py          # AI servis sınıfları
│   ├── AIService        # Genel tarot yorumları
│   └── DailyCardService # Günlük kart yorumları
├── views.py             # View fonksiyonları (AI entegre)
├── models.py            # TarotCard (image field'li)
└── templates/
    └── tarot/
        └── spread_detail.html  # Manuel seçim UI'ı
```

## ⚙️ Admin Panel Ayarları

### Site Ayarları
- **Varsayılan AI Sağlayıcı:** OpenAI veya Gemini seç
- **Günlük Okuma Limiti:** Kullanıcı başına limit
- **AI Yanıt Uzunluğu:** Max token sayısı

### AI Sağlayıcılar
- **OpenAI:**
  - Model: gpt-3.5-turbo (hızlı) veya gpt-4 (detaylı)
  - API Key: sk-...
  - Temperature: 0.7 (yaratıcılık)

- **Gemini:**
  - Model: gemini-pro
  - API Key: ...
  - Temperature: 0.7

### Tarot Kartları
- 78 kart tanımlı (22 Major Arcana + 56 Minor Arcana)
- Her kart için:
  - Düz anlam
  - Ters anlam
  - Açıklama
  - Görsel (opsiyonel)

## 🎨 Kart Görsellerini Ekleme

### Yöntem 1: Admin Panel
1. Admin > Tarot Kartları
2. Kartı seç
3. "Kart Görseli" alanından dosya yükle
4. Kaydet

### Yöntem 2: URL
1. Kartı seç
2. "Görsel URL" alanına resim linki yapıştır
3. Kaydet

### Örnek Görsel Kaynakları
- [Rider-Waite Deck](https://www.sacred-texts.com/tarot/pkt/)
- [Labyrinthos Tarot](https://labyrinthos.co/)

## 🔍 Test Etme

### AI Yorumları Test Et
```python
python manage.py shell

from tarot.services import AIService
from tarot.models import TarotCard

# AI servisini başlat
ai = AIService()

# Test kartları
cards = [
    {
        'card': TarotCard.objects.get(name="The Fool"),
        'position': 1,
        'is_reversed': False
    }
]

# Yorum üret
result = ai.generate_interpretation(
    question="Test sorusu",
    cards=cards,
    spread_name="Tek Kart"
)
print(result)
```

### Manuel Seçim Test Et
1. http://127.0.0.1:8000/spread/single-card/ 
2. "Kartları Kendim Seçmek İstiyorum" aç
3. Bir kart seç
4. Soruyu yaz ve gönder

## 📊 Özellik Durumu

| Özellik | Durum | Açıklama |
|---------|-------|----------|
| ✅ AI Yorumları | Tamamlandı | OpenAI + Gemini |
| ✅ Manuel Seçim | Tamamlandı | Toggle + Grid UI |
| ✅ Kart Görselleri | Destekleniyor | Image field mevcut |
| ⏳ Kart Detay Sayfaları | Planlandı | Sonraki adım |
| ⏳ Gelişmiş Filtreleme | Planlandı | Takım/tip bazlı |

## 🐛 Sorun Giderme

### AI Yorumu Gelmiyor
- Admin panelden API key'leri kontrol et
- AI Provider'ın "Aktif" olduğundan emin ol
- Console'da hata mesajlarını kontrol et

### Manuel Seçim Çalışmıyor
- JavaScript console'u kontrol et
- Gereken sayıda kart seçtiğinizden emin olun
- Sayfayı yenileyin

### Görsel Gösterilmiyor
- `MEDIA_ROOT` ve `MEDIA_URL` ayarlarını kontrol et
- Görsel dosyasının yüklendiğinden emin ol
- URL geçerliliğini kontrol et

## 🎯 Sonraki Adımlar

1. **Kart Detay Sayfaları**
   - Her kart için ayrı sayfa
   - Detaylı açıklamalar
   - İlişkili kartlar

2. **Kullanıcı Deneyimi**
   - Animasyonlu kart çekimi
   - Ses efektleri
   - Karanlık mod

3. **İleri Özellikler**
   - Okuma geçmişi analizi
   - Favori kartlar
   - Kart takvimi

## 📞 Destek

Sorularınız için:
- GitHub Issues
- admin@tarot-site.com

---

**🔮 Tarot sisteminiz artık tam fonksiyonel! Keyifli fallar! ✨**
