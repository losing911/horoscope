# 🎴 Tarot Yorum - AI Destekli Tarot Platformu

Modern, AI destekli tarot falı ve astroloji platformu. Google Gemini ve OpenAI entegrasyonlu.

## ✨ Özellikler

### 🎯 Kullanıcı Özellikleri
- ✅ **Rastgele Kart Çekimi**: Mistik deneyim için kartlar otomatik çekilir
- ✅ **AI Yorumlama**: Google Gemini veya OpenAI ile detaylı yorumlar
- ✅ **Çoklu Yayılımlar**: Farklı türde tarot yayılımları
- ✅ **Günlük Kart**: Her gün özel bir kart ve yorum
- ✅ **Okuma Geçmişi**: Tüm okumalarınızı saklayın
- ✅ **Modern Tasarım**: Responsive ve animasyonlu arayüz

### 🔧 Admin Özellikleri
- 📊 **Dashboard**: Detaylı istatistikler ve grafikler
- 👥 **Kullanıcı Yönetimi**: Kullanıcıları görüntüle ve yönet
- 🎴 **Okuma Yönetimi**: Tüm okumaları takip et
- 📈 **İstatistikler**: Dönemsel analiz ve grafikler
- ⚙️ **Site Ayarları**: AI, limitler ve genel ayarlar

### 🎨 Tasarım Özellikleri
- 🌈 Modern gradient tasarım
- 🎭 Glassmorphism efektleri
- 📱 Tam responsive (mobil/tablet/desktop)
- ✨ Smooth animasyonlar
- 🎯 Google AdSense reklam alanları

## 🚀 Kurulum

### 1. Gereksinimleri Yükleyin
```bash
pip install -r requirements.txt
```

### 2. Veritabanını Hazırlayın
```bash
python manage.py migrate
python manage.py populate_initial_data  # Tarot kartlarını yükle
```

### 3. Superuser Oluşturun
```bash
python manage.py createsuperuser
```

### 4. Sunucuyu Başlatın
```bash
python manage.py runserver
```

## ⚙️ Yapılandırma

### 1. Site Ayarlarını Yapın
1. Admin panele giriş yapın: http://127.0.0.1:8000/django-admin/
2. "Site Ayarları" bölümüne gidin
3. Ayarları yapın

### 2. Google Gemini API Key Ekleyin
1. [Google AI Studio](https://makersuite.google.com/app/apikey) adresinden ücretsiz API key alın
2. Admin Dashboard'a gidin: http://127.0.0.1:8000/admin/settings/
3. "Gemini API Key" alanına key'inizi yapıştırın
4. "Varsayılan AI Sağlayıcı" olarak "gemini" seçin
5. Kaydedin

### 3. (Opsiyonel) OpenAI API Key
1. [OpenAI Platform](https://platform.openai.com/api-keys) adresinden key alın
2. Admin settings'e ekleyin

## 📁 Proje Yapısı

```
djtarot/
├── accounts/           # Kullanıcı yönetimi
├── tarot/             # Ana tarot uygulaması
│   ├── admin_views.py # Admin panel view'ları
│   ├── services.py    # AI servis entegrasyonu
│   ├── models.py      # Veritabanı modelleri
│   ├── views.py       # Kullanıcı view'ları
│   └── templates/     # Template dosyaları
│       ├── tarot/     # Kullanıcı templates
│       └── admin/     # Admin templates
├── static/            # CSS, JS, görseller
└── templates/         # Base templates
```

## 🔗 URL Yapısı

### Kullanıcı Paneli
- **Ana Sayfa**: http://127.0.0.1:8000/
- **Yayılımlar**: http://127.0.0.1:8000/spreads/
- **Günlük Kart**: http://127.0.0.1:8000/daily-card/
- **Okumalarım**: http://127.0.0.1:8000/my-readings/

### Admin Paneli (Staff Gerekli)
- **Dashboard**: http://127.0.0.1:8000/admin/dashboard/
- **Kullanıcılar**: http://127.0.0.1:8000/admin/users/
- **Okumalar**: http://127.0.0.1:8000/admin/readings/
- **İstatistikler**: http://127.0.0.1:8000/admin/statistics/
- **Ayarlar**: http://127.0.0.1:8000/admin/settings/

### Django Admin
- **Yönetim Paneli**: http://127.0.0.1:8000/django-admin/

## 🛠️ Teknolojiler

### Backend
- **Django 5.0.2** - Web framework
- **Python 3.10+** - Programlama dili
- **SQLite** - Veritabanı

### AI Entegrasyonu
- **Google Gemini API** - AI yorumlama
- **OpenAI GPT** - Alternatif AI yorumlama

### Frontend
- **Bootstrap 5.3** - CSS framework
- **Font Awesome 6** - İkonlar
- **Chart.js** - Grafikler
- **Google Fonts** - Poppins font

## 🎯 Önemli Notlar

### Test Aşaması Özellikleri
- ❌ **Günlük okuma sınırı devre dışı** (Unlimited okuma)
- ✅ **Kart seçimi tamamen rastgele** (Manuel seçim yok)

### Üretim İçin
1. `settings.py`'de `DEBUG = False` yapın
2. `ALLOWED_HOSTS` ayarlayın
3. Güvenli `SECRET_KEY` kullanın
4. PostgreSQL/MySQL gibi production DB kullanın
5. Günlük okuma sınırını aktif edin (views.py'de yorumları kaldırın)

### Google AdSense
- Template'lerde placeholder'lar hazır
- Gerçek AdSense kodlarınızı ekleyin:
  - `index.html`
  - `spread_detail.html`
  - Diğer sayfalara

## 📝 Lisans

Bu proje özel bir proje olup, ticari kullanım için izin gereklidir.

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing`)
3. Değişikliklerinizi commit edin
4. Branch'inizi push edin
5. Pull Request açın

## 📧 İletişim

Sorularınız için: info@tarotyorum.com

---

**Not**: API key'lerinizi asla Git'e commit etmeyin! `.env` dosyası kullanın.

## 🎉 Teşekkürler

Bu projeyi kullandığınız için teşekkür ederiz! 🙏

**Geliştirici**: GitHub Copilot & AI Team
**Versiyon**: 1.0.0
**Tarih**: Ekim 2025
