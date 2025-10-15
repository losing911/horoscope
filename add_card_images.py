#!/usr/bin/env python
"""
Tarot kartlarına görsel URL'leri ekle
GitHub'daki ücretsiz Rider-Waite tarot görselleri kullanılıyor
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tarot_project.settings')
django.setup()

from tarot.models import TarotCard

# GitHub üzerinden ücretsiz RWS (Rider-Waite-Smith) görselleri
BASE_URL = "https://raw.githubusercontent.com/dariusk/corpora/master/data/divination/tarot_interpretations.json"

# Alternatif: Sacred Texts üzerinden RWS görselleri
RWS_BASE = "https://www.sacred-texts.com/tarot/pkt/img"

# En iyi seçenek: GitHub Tarot Images repository
TAROT_IMG_BASE = "https://raw.githubusercontent.com/ekelen/tarot-api/main/static/img/cards"

# Kart isimlerini URL-safe formata çevir
def card_name_to_url(name_en, suit):
    """Kart ismini URL formatına çevir"""
    # Major Arcana
    if suit == 'major':
        name_map = {
            'The Fool': 'ar00',
            'The Magician': 'ar01',
            'The High Priestess': 'ar02',
            'The Empress': 'ar03',
            'The Emperor': 'ar04',
            'The Hierophant': 'ar05',
            'The Lovers': 'ar06',
            'The Chariot': 'ar07',
            'Strength': 'ar08',
            'The Hermit': 'ar09',
            'Wheel of Fortune': 'ar10',
            'Justice': 'ar11',
            'The Hanged Man': 'ar12',
            'Death': 'ar13',
            'Temperance': 'ar14',
            'The Devil': 'ar15',
            'The Tower': 'ar16',
            'The Star': 'ar17',
            'The Moon': 'ar18',
            'The Sun': 'ar19',
            'Judgement': 'ar20',
            'The World': 'ar21',
        }
        return f"{TAROT_IMG_BASE}/{name_map.get(name_en, 'ar00')}.jpg"
    
    # Minor Arcana (sadece As'lar için)
    suit_map = {
        'cups': 'cu',
        'pentacles': 'pe',
        'swords': 'sw',
        'wands': 'wa'
    }
    suit_code = suit_map.get(suit, 'cu')
    return f"{TAROT_IMG_BASE}/{suit_code}01.jpg"

# Tüm kartları güncelle
cards = TarotCard.objects.all()
updated = 0

print(f"Toplam {cards.count()} kart güncellenecek...")

for card in cards:
    image_url = card_name_to_url(card.name_en, card.suit)
    card.image_url = image_url
    card.save()
    updated += 1
    print(f"✅ {card.name}: {image_url}")

print(f"\n🎉 {updated} kartın görseli güncellendi!")
