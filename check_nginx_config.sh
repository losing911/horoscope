#!/bin/bash
# Nginx konfigürasyon hatasını tespit ve düzelt

echo "🔍 Nginx konfigürasyon testi yapılıyor..."
echo ""

# Nginx config test
sudo nginx -t

echo ""
echo "========================================="
echo ""

# Eğer hata varsa detayları göster
echo "📋 Nginx error logları:"
sudo tail -n 50 /var/log/nginx/error.log

echo ""
echo "========================================="
echo ""

# Horoscope sitesinin config dosyasını kontrol et
echo "📄 Horoscope site config dosyası:"
if [ -f /etc/nginx/sites-available/horoscope ]; then
    echo "Dosya bulundu: /etc/nginx/sites-available/horoscope"
    echo ""
    cat /etc/nginx/sites-available/horoscope
else
    echo "❌ Config dosyası bulunamadı!"
fi

echo ""
echo "========================================="
echo ""

# Symbolic link kontrolü
echo "🔗 Symbolic link kontrolü:"
ls -la /etc/nginx/sites-enabled/ | grep horoscope
