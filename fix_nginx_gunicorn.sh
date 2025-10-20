#!/bin/bash
# Sunucuda Nginx ve Gunicorn'u düzelten script
# Kullanım: bash fix_nginx_gunicorn.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}🔧 NGINX & GUNICORN FIX SCRIPT${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

# Proje dizinine git
cd /home/django/projects/horoscope

# 1. Log dizini oluştur
echo -e "${YELLOW}📁 Log dizini oluşturuluyor...${NC}"
mkdir -p logs
sudo chown -R django:www-data logs
sudo chmod -R 755 logs

# 2. Git pull
echo -e "${YELLOW}📥 Son değişiklikler çekiliyor...${NC}"
git pull origin main

# 3. Gunicorn servis dosyasını kopyala
echo -e "${YELLOW}⚙️  Gunicorn servis dosyası güncelleniyor...${NC}"
sudo cp gunicorn.service /etc/systemd/system/gunicorn.service
sudo systemctl daemon-reload

# 4. Nginx config dosyasını kopyala
echo -e "${YELLOW}⚙️  Nginx config dosyası güncelleniyor...${NC}"
sudo cp nginx_horoscope.conf /etc/nginx/sites-available/horoscope

# 5. Symbolic link oluştur (varsa önce sil)
echo -e "${YELLOW}🔗 Nginx symbolic link oluşturuluyor...${NC}"
sudo rm -f /etc/nginx/sites-enabled/horoscope
sudo ln -s /etc/nginx/sites-available/horoscope /etc/nginx/sites-enabled/horoscope

# 6. Default nginx config'i devre dışı bırak (varsa)
if [ -f /etc/nginx/sites-enabled/default ]; then
    echo -e "${YELLOW}⚠️  Default Nginx config devre dışı bırakılıyor...${NC}"
    sudo rm -f /etc/nginx/sites-enabled/default
fi

# 7. Nginx config test
echo -e "${YELLOW}🧪 Nginx konfigürasyon testi...${NC}"
if sudo nginx -t; then
    echo -e "${GREEN}✅ Nginx config geçerli!${NC}"
else
    echo -e "${RED}❌ Nginx config hatası! Kontrol edin:${NC}"
    sudo nginx -t
    exit 1
fi

# 8. Virtual environment aktif et ve migration yap
echo -e "${YELLOW}🐍 Migration yapılıyor...${NC}"
source venv/bin/activate
python manage.py migrate

# 9. Static dosyaları topla
echo -e "${YELLOW}📂 Static dosyalar toplanıyor...${NC}"
python manage.py collectstatic --noinput

# 10. İzinleri düzelt
echo -e "${YELLOW}🔒 İzinler düzenleniyor...${NC}"
sudo chown -R django:www-data /home/django/projects/horoscope
sudo chmod -R 755 /home/django/projects/horoscope
sudo chmod -R 775 /home/django/projects/horoscope/staticfiles
sudo chmod -R 775 /home/django/projects/horoscope/media

# 11. Gunicorn'u yeniden başlat
echo -e "${YELLOW}🔄 Gunicorn başlatılıyor...${NC}"
sudo systemctl stop gunicorn 2>/dev/null || true
sudo systemctl start gunicorn
sleep 2

if sudo systemctl is-active --quiet gunicorn; then
    echo -e "${GREEN}✅ Gunicorn çalışıyor!${NC}"
    sudo systemctl status gunicorn --no-pager -l
else
    echo -e "${RED}❌ Gunicorn başlatılamadı!${NC}"
    echo "Log kontrol edin:"
    sudo journalctl -u gunicorn -n 50 --no-pager
    exit 1
fi

# 12. Nginx'i yeniden başlat
echo -e "${YELLOW}🔄 Nginx başlatılıyor...${NC}"
sudo systemctl stop nginx 2>/dev/null || true
sudo systemctl start nginx
sleep 1

