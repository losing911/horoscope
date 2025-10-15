# 🚀 Sıfırdan DigitalOcean Django Kurulumu

## Yeni Droplet için Eksiksiz Kurulum Rehberi

---

## 📋 1. YENİ DROPLET OLUŞTUR

### DigitalOcean Dashboard:

1. **Create** → **Droplets**
2. **Choose Region:** Frankfurt (yakın, hızlı)
3. **Choose Image:** 
   - ✅ **Ubuntu 22.04 LTS x64** (önerilen)
4. **Choose Size:**
   - ✅ **Basic** → **Regular** → **$6/mo** (1GB RAM, 1 vCPU, 25GB SSD)
   - Veya **$12/mo** (2GB RAM) - daha iyi performans
5. **Authentication:**
   - ✅ **SSH Key** (güvenli) veya **Password**
6. **Hostname:** `horoscope-prod`
7. **Create Droplet**

**NOT:** IP adresini kaydet: `165.232.XXX.XXX`

---

## 🔐 2. İLK BAĞLANTI VE GÜVENLİK

### SSH Bağlantısı

```bash
# Windows PowerShell veya CMD
ssh root@165.232.XXX.XXX

# İlk girişte "yes" yaz
```

### Root Şifresini Değiştir

```bash
passwd
# Yeni şifre gir (güçlü olsun!)
```

### Sistem Güncellemeleri

```bash
# Tüm paketleri güncelle
apt update && apt upgrade -y

# Gerekli araçları kur
apt install -y curl wget git nano htop ufw
```

### Yeni Kullanıcı Oluştur (Güvenlik)

```bash
# Django kullanıcısı oluştur
adduser django
# Şifre gir

# Sudo yetkisi ver
usermod -aG sudo django

# SSH erişimi ver
rsync --archive --chown=django:django ~/.ssh /home/django
```

### Firewall Ayarları

```bash
# UFW kur ve yapılandır
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 7080/tcp  # OpenLiteSpeed Admin (geçici)
ufw enable

# Kontrol
ufw status
```

---

## 🐍 3. PYTHON VE VIRTUAL ENVIRONMENT

```bash
# Django kullanıcısına geç
su - django

# Python 3.11 kur (en güncel)
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# pip güncelle
python3.11 -m pip install --upgrade pip

# Proje klasörü oluştur
mkdir -p ~/projects
cd ~/projects
```

---

## 🗄️ 4. POSTGRESQL KURULUMU

```bash
# PostgreSQL kur
sudo apt install -y postgresql postgresql-contrib

# PostgreSQL'e geç
sudo -u postgres psql

# Database ve kullanıcı oluştur (PostgreSQL içinde)
CREATE DATABASE horoscope_db;
CREATE USER horoscope_user WITH PASSWORD 'GucluSifre123!@#';

-- Türkçe karakter desteği
ALTER ROLE horoscope_user SET client_encoding TO 'utf8';
ALTER ROLE horoscope_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE horoscope_user SET timezone TO 'Europe/Istanbul';

-- Yetkileri ver
GRANT ALL PRIVILEGES ON DATABASE horoscope_db TO horoscope_user;

-- PostgreSQL 15+ için ek yetki
\c horoscope_db
GRANT ALL ON SCHEMA public TO horoscope_user;

-- Çık
\q
```

### PostgreSQL Bağlantı Testi

```bash
# Test et
psql -h localhost -U horoscope_user -d horoscope_db
# Şifre: GucluSifre123!@#
# \q ile çık
```

---

## 📦 5. PROJEYI YÜKLEYİN

### GitHub'dan Clone

```bash
cd ~/projects

# Projeyi clone et
git clone https://github.com/losing911/horoscope.git
cd horoscope

# Kontrol
ls -la
```

### Virtual Environment Oluştur

```bash
# venv oluştur
python3.11 -m venv venv

# Aktif et
source venv/bin/activate

# Pip güncelle
pip install --upgrade pip

# Requirements kur
pip install -r requirements.txt

# Eksik paketler (production için)
pip install gunicorn psycopg2-binary python-decouple
```

---

## ⚙️ 6. DJANGO AYARLARI

### .env Dosyası Oluştur

```bash
cd ~/projects/horoscope

# .env dosyası oluştur
nano .env
```

**İçerik (kendi bilgilerinle değiştir):**

```env
# Django Settings
DEBUG=False
SECRET_KEY=super-gizli-secret-key-min-50-karakter-olsun-buraya-rastgele-string-yaz
ALLOWED_HOSTS=165.232.XXX.XXX,tarot-yorum.fun,www.tarot-yorum.fun

# Database
DB_ENGINE=postgresql
DB_NAME=horoscope_db
DB_USER=horoscope_user
DB_PASSWORD=GucluSifre123!@#
DB_HOST=localhost
DB_PORT=5432

# AI Keys
OPENAI_API_KEY=sk-proj-your-openai-key-here
GEMINI_API_KEY=your-gemini-key-here
DEFAULT_AI_PROVIDER=gemini

# Email (opsiyonel)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

Kaydet: `Ctrl+X`, `Y`, `Enter`

### settings.py'yi Kontrol Et

```bash
nano tarot_project/settings.py
```

**Bu ayarların olduğundan emin ol:**

```python
import os
from pathlib import Path
from decouple import config

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Static files (production)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Security Settings (production)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
```

Kaydet.

---

## 🔧 7. DJANGO KOMUTLARI

```bash
cd ~/projects/horoscope
source venv/bin/activate

