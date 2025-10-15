#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tarot_project.settings')
django.setup()

from tarot.models import SiteSettings
from decouple import config

# Site ayarlarını al
settings = SiteSettings.objects.first()

if not settings:
    print("❌ Site ayarları bulunamadı!")
    exit(1)

print("=== MEVCUT AYARLAR ===")
print(f"Default AI Provider: {settings.default_ai_provider}")
print(f"OpenAI Key: {settings.openai_api_key[:30] if settings.openai_api_key else 'BOŞ'}...")
print(f"OpenAI Model: {settings.openai_model}")
print(f"Gemini Key: {settings.gemini_api_key[:30] if settings.gemini_api_key else 'BOŞ'}...")

# .env'den key'leri al ve güncelle
print("\n=== GÜNCELLEME ===")
settings.openai_api_key = config('OPENAI_API_KEY')
settings.gemini_api_key = config('GEMINI_API_KEY')
settings.default_ai_provider = config('DEFAULT_AI_PROVIDER', default='openai')
settings.openai_model = config('OPENAI_MODEL', default='gpt-4o-mini')
settings.gemini_model = config('GEMINI_MODEL', default='gemini-1.5-flash')
settings.save()

print("✅ Site ayarları güncellendi!")
print(f"Default AI Provider: {settings.default_ai_provider}")
print(f"OpenAI Key: {settings.openai_api_key[:30]}...")
print(f"OpenAI Model: {settings.openai_model}")

# AI Provider'ları kontrol et
print("\n=== AI PROVIDERS ===")
from tarot.models import AIProvider
for provider in AIProvider.objects.all():
    print(f"{provider.name}: Active={provider.is_active}, Default={provider.is_default}")
    
    # OpenAI'ı aktif ve default yap
    if 'openai' in provider.name.lower() or 'gpt' in provider.name.lower():
        provider.is_active = True
        provider.is_default = True
        provider.save()
        print(f"  ✅ {provider.name} aktif ve default yapıldı")

print("\n🎉 Tamamlandı! Şimdi tarot okuma yapın.")
