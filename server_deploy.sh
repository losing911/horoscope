#!/bin/bash
# Sunucuda çalıştırılacak deployment script
# Kullanım: bash server_deploy.sh

set -e  # Hata olursa dur

echo "========================================="
echo "🚀 DEPLOYMENT BAŞLATILIYOR..."
echo "========================================="
echo ""

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Proje dizinine git
echo "📁 Proje dizinine gidiliyor..."
cd /home/django/projects/horoscope

# Git durumunu kontrol et
echo ""
echo "📊 Git durumu:"
git status

# Uncommitted değişiklikler var mı kontrol et
if [[ `git status --porcelain` ]]; then
    echo -e "${YELLOW}⚠️  Uncommitted değişiklikler bulundu!${NC}"
    echo "Devam etmek istiyor musunuz? (y/n)"
    read -r response
    if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo "Deployment iptal edildi."
        exit 1
    fi
    
    # Değişiklikleri stash'le
    echo "📦 Değişiklikler stash'leniyor..."
    git stash
fi

# Git pull
echo ""
echo "📥 GitHub'dan son değişiklikler çekiliyor..."
git pull origin main

# Virtual environment'ı aktif et
echo ""
echo "🐍 Virtual environment aktif ediliyor..."
source venv/bin/activate

# Bağımlılıkları güncelle (varsa)
echo ""
echo "📦 Python bağımlılıkları kontrol ediliyor..."
pip install -r requirements.txt --quiet

# Database migration
echo ""
echo "🗄️  Database migration yapılıyor..."
python manage.py migrate

# Static dosyaları topla
echo ""
echo "📂 Static dosyalar toplanıyor..."
python manage.py collectstatic --noinput

# Gunicorn'u restart et
echo ""
echo "🔄 Gunicorn restart ediliyor..."
sudo systemctl restart gunicorn
sleep 2

# Gunicorn durumu
if sudo systemctl is-active --quiet gunicorn; then
    echo -e "${GREEN}✅ Gunicorn başarıyla başlatıldı!${NC}"
else
    echo -e "${RED}❌ Gunicorn başlatılamadı! Logları kontrol edin:${NC}"
    echo "sudo journalctl -u gunicorn -n 50"
    exit 1
fi

# Nginx'i restart et
echo ""
echo "🔄 Nginx restart ediliyor..."
sudo systemctl restart nginx
sleep 1

# Nginx durumu
if sudo systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✅ Nginx başarıyla başlatıldı!${NC}"
else
    echo -e "${RED}❌ Nginx başlatılamadı! Logları kontrol edin:${NC}"
    echo "sudo tail -f /var/log/nginx/error.log"
    exit 1
fi

# Test et
echo ""
echo "🧪 Site testi yapılıyor..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://159.89.108.100/)

if [ "$HTTP_STATUS" -eq 200 ] || [ "$HTTP_STATUS" -eq 301 ] || [ "$HTTP_STATUS" -eq 302 ]; then
    echo -e "${GREEN}✅ Ana sayfa erişilebilir! (HTTP $HTTP_STATUS)${NC}"
else
    echo -e "${RED}❌ Ana sayfa erişilemiyor! (HTTP $HTTP_STATUS)${NC}"
fi

# Custom Admin test
HTTP_STATUS_ADMIN=$(curl -s -o /dev/null -w "%{http_code}" http://159.89.108.100/shop/manage/)
if [ "$HTTP_STATUS_ADMIN" -eq 200 ] || [ "$HTTP_STATUS_ADMIN" -eq 302 ]; then
    echo -e "${GREEN}✅ Custom Admin erişilebilir! (HTTP $HTTP_STATUS_ADMIN)${NC}"
else
    echo -e "${YELLOW}⚠️  Custom Admin kontrol edin! (HTTP $HTTP_STATUS_ADMIN)${NC}"
fi

# Sonuç
echo ""
echo "========================================="
echo -e "${GREEN}✅ DEPLOYMENT TAMAMLANDI!${NC}"
echo "========================================="
echo ""
echo "📋 Test edilmesi gereken sayfalar:"
echo "   - Ana Sayfa: http://138.68.76.120/"
echo "   - Django Admin: http://138.68.76.120/admin/"
echo "   - Custom Admin: http://138.68.76.120/shop/manage/"
echo "   - EPROLO Settings: http://138.68.76.120/shop/manage/eprolo/settings/"
echo ""
echo "📊 Log kontrol komutları:"
echo "   - Gunicorn: sudo journalctl -u gunicorn -n 50"
echo "   - Nginx: sudo tail -f /var/log/nginx/error.log"
echo "   - Django: tail -f logs/django.log"
echo ""
