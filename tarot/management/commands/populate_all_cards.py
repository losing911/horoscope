"""
Management command to populate all 78 Tarot cards
"""
from django.core.management.base import BaseCommand
from tarot.models import TarotCard


class Command(BaseCommand):
    help = 'Tüm 78 Tarot kartını database\'e ekler'
    
    def handle(self, *args, **options):
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("🎴 78 TAROT KARTINI EKLEME"))
        self.stdout.write("="*60 + "\n")
        
        created_count = 0
        updated_count = 0
        
        # 22 Major Arcana kartları (zaten var)
        major_arcana = [
            (0, "Deli", "The Fool"),
            (1, "Büyücü", "The Magician"),
            (2, "Yüksek Rahibe", "The High Priestess"),
            (3, "İmparatoriçe", "The Empress"),
            (4, "İmparator", "The Emperor"),
            (5, "Hierophant", "The Hierophant"),
            (6, "Aşıklar", "The Lovers"),
            (7, "Savaş Arabası", "The Chariot"),
            (8, "Güç", "Strength"),
            (9, "Ermiş", "The Hermit"),
            (10, "Kader Çarkı", "Wheel of Fortune"),
            (11, "Adalet", "Justice"),
            (12, "Asılan Adam", "The Hanged Man"),
            (13, "Ölüm", "Death"),
            (14, "Ölçülülük", "Temperance"),
            (15, "Şeytan", "The Devil"),
            (16, "Kule", "The Tower"),
            (17, "Yıldız", "The Star"),
            (18, "Ay", "The Moon"),
            (19, "Güneş", "The Sun"),
            (20, "Yargı", "Judgement"),
            (21, "Dünya", "The World"),
        ]
        
        # 56 Minor Arcana kartları
        minor_suits = {
            'cups': ('Kupa', 'Cups'),
            'pentacles': ('Tılsım', 'Pentacles'),
            'swords': ('Kılıç', 'Swords'),
            'wands': ('Değnek', 'Wands')
        }
        
        court_cards_tr = ['As', 'İkili', 'Üçlü', 'Dörtlü', 'Beşli', 'Altılı', 'Yedili', 
                         'Sekizli', 'Dokuzlu', 'Onlu', 'Vale', 'Şövalye', 'Kraliçe', 'Kral']
        court_cards_en = ['Ace', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 
                         'Eight', 'Nine', 'Ten', 'Page', 'Knight', 'Queen', 'King']
        
        # Major Arcana'yı kontrol et (zaten var mı?)
        for number, name_tr, name_en in major_arcana:
            card, created = TarotCard.objects.get_or_create(
                suit='major',
                number=number,
                defaults={
                    'name': name_tr,
                    'name_en': name_en,
                    'upright_meaning': f'{name_tr} kartının düz anlamı',
                    'reversed_meaning': f'{name_tr} kartının ters anlamı',
                    'description': f'{name_tr} kartı',
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f"  ✅ {name_tr} eklendi")
            else:
                updated_count += 1
        
        # Minor Arcana kartlarını ekle
        for suit_key, (suit_name_tr, suit_name_en) in minor_suits.items():
            for i in range(14):
                number = i + 1
                card_name_tr = f"{suit_name_tr} {court_cards_tr[i]}"
                card_name_en = f"{court_cards_en[i]} of {suit_name_en}"
                
                card, created = TarotCard.objects.get_or_create(
                    suit=suit_key,
                    number=number,
                    defaults={
                        'name': card_name_tr,
                        'name_en': card_name_en,
                        'upright_meaning': f'{card_name_tr} kartının düz anlamı',
                        'reversed_meaning': f'{card_name_tr} kartının ters anlamı',
                        'description': f'{card_name_tr} kartı',
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f"  ✅ {card_name_tr} ({card_name_en}) eklendi")
                else:
                    updated_count += 1
        
        # Toplam kontrol
        total = TarotCard.objects.count()
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(f"📊 Toplam Kart: {total}")
        self.stdout.write(f"✅ Yeni Eklenen: {created_count}")
        self.stdout.write(f"ℹ️  Zaten Var: {updated_count}")
        
        if total == 78:
            self.stdout.write(self.style.SUCCESS("\n🎉 Tüm 78 kart başarıyla eklendi!"))
        else:
            self.stdout.write(self.style.WARNING(f"\n⚠️  Toplam {total} kart, 78 olmalı!"))
        
        self.stdout.write("="*60 + "\n")
