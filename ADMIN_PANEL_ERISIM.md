# 🔧 Admin Panel Erişim Bilgileri

## URL Yapısı

Django Tarot projemizde **iki farklı admin paneli** bulunmaktadır:

### 1. 📊 Custom Dashboard (Özel Yönetim Paneli)
**Ana URL**: http://127.0.0.1:8000/dashboard/

**Alt Sayfalar**:
- 📈 Dashboard: `/dashboard/` - Genel istatistikler
- 👥 Kullanıcılar: `/dashboard/users/` - Kullanıcı yönetimi
- 📖 Okumalar: `/dashboard/readings/` - Tarot okumaları
- ⚙️ Ayarlar: `/dashboard/settings/` - Site ayarları
- 📊 İstatistikler: `/dashboard/statistics/` - Detaylı raporlar

**Özellikler**:
- Modern, özel tasarım
- Tarot'a özel istatistikler
- Kullanıcı dostu arayüz
- Hızlı işlemler

### 2. 🗄️ Django Admin (Sistem Yönetimi)
**Ana URL**: http://127.0.0.1:8000/admin/

**Modül Yapısı**:

#### Tarot Uygulaması
- `tarot/sitesettings/` - Site ayarları (API keys, limitler)
- `tarot/aiprovider/` - AI sağlayıcı yapılandırmaları
- `tarot/tarotcard/` - Tarot kartları
- `tarot/tarotspread/` - Yayılımlar
- `tarot/tarotreading/` - Okumalar
- `tarot/dailycard/` - Günlük kartlar

#### Zodiac Uygulaması
- `zodiac/zodiacsign/` - Burç bilgileri
- `zodiac/dailyhoroscope/` - Günlük yorumlar
- `zodiac/weeklyhoroscope/` - Haftalık yorumlar
- `zodiac/monthlyhoroscope/` - Aylık yorumlar
- `zodiac/compatibilityreading/` - Uyum analizleri
- `zodiac/birthchart/` - Doğum haritaları
- `zodiac/moonsign/` - Ay burcu hesaplamaları
- `zodiac/ascendant/` - Yükselen burç
- `zodiac/personalhoroscope/` - Kişisel profiller

#### Kullanıcı Yönetimi
- `accounts/user/` - Kullanıcı hesapları
- `auth/group/` - Kullanıcı grupları

**Özellikler**:
- Django'nun güçlü admin arayüzü
- Veritabanı seviyesi erişim
- Batch işlemler
- Gelişmiş filtreleme ve arama

## Menü Yapısı

### Navbar → Yönetim Dropdown:

```
Yönetim ▼
  ├─ Dashboard (Custom Panel)
  │
  ├─ ─────────────────────
  │  Site Yönetimi
  │
  ├─ 🎛️ Site Ayarları       → /admin/tarot/sitesettings/
  ├─ 🧠 AI Sağlayıcılar      → /admin/tarot/aiprovider/
  │
  ├─ ─────────────────────
  │  Tam Yönetim
  │
  └─ 🗄️ Django Admin        → /admin/
```

## ❌ Yanlış URL'ler (404 Hataları)

### YANLIŞ:
```
❌ /admin/settings/          → 404 hatası
❌ /dashboard/admin/         → 404 hatası
❌ /admin/config/            → 404 hatası
```

### DOĞRU:
```
✅ /dashboard/settings/               → Custom dashboard ayarları
✅ /admin/tarot/sitesettings/         → Django admin site ayarları
✅ /admin/tarot/aiprovider/           → AI sağlayıcı yönetimi
```

## 🔑 Erişim Yetkileri

### Custom Dashboard (/dashboard/):
- `@login_required` - Giriş yapılmış olmalı
- `@user_passes_test(is_staff)` - Staff yetkisi gerekli
- `user.is_staff = True` olmalı

### Django Admin (/admin/):
- `user.is_staff = True` olmalı
- Superuser için: `user.is_superuser = True`

## 🚀 Hızlı Erişim Komutları

### Superuser Oluşturma:
```bash
python manage.py createsuperuser
```

### Staff Kullanıcı Yapma (Django Shell):
```python
python manage.py shell

from accounts.models import User
user = User.objects.get(username='kullaniciadi')
user.is_staff = True
user.save()
```

### Site Ayarları Kontrolü:
```python
from tarot.models import SiteSettings
settings = SiteSettings.load()
print(f"Site: {settings.site_title}")
print(f"AI: {settings.default_ai_provider}")
```

## 📝 Örnek Kullanım Senaryoları

### Senaryo 1: API Key Güncelleme
1. Giriş yap: http://127.0.0.1:8000/admin/
2. Git: **Tarot** → **Site Settings**
3. Güncelle: `gemini_api_key` veya `openai_api_key`
4. Kaydet

### Senaryo 2: Günlük Okuma Limiti Değiştirme
**Yöntem 1** (Custom Dashboard):
1. http://127.0.0.1:8000/dashboard/settings/
2. `daily_reading_limit` değiştir
3. Kaydet

**Yöntem 2** (Django Admin):
1. http://127.0.0.1:8000/admin/tarot/sitesettings/
2. İlk kayıt üzerinde değişiklik yap
3. Kaydet

### Senaryo 3: Kullanıcı İstatistikleri
1. http://127.0.0.1:8000/dashboard/
2. Grafikleri ve istatistikleri görüntüle

### Senaryo 4: Burç Yorumu Elle Düzenleme
1. http://127.0.0.1:8000/admin/zodiac/dailyhoroscope/
2. Günlük yorumu bul
3. İçeriği düzenle veya yeni ekle

## 🎨 Frontend Erişim

Template'lerde doğru URL kullanımı:

```django
<!-- Custom Dashboard -->
<a href="{% url 'tarot:admin_dashboard' %}">Dashboard</a>
<a href="{% url 'tarot:admin_settings' %}">Ayarlar</a>

<!-- Django Admin -->
<a href="/admin/">Django Admin</a>
<a href="/admin/tarot/sitesettings/">Site Ayarları</a>
<a href="/admin/zodiac/dailyhoroscope/">Günlük Yorumlar</a>
```

## 🔍 Sorun Giderme

### Sorun: "Page not found (404)" /admin/settings/
**Çözüm**: 
- Custom dashboard için: `/dashboard/settings/` kullanın
- Django admin için: `/admin/tarot/sitesettings/` kullanın

### Sorun: Permission Denied
**Çözüm**:
```python
# Kullanıcıya yetki ver
user = User.objects.get(username='kullaniciadi')
user.is_staff = True
user.save()
```

### Sorun: SiteSettings objesi yok
**Çözüm**:
```python
python manage.py shell
from tarot.models import SiteSettings
settings = SiteSettings.load()  # Otomatik oluşturur
```

## 📚 İlgili Dosyalar

- **Views**: `tarot/admin_views.py`
- **URLs**: `tarot/urls.py` (dashboard/* patterns)
- **Templates**: `tarot/templates/admin/*.html`
- **Models**: `tarot/models.py` (SiteSettings, AIProvider)

---

**Son Güncelleme**: 6 Ekim 2025
**Proje**: Django Tarot - Burç ve Tarot Okuma Platformu
