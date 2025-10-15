#!/usr/bin/env python
"""
Template rendering testi
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tarot_project.settings')
django.setup()

from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.test import RequestFactory

User = get_user_model()

# Test kullanıcısı
try:
    user = User.objects.get(username='testuser')
    print(f"✅ Kullanıcı bulundu: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   Active: {user.is_active}")
    print(f"   Staff: {user.is_staff}")
    print(f"   Last login: {user.last_login}")
    
    # Request factory
    factory = RequestFactory()
    request = factory.get('/')
    request.user = user
    
    # Base template render test
    print("\n--- Base template render testi ---")
    try:
        context = {
            'user': user,
            'request': request
        }
        # Basit bir test template
        html = render_to_string('base.html', context, request=request)
        print(f"✅ Base template render başarılı: {len(html)} bytes")
    except Exception as e:
        print(f"❌ Base template render hatası: {e}")
        import traceback
        traceback.print_exc()
        
except User.DoesNotExist:
    print("❌ Test kullanıcısı bulunamadı")
except Exception as e:
    print(f"❌ Hata: {e}")
    import traceback
    traceback.print_exc()
