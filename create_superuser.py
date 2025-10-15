#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tarot_project.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Eski admin varsa sil
User.objects.filter(username='admin').delete()

# Yeni admin oluştur
admin = User.objects.create_superuser(
    username='admin',
    email='admin@tarot-yorum.fun',
    password='Admin2025!'
)

print(f'✅ Superuser oluşturuldu!')
print(f'👤 Kullanıcı adı: {admin.username}')
print(f'📧 Email: {admin.email}')
print(f'🔑 Şifre: Admin2025!')
print(f'🌐 Giriş: https://tarot-yorum.fun/admin')