# Logs klasörü oluştur
mkdir -p logs

# Migrations
python manage.py makemigrations
python manage.py migrate

# Static files topla
python manage.py collectstatic --noinput

# Superuser oluştur
python manage.py createsuperuser
# Kullanıcı adı: admin
# Email: admin@tarot.com
# Şifre: (güçlü şifre)

# Initial data (tarot kartları, burçlar)
python manage.py populate_initial_data
```

### Django Test Et

```bash
# Development server başlat
python manage.py runserver 0.0.0.0:8000
```

**Başka terminal'den test et:**

```bash
curl http://localhost:8000
```

HTML geliyorsa ✅ Django çalışıyor!

`Ctrl+C` ile durdur.

---

## 🚀 8. GUNICORN KURULUMU

### Gunicorn Systemd Service

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

**İçerik:**

```ini
[Unit]
Description=Gunicorn daemon for Django Horoscope
After=network.target

[Service]
User=django
Group=www-data
WorkingDirectory=/home/django/projects/horoscope
Environment="PATH=/home/django/projects/horoscope/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=tarot_project.settings"

ExecStart=/home/django/projects/horoscope/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/home/django/projects/horoscope/gunicorn.sock \
          --timeout 120 \
          --access-logfile /home/django/projects/horoscope/logs/gunicorn_access.log \
          --error-logfile /home/django/projects/horoscope/logs/gunicorn_error.log \
          tarot_project.wsgi:application

Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

Kaydet.

### Gunicorn'u Başlat

```bash
# Servisi başlat
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn

# Kontrol et
sudo systemctl status gunicorn

# Socket oluştu mu?
ls -la /home/django/projects/horoscope/gunicorn.sock
```

✅ **Active (running)** görmelisin!

---

## 🌐 9. NGINX KURULUMU (OpenLiteSpeed Yerine)

Nginx daha stabil ve yaygın. Bunu kullanacağız:

### Nginx Kur

```bash
sudo apt install -y nginx
```

### Nginx Config Oluştur

```bash
sudo nano /etc/nginx/sites-available/horoscope
```

**İçerik (DİKKAT: ```nginx ve ``` satırlarını KOPYALAMA!):**

```
upstream django {
    server unix:/home/django/projects/horoscope/gunicorn.sock;
}

server {
    listen 80;
    server_name 159.89.108.100 tarot-yorum.fun www.tarot-yorum.fun;

    client_max_body_size 10M;

    # Logs
    access_log /home/django/projects/horoscope/logs/nginx_access.log;
    error_log /home/django/projects/horoscope/logs/nginx_error.log;

    # Static files
    location /static/ {
        alias /home/django/projects/horoscope/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /home/django/projects/horoscope/media/;
        expires 7d;
    }

    # Django
    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

Kaydet.

### Nginx'i Aktif Et

```bash
# Symlink oluştur
sudo ln -s /etc/nginx/sites-available/horoscope /etc/nginx/sites-enabled/

# Default site'ı kaldır
sudo rm /etc/nginx/sites-enabled/default

# Test et
sudo nginx -t

# Başlat
sudo systemctl restart nginx
sudo systemctl enable nginx

# Kontrol
sudo systemctl status nginx
```

### İzinleri Düzelt

```bash
# Django kullanıcısına www-data grubu ekle
sudo usermod -aG www-data django

# Dosya izinleri
sudo chown -R django:www-data /home/django/projects/horoscope
sudo chmod -R 755 /home/django/projects/horoscope

# Socket'e erişim
sudo chmod 660 /home/django/projects/horoscope/gunicorn.sock
```

---

## 🧪 10. TEST ET

### Tarayıcıdan Aç

```
http://165.232.XXX.XXX
```

✅ **Ana sayfa görünüyor!**

### Admin Panel

```
http://165.232.XXX.XXX/admin
```

Giriş yap: `admin` / `şifreniz`

---

## 🔒 11. SSL SERTİFİKASI (Let's Encrypt)

### Domain'i DNS'e Ekle

**Cloudflare/Domain Provider:**

```
A Record: tarot-yorum.fun → 165.232.XXX.XXX
A Record: www.tarot-yorum.fun → 165.232.XXX.XXX
```

DNS yayılması için 5-10 dakika bekle.

### Certbot Kur

```bash
# Certbot kur
sudo apt install -y certbot python3-certbot-nginx

