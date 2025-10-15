#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tarot_project.settings')

try:
    django.setup()
    print("✅ Django setup başarılı")
    
    from django.urls import get_resolver
    resolver = get_resolver()
    print(f"✅ URL resolver çalışıyor: {len(resolver.url_patterns)} pattern")
    
    from accounts.views import register, profile
    print("✅ accounts.views import başarılı")
    
    from django.contrib.auth.views import LoginView
    print("✅ Django auth views import başarılı")
    
    print("\n🎉 Tüm kontroller başarılı!")
    
except Exception as e:
    print(f"❌ HATA: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
