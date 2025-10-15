#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tarot_project.settings')
django.setup()

from tarot.models import TarotCard

cards = TarotCard.objects.all()
print(f"Toplam kart sayısı: {cards.count()}")
print(f"Görselli kart sayısı: {cards.exclude(image_url='').count()}")
print(f"Görselsiz kart sayısı: {cards.filter(image_url='').count()}")
print("\n--- İlk 5 kart ---")
for card in cards[:5]:
    print(f"{card.name}: {card.image_url or 'BOŞ'}")
