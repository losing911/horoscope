# SUNUCUYA DEPLOYMENT ADIMLARI

## 1. Sunucuya SSH ile Bağlan
```bash
ssh root@159.89.108.100
# Şifre: losing2016
```

## 2. Proje Dizinine Git ve Git Pull
```bash
cd /home/django/projects/horoscope
git pull origin main
```

## 3. Virtual Environment'ı Aktif Et
```bash
source venv/bin/activate
```

## 4. Yeni Bağımlılıkları Yükle (varsa)
```bash
pip install -r requirements.txt
```

## 5. Database Migration Yap
```bash
python manage.py migrate
```

## 6. Static Dosyaları Topla
```bash
python manage.py collectstatic --noinput
```

## 7. Gunicorn'u Yeniden Başlat
```bash
sudo systemctl restart gunicorn
sudo systemctl status gunicorn
```

## 8. Nginx'i Yeniden Başlat
```bash
sudo systemctl restart nginx
sudo systemctl status nginx
```

## 9. Log Kontrolü
```bash
# Gunicorn logları
sudo journalctl -u gunicorn -n 50

# Nginx error logları
sudo tail -f /var/log/nginx/error.log

# Application logları (varsa)
tail -f /home/django/projects/horoscope/logs/django.log
```

## 10. Test Et
```bash
# Site çalışıyor mu kontrol et
curl http://159.89.108.100

# Custom admin panele erişimi test et
curl http://159.89.108.100/shop/manage/
```

---

## ⚠️ SORUN GİDERME

### Gunicorn Başlatılamıyorsa:
```bash
# Servis dosyasını kontrol et
sudo nano /etc/systemd/system/gunicorn.service

# Daemon'u yeniden yükle
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
```

### Static Dosyalar Yüklenemiyorsa:
```bash
# Static dizini kontrol et
ls -la /home/django/projects/horoscope/staticfiles/

# İzinleri düzelt
sudo chown -R django:www-data /home/django/projects/horoscope/staticfiles/
sudo chmod -R 755 /home/django/projects/horoscope/staticfiles/
```

### Database Hatası:
```bash
# PostgreSQL'e bağlan
sudo -u postgres psql

# Database'i kontrol et
\l
\c horoscope_db
\dt

# Çık
\q
```

### Nginx Hatası:
```bash
# Config test et
sudo nginx -t

# Config dosyasını düzenle
sudo nano /etc/nginx/sites-available/horoscope
```

---

## 📝 DEPLOYMENT ÖNCESİ KONTROL LİSTESİ

- [x] Tüm dosyalar commit edildi
- [x] GitHub'a push yapıldı
- [ ] Sunucuya SSH bağlantısı yapıldı
- [ ] Git pull yapıldı
- [ ] Migration uygulandı
- [ ] Static dosyalar toplandı
- [ ] Gunicorn restart edildi
- [ ] Nginx restart edildi
- [ ] Site test edildi
- [ ] Custom admin panel çalışıyor mu kontrol edildi
- [ ] EPROLO sayfaları test edildi

---

## 🎯 DEPLOY SONRASI TEST NOKTALARI

1. **Ana Sayfa**: http://159.89.108.100/
2. **Django Admin**: http://159.89.108.100/admin/
3. **Custom Admin Dashboard**: http://159.89.108.100/shop/manage/
4. **Ürün Yönetimi**: http://159.89.108.100/shop/manage/products/
5. **Sipariş Yönetimi**: http://159.89.108.100/shop/manage/orders/
6. **Kategori Yönetimi**: http://159.89.108.100/shop/manage/categories/
7. **EPROLO Dashboard**: http://159.89.108.100/shop/manage/eprolo/
8. **EPROLO Ayarları**: http://159.89.108.100/shop/manage/eprolo/settings/
9. **İstatistikler**: http://159.89.108.100/shop/manage/statistics/

---

## 🚀 HIZLI DEPLOYMENT (Tek Komut)

Tüm deployment adımlarını tek seferde yapmak için:

```bash
ssh root@159.89.108.100 << 'EOF'
cd /home/django/projects/horoscope && \
source venv/bin/activate && \
git pull origin main && \
pip install -r requirements.txt && \
python manage.py migrate && \
python manage.py collectstatic --noinput && \
sudo systemctl restart gunicorn && \
sudo systemctl restart nginx && \
echo "✅ Deployment tamamlandı!" && \
sudo systemctl status gunicorn --no-pager && \
sudo systemctl status nginx --no-pager
EOF
```

---

## 📊 YAPILAN DEĞİŞİKLİKLER

### Yeni Dosyalar:
- ✅ `shop/custom_admin_views.py` - Custom admin backend (820+ satır)
- ✅ `shop/services.py` - EPROLO servis katmanı (480+ satır)
- ✅ `shop/templates/shop/custom_admin/` - 10 template dosyası
- ✅ `EPROLO_KATEGORI_BAZLI_SENKRON.md` - Dokümantasyon
- ✅ Migration dosyaları (0002, 0003)

### Değiştirilen Dosyalar:
- ✅ `shop/models.py` - EPROLO alanları eklendi
- ✅ `shop/admin.py` - Django admin güncellendi
- ✅ `shop/urls.py` - Custom admin URL'leri eklendi

### Özellikler:
- ✅ Kategori bazlı EPROLO senkronizasyonu
- ✅ Template filter hatası düzeltildi (mul, filter_active)
- ✅ Tam özellikli custom admin paneli
- ✅ Mock API desteği
- ✅ Otomatik fiyatlandırma sistemi
