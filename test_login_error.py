#!/usr/bin/env python
"""
Login sonrası 500 hatasını test et
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tarot_project.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model

User = get_user_model()

# Test client oluştur
client = Client()

print("=" * 50)
print("LOGIN SONRASI 500 HATA TESTİ")
print("=" * 50)

# Test kullanıcısı oluştur veya al
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={'email': 'test@test.com'}
)
if created:
    user.set_password('testpass123')
    user.save()
    print(f"✅ Test kullanıcısı oluşturuldu: {user.username}")
else:
    print(f"✅ Test kullanıcısı mevcut: {user.username}")

# Login dene
print("\n--- Login testi ---")
login_success = client.login(username='testuser', password='testpass123')
print(f"Login başarılı: {login_success}")

# Ana sayfayı dene
print("\n--- Ana sayfa testi (authenticated) ---")
try:
    response = client.get('/')
    print(f"Status Code: {response.status_code}")
    if response.status_code == 500:
        print("❌ 500 HATASI!")
        print(f"Content: {response.content[:500]}")
except Exception as e:
    print(f"❌ EXCEPTION: {e}")
    import traceback
    traceback.print_exc()

# Public readings test
print("\n--- Public readings testi ---")
try:
    response = client.get('/public-readings/')
    print(f"Status Code: {response.status_code}")
    if response.status_code == 500:
        print("❌ 500 HATASI!")
        print(f"Content: {response.content[:500]}")
except Exception as e:
    print(f"❌ EXCEPTION: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