if sudo systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✅ Nginx çalışıyor!${NC}"
else
    echo -e "${RED}❌ Nginx başlatılamadı!${NC}"
    echo "Log kontrol edin:"
    sudo tail -n 50 /var/log/nginx/error.log
    exit 1
fi

# 13. Servisleri enable et (otomatik başlasın)
echo -e "${YELLOW}⚡ Servisler otomatik başlatma için ayarlanıyor...${NC}"
sudo systemctl enable gunicorn
sudo systemctl enable nginx

# 14. Test et
echo ""
echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}🧪 SİTE TESTLERİ${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

# Ana sayfa testi
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://159.89.108.100/)
if [ "$HTTP_STATUS" -eq 200 ] || [ "$HTTP_STATUS" -eq 301 ] || [ "$HTTP_STATUS" -eq 302 ]; then
    echo -e "${GREEN}✅ Ana Sayfa: OK (HTTP $HTTP_STATUS)${NC}"
else
    echo -e "${RED}❌ Ana Sayfa: HATA (HTTP $HTTP_STATUS)${NC}"
fi

# Django Admin testi
HTTP_STATUS_ADMIN=$(curl -s -o /dev/null -w "%{http_code}" http://159.89.108.100/admin/)
if [ "$HTTP_STATUS_ADMIN" -eq 200 ] || [ "$HTTP_STATUS_ADMIN" -eq 302 ]; then
    echo -e "${GREEN}✅ Django Admin: OK (HTTP $HTTP_STATUS_ADMIN)${NC}"
else
    echo -e "${YELLOW}⚠️  Django Admin: Kontrol edin (HTTP $HTTP_STATUS_ADMIN)${NC}"
fi

# Custom Admin testi
HTTP_STATUS_CUSTOM=$(curl -s -o /dev/null -w "%{http_code}" http://159.89.108.100/shop/manage/)
if [ "$HTTP_STATUS_CUSTOM" -eq 200 ] || [ "$HTTP_STATUS_CUSTOM" -eq 302 ]; then
    echo -e "${GREEN}✅ Custom Admin: OK (HTTP $HTTP_STATUS_CUSTOM)${NC}"
else
    echo -e "${YELLOW}⚠️  Custom Admin: Kontrol edin (HTTP $HTTP_STATUS_CUSTOM)${NC}"
fi

# Static dosyalar testi
HTTP_STATUS_STATIC=$(curl -s -o /dev/null -w "%{http_code}" http://159.89.108.100/static/css/main.css)
if [ "$HTTP_STATUS_STATIC" -eq 200 ]; then
    echo -e "${GREEN}✅ Static Files: OK (HTTP $HTTP_STATUS_STATIC)${NC}"
else
    echo -e "${YELLOW}⚠️  Static Files: Kontrol edin (HTTP $HTTP_STATUS_STATIC)${NC}"
fi

# Sonuç
echo ""
echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}✅ KURULUM TAMAMLANDI!${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""
echo -e "${GREEN}📋 Servis Durumları:${NC}"
sudo systemctl status gunicorn --no-pager | head -3
sudo systemctl status nginx --no-pager | head -3
echo ""
echo -e "${GREEN}🌐 Test Edilebilir URL'ler:${NC}"
echo "   • Ana Sayfa: http://159.89.108.100/"
echo "   • Django Admin: http://159.89.108.100/admin/"
echo "   • Custom Admin: http://159.89.108.100/shop/manage/"
echo "   • EPROLO Settings: http://159.89.108.100/shop/manage/eprolo/settings/"
echo ""
echo -e "${GREEN}📊 Log Komutları:${NC}"
echo "   • Gunicorn: sudo journalctl -u gunicorn -f"
echo "   • Nginx Access: sudo tail -f /var/log/nginx/horoscope_access.log"
echo "   • Nginx Error: sudo tail -f /var/log/nginx/horoscope_error.log"
echo "   • Django: tail -f logs/gunicorn_error.log"
echo ""
