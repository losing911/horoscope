# 🚀 Production Deployment Komutları

Sunucuya SSH ile bağlanın ve şu komutları sırayla çalıştırın:

```bash
ssh django@159.89.108.100

cd /home/django/projects/horoscope
source venv/bin/activate

# Migration'ı uygula
python manage.py migrate

# AI Provider'ları kur
python setup_ai_providers.py

# Gunicorn'u yeniden başlat
sudo systemctl restart gunicorn

# Nginx'i yeniden başlat (opsiyonel)
sudo systemctl restart nginx

# Logları kontrol et
sudo journalctl -u gunicorn -n 50 --no-pager
```

## ✅ Beklenen Çıktı:

1. **Migration**: `Applying tarot.0008_update_ai_providers... OK`
2. **AI Provider Setup**: 
   - ✅ OpenAI Provider oluşturuldu
   - ✅ Gemini Provider oluşturuldu  
   - ✅ DeepSeek Provider oluşturuldu (deaktif)
3. **Gunicorn**: `Restarted gunicorn.service`

## 🔍 Test:

Admin paneline gidin: `http://your-domain/admin/tarot/aiprovider/`

Provider'ları görebiliyor musunuz kontrol edin!
