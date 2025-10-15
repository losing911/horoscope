# Django Çoklu Dil Çeviri Dosyaları Oluşturma Scripti (Windows)

Write-Host "🌍 Django Çeviri Dosyaları Oluşturuluyor..." -ForegroundColor Green

# İngilizce için
Write-Host "📝 İngilizce çeviri dosyası oluşturuluyor..." -ForegroundColor Yellow
.venv\Scripts\python.exe manage.py makemessages -l en --ignore=.venv --ignore=staticfiles

# Almanca için
Write-Host "📝 Almanca çeviri dosyası oluşturuluyor..." -ForegroundColor Yellow
.venv\Scripts\python.exe manage.py makemessages -l de --ignore=.venv --ignore=staticfiles

# Fransızca için
Write-Host "📝 Fransızca çeviri dosyası oluşturuluyor..." -ForegroundColor Yellow
.venv\Scripts\python.exe manage.py makemessages -l fr --ignore=.venv --ignore=staticfiles

Write-Host ""
Write-Host "✅ Tüm çeviri dosyaları oluşturuldu!" -ForegroundColor Green
Write-Host ""
Write-Host "📁 Çeviri dosyaları şurada:" -ForegroundColor Cyan
Write-Host "   - locale\en\LC_MESSAGES\django.po"
Write-Host "   - locale\de\LC_MESSAGES\django.po"
Write-Host "   - locale\fr\LC_MESSAGES\django.po"
Write-Host ""
Write-Host "📋 Sıradaki adımlar:" -ForegroundColor Cyan
Write-Host "   1. .po dosyalarını düzenleyin ve çevirileri ekleyin"
Write-Host "   2. .venv\Scripts\python.exe manage.py compilemessages komutunu çalıştırın"
Write-Host "   3. Server'ı yeniden başlatın"
