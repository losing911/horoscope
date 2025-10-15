# 🚀 DigitalOcean Production Deployment Rehberi

## Django + OpenLiteSpeed Droplet Kurulumu

Bu rehber, DigitalOcean'da Django + OpenLiteSpeed droplet üzerinde horoscope projesini production'a almak için gerekli tüm adımları içerir.

---

## 📋 İçindekiler

1. [Ön Hazırlık](#ön-hazırlık)
2. [Droplet Bağlantısı](#droplet-bağlantısı)
3. [Proje Dosyalarını Yükleme](#proje-dosyalarını-yükleme)
4. [Python Sanal Ortam](#python-sanal-ortam)
5. [Veritabanı Kurulumu](#veritabanı-kurulumu)
6. [Django Ayarları](#django-ayarları)
7. [OpenLiteSpeed Konfigürasyonu](#openlitespeed-konfigürasyonu)
8. [Static ve Media Files](#static-ve-media-files)
9. [SSL Sertifikası](#ssl-sertifikası)
10. [Güvenlik](#güvenlik)
11. [Performans Optimizasyonu](#performans-optimizasyonu)
12. [Yedekleme](#yedekleme)

---

## 1. Ön Hazırlık

### Gerekli Bilgiler
- ✅ Droplet IP adresi
- ✅ SSH root şifresi veya SSH key
- ✅ Domain adı (örn: horoscope.com)
- ✅ GitHub repository erişimi

### Yerel Bilgisayarınızda

```bash
# .env dosyası oluştur (production ayarları)
SECRET_KEY=your-very-secure-secret-key-here-min-50-char
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,your-droplet-ip

# Database (PostgreSQL)
DB_NAME=horoscope_db
DB_USER=horoscope_user
DB_PASSWORD=secure-database-password
DB_HOST=localhost
DB_PORT=5432

# AI Keys
OPENAI_API_KEY=your-openai-api-key
GEMINI_API_KEY=your-gemini-api-key
DEFAULT_AI_PROVIDER=gemini

# Email (opsiyonel)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

## 2. Droplet Bağlantısı

### SSH ile Bağlan

```bash
# Terminal'den bağlan
ssh root@your_droplet_ip

# İlk girişte şifre değiştir
passwd
```

### Güvenlik için Yeni Kullanıcı Oluştur

```bash
# Yeni kullanıcı oluştur
adduser django
usermod -aG sudo django

# SSH için yetki ver
rsync --archive --chown=django:django ~/.ssh /home/django

# Kullanıcıya geç
su - django
```

---

## 3. Proje Dosyalarını Yükleme

### GitHub'dan Clone

```bash
# Ana dizine git
cd /home/django

# Projeyi clone et
git clone https://github.com/losing911/horoscope.git djtarot
cd djtarot

# Doğru branch'i seç
git checkout main
```

### Alternatif: SCP ile Yükleme

```bash
# Yerel bilgisayardan dosyaları yükle
scp -r C:\xampp\htdocs\djtarot django@your_droplet_ip:/home/django/
```

---

## 4. Python Sanal Ortam

### Python ve Pip Kurulumu

```bash
# Python 3.10+ kurulu mu kontrol et
python3 --version

# Eğer yoksa kur
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-dev python3-pip -y

# pip güncelle
python3 -m pip install --upgrade pip
```

### Virtual Environment Oluştur

```bash
cd /home/django/djtarot

# Virtual environment oluştur
python3 -m venv venv

# Aktif et
source venv/bin/activate

# Gereksinimleri kur
pip install -r requirements.txt

# Gunicorn ekle (production server)
pip install gunicorn psycopg2-binary
```

### requirements.txt'ye Ekle

```bash
echo "gunicorn==21.2.0" >> requirements.txt
echo "psycopg2-binary==2.9.9" >> requirements.txt
pip freeze > requirements.txt
```

---

## 5. Veritabanı Kurulumu

### PostgreSQL Kurulumu

```bash
# PostgreSQL kur
sudo apt install postgresql postgresql-contrib -y

# PostgreSQL'e geç
sudo -u postgres psql

# Database ve kullanıcı oluştur
CREATE DATABASE horoscope_db;
CREATE USER horoscope_user WITH PASSWORD 'secure-database-password';

# Yetkileri ver
ALTER ROLE horoscope_user SET client_encoding TO 'utf8';
ALTER ROLE horoscope_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE horoscope_user SET timezone TO 'Europe/Istanbul';
GRANT ALL PRIVILEGES ON DATABASE horoscope_db TO horoscope_user;

# Çık
\q
```

### PostgreSQL Ayarları

```bash
# postgresql.conf düzenle
sudo nano /etc/postgresql/14/main/postgresql.conf

# Şu satırları bul ve değiştir:
shared_buffers = 256MB
effective_cache_size = 1GB
max_connections = 100
```

---

## 6. Django Ayarları

### .env Dosyası Oluştur

```bash
cd /home/django/djtarot

# .env dosyası oluştur
nano .env

# Yukarıdaki .env içeriğini yapıştır (Ctrl+X, Y, Enter)
```

### settings.py Güncellemeleri

`tarot_project/settings.py` dosyasını düzenle:

```python
# Production settings
import os
from pathlib import Path
from decouple import config

DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*').split(',')

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Database - PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='horoscope_db'),
        'USER': config('DB_USER', default='horoscope_user'),
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

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django_errors.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

### Django Komutları

```bash
# Virtual environment aktif
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

# Initial data (tarot kartları, burçlar)
python manage.py populate_initial_data
```

---

## 7. OpenLiteSpeed Konfigürasyonu

### OpenLiteSpeed Admin Panel

```
URL: https://your_droplet_ip:7080
Kullanıcı: admin
Şifre: /usr/local/lsws/admin/misc/admpass.sh ile değiştir
```

### Admin Şifresi Değiştir

```bash
sudo /usr/local/lsws/admin/misc/admpass.sh
```

### Virtual Host Ayarları

1. **Admin Panel'e Gir:** https://your_droplet_ip:7080

2. **Virtual Hosts → Example → General:**
   - Document Root: `/home/django/djtarot`
   - Domain Name: `your-domain.com, www.your-domain.com`

3. **Virtual Hosts → Example → Context:**
   
   **Static Context:**
   ```
   URI: /static/
   Location: /home/django/djtarot/staticfiles/
   Accessible: Yes
   ```
   
   **Media Context:**
   ```
   URI: /media/
   Location: /home/django/djtarot/media/
   Accessible: Yes
   ```
   
   **LSAPI Context:**
   ```
   URI: /
   Location: /home/django/djtarot/
   Command: /home/django/djtarot/venv/bin/python /home/django/djtarot/manage.py lsgi
   ```

4. **Graceful Restart:**
   - Actions → Graceful Restart

### LSGI Wrapper Script (Alternatif)

Eğer LSAPI çalışmazsa, Gunicorn ile:

```bash
# gunicorn.service oluştur
sudo nano /etc/systemd/system/gunicorn.service
```

İçeriği:

```ini
[Unit]
Description=Gunicorn daemon for Django Horoscope
After=network.target

[Service]
User=django
Group=www-data
WorkingDirectory=/home/django/djtarot
Environment="PATH=/home/django/djtarot/venv/bin"
ExecStart=/home/django/djtarot/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/home/django/djtarot/gunicorn.sock \
          tarot_project.wsgi:application

[Install]
WantedBy=multi-user.target
```

Aktif et:

```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn
```

### OpenLiteSpeed Proxy (Gunicorn için)

Admin Panel → Virtual Host → Context → Proxy Context:

```
URI: /
Web Server Address: unix:/home/django/djtarot/gunicorn.sock
```

---

## 8. Static ve Media Files

### Dosya İzinleri

```bash
# Django kullanıcısı sahipliği
sudo chown -R django:www-data /home/django/djtarot

# Static ve media izinleri
sudo chmod -R 755 /home/django/djtarot/staticfiles
sudo chmod -R 755 /home/django/djtarot/media

# Database izinleri (SQLite kullanıyorsanız)
sudo chmod 664 /home/django/djtarot/db.sqlite3
sudo chown django:www-data /home/django/djtarot/db.sqlite3
```

### Nginx Alternative (Opsiyonel)

Eğer OpenLiteSpeed yerine Nginx tercih ederseniz:

```bash
sudo apt install nginx -y

# Nginx config
sudo nano /etc/nginx/sites-available/horoscope
```

Config:

```nginx
upstream django {
    server unix:/home/django/djtarot/gunicorn.sock;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location /static/ {
        alias /home/django/djtarot/staticfiles/;
    }

    location /media/ {
        alias /home/django/djtarot/media/;
    }

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Aktif et:

```bash
sudo ln -s /etc/nginx/sites-available/horoscope /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 9. SSL Sertifikası

### Let's Encrypt (Certbot)

```bash
# Certbot kur
sudo apt install certbot python3-certbot-nginx -y

# OpenLiteSpeed için certbot
sudo certbot --webroot -w /home/django/djtarot/staticfiles \
  -d your-domain.com -d www.your-domain.com

# Otomatik yenileme
sudo certbot renew --dry-run

# Cron job ekle
sudo crontab -e

# Her gün 2:30'da kontrol et
30 2 * * * certbot renew --quiet
```

### OpenLiteSpeed SSL Ayarları

Admin Panel → Listeners → SSL:

```
Private Key File: /etc/letsencrypt/live/your-domain.com/privkey.pem
Certificate File: /etc/letsencrypt/live/your-domain.com/fullchain.pem
```

---

## 10. Güvenlik

### Firewall (UFW)

```bash
# UFW kur ve aktif et
sudo apt install ufw -y

# Gerekli portları aç
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw allow 7080/tcp    # OpenLiteSpeed Admin (geçici)

# Firewall'u aktif et
sudo ufw enable
sudo ufw status
```

### Fail2Ban

```bash
# Fail2ban kur
sudo apt install fail2ban -y

# SSH koruması
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local

# [sshd] bölümünü bul ve aktif et:
[sshd]
enabled = true
port = ssh
logpath = %(sshd_log)s
maxretry = 3
bantime = 3600

sudo systemctl restart fail2ban
```

### Django Security Checklist

```bash
# Production'da güvenlik kontrolü
python manage.py check --deploy
```

---

## 11. Performans Optimizasyonu

### Redis Cache (Opsiyonel ama Önerilen)

```bash
# Redis kur
sudo apt install redis-server -y

# Django'da redis paketi
pip install django-redis

# settings.py'ye ekle:
```

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

# Session'ları Redis'te sakla
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

### Database Connection Pooling

```bash
pip install django-db-geventpool
```

```python
# settings.py
DATABASES['default']['CONN_MAX_AGE'] = 600  # 10 dakika
```

### Gunicorn Workers

```bash
# CPU core sayısını öğren
nproc

# Gunicorn workers = (2 x CPU) + 1
# 2 core = 5 workers
# gunicorn.service'te güncelle:
--workers 5
```

---

## 12. Yedekleme

### Database Backup Script

```bash
# Backup scripti oluştur
nano /home/django/backup_db.sh
```

İçerik:

```bash
#!/bin/bash

# Backup klasörü
BACKUP_DIR="/home/django/backups"
mkdir -p $BACKUP_DIR

# Tarih
DATE=$(date +%Y%m%d_%H%M%S)

# PostgreSQL Backup
PGPASSWORD="secure-database-password" pg_dump \
  -h localhost \
  -U horoscope_user \
  -d horoscope_db \
  > $BACKUP_DIR/db_backup_$DATE.sql

# Media files backup
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz /home/django/djtarot/media

# Eski backup'ları temizle (30 gün öncesi)
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $DATE"
```

Çalıştırılabilir yap:

```bash
chmod +x /home/django/backup_db.sh

# Cron job ekle (her gün 3:00'de)
crontab -e

0 3 * * * /home/django/backup_db.sh >> /home/django/backup.log 2>&1
```

### Git Backup (Kod Yedekleme)

```bash
# Her değişiklikten sonra push et
git add .
git commit -m "Production update"
git push origin main
```

---

## 📊 Production Checklist

### ✅ Deployment Öncesi

- [ ] DEBUG=False
- [ ] SECRET_KEY değiştirildi
- [ ] ALLOWED_HOSTS ayarlandı
- [ ] PostgreSQL kuruldu
- [ ] .env dosyası oluşturuldu
- [ ] requirements.txt güncellendi

### ✅ Deployment

- [ ] Git'ten proje çekildi
- [ ] Virtual environment oluşturuldu
- [ ] Migrations uygulandı
- [ ] Static files toplandı
- [ ] Superuser oluşturuldu
- [ ] Initial data yüklendi

### ✅ Server Yapılandırması

- [ ] OpenLiteSpeed yapılandırıldı
- [ ] Gunicorn servisi aktif
- [ ] Static ve media erişimi çalışıyor
- [ ] Domain ayarlandı

### ✅ Güvenlik

- [ ] SSL sertifikası kuruldu
- [ ] Firewall aktif
- [ ] Fail2ban kuruldu
- [ ] Security checklist geçti

### ✅ Performans

- [ ] Redis cache kuruldu
- [ ] Database pooling aktif
- [ ] Gunicorn workers optimize edildi

### ✅ Bakım

- [ ] Backup scripti çalışıyor
- [ ] Cron job'lar kuruldu
- [ ] Monitoring aktif

---

## 🐛 Troubleshooting

### 502 Bad Gateway

```bash
# Gunicorn çalışıyor mu?
sudo systemctl status gunicorn

# Log kontrol
sudo journalctl -u gunicorn -n 50

# Restart
sudo systemctl restart gunicorn
```

### Static Files Yüklenmiyor

```bash
# Collectstatic tekrar çalıştır
python manage.py collectstatic --clear --noinput

# İzinleri kontrol et
sudo chown -R django:www-data /home/django/djtarot/staticfiles
sudo chmod -R 755 /home/django/djtarot/staticfiles
```

### Database Connection Error

```bash
# PostgreSQL çalışıyor mu?
sudo systemctl status postgresql

# Connection test
psql -h localhost -U horoscope_user -d horoscope_db

# .env dosyasını kontrol et
cat /home/django/djtarot/.env
```

### Permission Denied

```bash
# Tüm izinleri düzelt
sudo chown -R django:www-data /home/django/djtarot
sudo chmod -R 755 /home/django/djtarot
```

---

## 📞 Yardım ve Destek

**Logları İnceleme:**

```bash
# Django errors
tail -f /home/django/djtarot/logs/django_errors.log

# Gunicorn
sudo journalctl -u gunicorn -f

# OpenLiteSpeed
sudo tail -f /usr/local/lsws/logs/error.log

# PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

**Performans İzleme:**

```bash
# CPU ve RAM
htop

# Disk kullanımı
df -h

# Database boyutu
psql -U horoscope_user -d horoscope_db -c "SELECT pg_size_pretty(pg_database_size('horoscope_db'));"
```

---

## 🎉 Tamamlandı!

Projeniz artık production'da! 

**Test Etme:**

1. https://your-domain.com - Ana sayfa
2. https://your-domain.com/admin - Admin panel
3. https://your-domain.com/blog - Blog modülü
4. https://your-domain.com/zodiac - Burçlar

**İlk Adımlar:**

```bash
# AI ile blog içeriği üret
source /home/django/djtarot/venv/bin/activate
cd /home/django/djtarot
python manage.py generate_blog_posts --count 5 --publish

# Günlük burç yorumları üret
python manage.py batch_generate_horoscopes
```

**Cron Job (Otomatik Güncelleme):**

```bash
crontab -e

# Her gün 6:00'da burç yorumları
0 6 * * * cd /home/django/djtarot && /home/django/djtarot/venv/bin/python manage.py batch_generate_horoscopes

# Her hafta 5 blog yazısı
0 9 * * 1 cd /home/django/djtarot && /home/django/djtarot/venv/bin/python manage.py generate_blog_posts --count 5 --publish
```

---

## 📚 Kaynaklar

- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)
- [OpenLiteSpeed Django](https://openlitespeed.org/kb/django-on-openlitespeed/)
- [DigitalOcean Tutorials](https://www.digitalocean.com/community/tutorials)
- [Let's Encrypt](https://letsencrypt.org/getting-started/)

---

**🚀 İyi Çalışmalar!**
