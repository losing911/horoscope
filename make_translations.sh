#!/bin/bash
# Django Çoklu Dil Çeviri Dosyaları Oluşturma Scripti

echo "🌍 Django Çeviri Dosyaları Oluşturuluyor..."

# İngilizce için
echo "📝 İngilizce çeviri dosyası oluşturuluyor..."
django-admin makemessages -l en --ignore=.venv --ignore=staticfiles

# Almanca için
echo "📝 Almanca çeviri dosyası oluşturuluyor..."
django-admin makemessages -l de --ignore=.venv --ignore=staticfiles

# Fransızca için
echo "📝 Fransızca çeviri dosyası oluşturuluyor..."
django-admin makemessages -l fr --ignore=.venv --ignore=staticfiles

echo "✅ Tüm çeviri dosyaları oluşturuldu!"
echo ""
echo "📁 Çeviri dosyaları şurada:"
echo "   - locale/en/LC_MESSAGES/django.po"
echo "   - locale/de/LC_MESSAGES/django.po"
echo "   - locale/fr/LC_MESSAGES/django.po"
echo ""
echo "📋 Sıradaki adımlar:"
echo "   1. .po dosyalarını düzenleyin ve çevirileri ekleyin"
echo "   2. python manage.py compilemessages komutunu çalıştırın"
echo "   3. Server'ı yeniden başlatın"