# SSL sertifikası al
sudo certbot --nginx -d tarot-yorum.fun -d www.tarot-yorum.fun

# Email gir
# Terms: Yes (Y)
# Share email: No (N)
# Redirect HTTP to HTTPS: Yes (2)
```

### Otomatik Yenileme

```bash
# Test et
sudo certbot renew --dry-run

# Cron job (otomatik)
sudo crontab -e

# Ekle:
30 2 * * * certbot renew --quiet
```

---

## 🎨 12. SON ADIMLAR

### Initial Blog Posts Üret

```bash
cd ~/projects/horoscope
source venv/bin/activate

# Blog kategorileri oluştur (admin'den)
# Sonra:
python manage.py generate_blog_posts --count 5 --publish
```

### Günlük Burç Yorumları

```bash
# Manuel
python manage.py batch_generate_horoscopes

# Otomatik (cron)
crontab -e

# Ekle:
0 6 * * * cd /home/django/projects/horoscope && /home/django/projects/horoscope/venv/bin/python manage.py batch_generate_horoscopes
```

### Yedekleme Script

```bash
nano ~/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/home/django/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Database backup
PGPASSWORD="GucluSifre123!@#" pg_dump -h localhost -U horoscope_user -d horoscope_db > $BACKUP_DIR/db_$DATE.sql

# Media backup
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /home/django/projects/horoscope/media

# Eski backupları sil (30 gün)
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $DATE"
```

```bash
chmod +x ~/backup.sh

# Cron (her gün 3:00)
crontab -e

0 3 * * * /home/django/backup.sh >> /home/django/backup.log 2>&1
```

---

## ✅ KURULUM TAMAMLANDI!

### 🎉 Test Etme:

1. ✅ Ana Sayfa: https://tarot-yorum.fun
2. ✅ Admin: https://tarot-yorum.fun/admin
3. ✅ Blog: https://tarot-yorum.fun/blog
4. ✅ Burçlar: https://tarot-yorum.fun/zodiac

### 📊 Performans İzleme:

```bash
# Gunicorn log
tail -f ~/projects/horoscope/logs/gunicorn_error.log

# Nginx log
sudo tail -f /var/log/nginx/error.log

# Django log
tail -f ~/projects/horoscope/logs/django_errors.log

# System resources
htop
```

### 🔄 Güncelleme:

```bash
cd ~/projects/horoscope
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

---

## 🐛 Troubleshooting

### 502 Bad Gateway

```bash
# Gunicorn çalışıyor mu?
sudo systemctl status gunicorn

# Restart
sudo systemctl restart gunicorn

# Log kontrol
tail -50 ~/projects/horoscope/logs/gunicorn_error.log
```

### Static Files Yüklenmiyor

```bash
# Yeniden topla
python manage.py collectstatic --clear --noinput

# İzinler
sudo chmod -R 755 ~/projects/horoscope/staticfiles
```

### Database Connection Error

```bash
# PostgreSQL çalışıyor mu?
sudo systemctl status postgresql

# .env kontrol
cat ~/projects/horoscope/.env | grep DB_
```

---

## 📞 Yardım

**Log Konumları:**
- Django: `~/projects/horoscope/logs/django_errors.log`
- Gunicorn: `~/projects/horoscope/logs/gunicorn_error.log`
- Nginx: `/var/log/nginx/error.log`
- PostgreSQL: `/var/log/postgresql/postgresql-14-main.log`

**Servisler:**
```bash
sudo systemctl status gunicorn
sudo systemctl status nginx
sudo systemctl status postgresql
```

---

## 🎯 Özet Komutlar (Tek Seferde)

```bash
# 1. Sistem güncelle
apt update && apt upgrade -y && apt install -y curl wget git nano htop ufw

# 2. Firewall
ufw allow OpenSSH && ufw allow 80/tcp && ufw allow 443/tcp && ufw enable

# 3. Python
apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# 4. PostgreSQL
apt install -y postgresql postgresql-contrib nginx

# 5. Kullanıcı
adduser django && usermod -aG sudo django

# 6. Proje
su - django
cd ~/projects
git clone https://github.com/losing911/horoscope.git
cd horoscope
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn psycopg2-binary python-decouple

# 7. Database oluştur (PostgreSQL içinde)
sudo -u postgres psql
CREATE DATABASE horoscope_db;
CREATE USER horoscope_user WITH PASSWORD 'GucluSifre123!@#';
GRANT ALL PRIVILEGES ON DATABASE horoscope_db TO horoscope_user;
\q

# 8. .env oluştur (yukarıdaki template'i kullan)

# 9. Django migrate
mkdir logs
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
python manage.py populate_initial_data

# 10. Gunicorn service (yukarıdaki template'i kullan)

# 11. Nginx config (yukarıdaki template'i kullan)

# 12. SSL
sudo certbot --nginx -d tarot-yorum.fun -d www.tarot-yorum.fun
```

---

**🚀 Başarılar! Sorularını sor, yardımcı olayım!**
