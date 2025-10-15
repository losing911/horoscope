#!/usr/bin/env python
"""
Tarot kartlarına yeni görsel URL'leri ekle
Sacred Texts ücretsiz Rider-Waite görselleri
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tarot_project.settings')
django.setup()

from tarot.models import TarotCard

# Sacred Texts üzerinden ücretsiz RWS görselleri
# Format: https://www.sacred-texts.com/tarot/pkt/img/ar00.jpg
SACRED_TEXTS_BASE = "https://www.sacred-texts.com/tarot/pkt/img"

def card_name_to_url(name_en, suit, number):
    """Kart ismini URL formatına çevir"""
    # Major Arcana
    if suit == 'major':
        # Sacred Texts formatı: ar00.jpg, ar01.jpg, ..., ar21.jpg
        card_number = str(number).zfill(2)
        return f"{SACRED_TEXTS_BASE}/ar{card_number}.jpg"
    
    # Minor Arcana (sadece As'lar için)
    # Format: cups01.jpg, pent01.jpg, swords01.jpg, wands01.jpg
    suit_map = {
        'cups': 'cups',
        'pentacles': 'pent',
        'swords': 'swords',
        'wands': 'wands'
    }
    suit_name = suit_map.get(suit, 'cups')
    card_number = str(number).zfill(2)
    return f"{SACRED_TEXTS_BASE}/{suit_name}{card_number}.jpg"

# Tüm kartları güncelle
cards = TarotCard.objects.all()
updated = 0

print(f"Toplam {cards.count()} kart güncellenecek...")
print("=" * 60)

for card in cards:
    image_url = card_name_to_url(card.name_en, card.suit, card.number)
    card.image_url = image_url
    card.save()
    updated += 1
    print(f"✅ {card.name:20s} -> {image_url}")

print("=" * 60)
print(f"\n🎉 {updated} kartın görseli güncellendi!")
print(f"\nTest URL: {SACRED_TEXTS_BASE}/ar00.jpg")
