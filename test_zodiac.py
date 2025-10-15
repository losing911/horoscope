#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tarot_project.settings')
django.setup()

from zodiac.models import ZodiacSign
from datetime import date

print("=" * 60)
print("🌟 BURÇ VERİLERİ TEST RAPORU")
print("=" * 60)

# 1. Toplam burç sayısı
total = ZodiacSign.objects.count()
print(f"\n📊 Toplam Burç Sayısı: {total}")

if total == 0:
    print("❌ VERİTABANINDA BURÇ YOK! populate_zodiac_data komutunu çalıştırın.")
    exit(1)

# 2. Tüm burçları listele
print(f"\n📋 TÜM BURÇLAR ({total} adet):")
print("-" * 60)
for sign in ZodiacSign.objects.all().order_by('order'):
    print(f"{sign.order:2d}. {sign.symbol} {sign.name:12} ({sign.name_en:12}) - {sign.date_range}")

# 3. Tarihten burç bulma testleri
print("\n🔍 TARİHTEN BURÇ BULMA TESTLERİ:")
print("-" * 60)
test_dates = [
    (3, 25, 'Mart 25'),
    (5, 15, 'Mayıs 15'),
    (7, 20, 'Temmuz 20'),
    (10, 10, 'Ekim 10'),
    (12, 25, 'Aralık 25'),
    (1, 15, 'Ocak 15'),
    (2, 19, 'Şubat 19'),
    (3, 20, 'Mart 20'),
]

for month, day, desc in test_dates:
    try:
        sign = ZodiacSign.get_sign_by_date(month, day)
        print(f"✓ {desc:15} → {sign.symbol} {sign.name} ({sign.name_en})")
    except Exception as e:
        print(f"✗ {desc:15} → HATA: {e}")

# 4. Her elementin burç sayısı
print("\n🔥 ELEMENT DAĞILIMI:")
print("-" * 60)
elements = {
    'fire': 'Ateş 🔥',
    'earth': 'Toprak 🌍',
    'air': 'Hava 💨',
    'water': 'Su 💧',
}
for element, name in elements.items():
    count = ZodiacSign.objects.filter(element=element).count()
    signs = ZodiacSign.objects.filter(element=element).values_list('name', flat=True)
    print(f"{name:12} → {count} burç: {', '.join(signs)}")

# 5. Her kalitenin burç sayısı
print("\n⚖️  KALİTE DAĞILIMI:")
print("-" * 60)
qualities = {
    'cardinal': 'Öncü (Cardinal)',
    'fixed': 'Sabit (Fixed)',
    'mutable': 'Değişken (Mutable)',
}
for quality, name in qualities.items():
    count = ZodiacSign.objects.filter(quality=quality).count()
    signs = ZodiacSign.objects.filter(quality=quality).values_list('name', flat=True)
    print(f"{name:20} → {count} burç: {', '.join(signs)}")

# 6. Rastgele bir burç detayı
import random
random_sign = random.choice(ZodiacSign.objects.all())
print(f"\n🎲 RASTGELE BURÇ DETAYI:")
print("=" * 60)
print(f"Burç: {random_sign.symbol} {random_sign.name} ({random_sign.name_en})")
print(f"Tarih: {random_sign.date_range}")
print(f"Element: {random_sign.element}")
print(f"Kalite: {random_sign.quality}")
print(f"Gezegen: {random_sign.ruling_planet}")
print(f"Açıklama: {random_sign.description}")
print(f"Özellikler: {random_sign.traits}")
print(f"Güçlü Yönler: {random_sign.strengths}")
print(f"Zayıf Yönler: {random_sign.weaknesses}")
print(f"Uyumlu Burçlar: {random_sign.compatibility}")
print(f"Şanslı Sayılar: {random_sign.lucky_numbers}")
print(f"Şanslı Renkler: {random_sign.lucky_colors}")
print(f"Şanslı Gün: {random_sign.lucky_day}")

print("\n" + "=" * 60)
print("✅ TÜM TESTLER TAMAMLANDI!")
print("=" * 60)
