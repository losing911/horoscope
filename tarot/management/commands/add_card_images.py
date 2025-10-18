"""
Management command to download tarot card images from Tarot API
"""
import os
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from tarot.models import TarotCard


class Command(BaseCommand):
    help = 'Tarot kartlarına görselleri ekler (Tarot API kullanarak)'
    
    # Tarot API kartları için mapping (ücretsiz kaynak)
    CARD_MAPPING = {
        'The Fool': '0',
        'The Magician': '1',
        'The High Priestess': '2',
        'The Empress': '3',
        'The Emperor': '4',
        'The Hierophant': '5',
        'The Lovers': '6',
        'The Chariot': '7',
        'Strength': '8',
        'The Hermit': '9',
        'Wheel of Fortune': '10',
        'Justice': '11',
        'The Hanged Man': '12',
        'Death': '13',
        'Temperance': '14',
        'The Devil': '15',
        'The Tower': '16',
        'The Star': '17',
        'The Moon': '18',
        'The Sun': '19',
        'Judgement': '20',
        'The World': '21',
        # Minor Arcana
        'Ace of Cups': 'c01',
        'Ace of Pentacles': 'p01',
        'Ace of Swords': 's01',
        'Ace of Wands': 'w01',
    }
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=str,
            default='tarotapi',
            help='Görsel kaynağı: tarotapi (varsayılan), manual'
        )
    
    def handle(self, *args, **options):
        source = options['source']
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("🎴 TAROT KART GÖRSELLERİNİ EKLEME"))
        self.stdout.write("="*60 + "\n")
        
        if source == 'tarotapi':
            self._download_from_tarotapi()
        elif source == 'manual':
            self._set_manual_urls()
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("✅ İşlem tamamlandı!"))
        self.stdout.write("="*60 + "\n")
    
    def _download_from_tarotapi(self):
        """Tarot API'den görselleri indir"""
        base_url = "https://sacred-texts.com/tarot/pkt/img"
        
        cards = TarotCard.objects.all()
        success_count = 0
        failed_count = 0
        
        for card in cards:
            card_code = self.CARD_MAPPING.get(card.name_en)
            
            if not card_code:
                self.stdout.write(
                    self.style.WARNING(f"⚠️  Eşleşme bulunamadı: {card.name} ({card.name_en})")
                )
                failed_count += 1
                continue
            
            # Rider-Waite görselleri
            image_url = f"{base_url}/ar{card_code}.jpg"
            
            try:
                # URL'yi kontrol et
                response = requests.head(image_url, timeout=5)
                if response.status_code == 200:
                    card.image_url = image_url
                    card.save()
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ {card.name} - {image_url}")
                    )
                    success_count += 1
                else:
                    self.stdout.write(
                        self.style.ERROR(f"❌ {card.name} - URL geçersiz: {response.status_code}")
                    )
                    failed_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ {card.name} - Hata: {str(e)}")
                )
                failed_count += 1
        
        self.stdout.write(f"\n📊 Başarılı: {success_count}")
        self.stdout.write(f"📊 Başarısız: {failed_count}")
    
    def _set_manual_urls(self):
        """Manuel URL'leri ayarla (alternatif kaynaklar)"""
        # Wikimedia Commons - Public Domain tarot görselleri
        base_url = "https://upload.wikimedia.org/wikipedia/commons"
        
        manual_urls = {
            # Major Arcana (22 cards)
            'The Fool': f"{base_url}/9/90/RWS_Tarot_00_Fool.jpg",
            'The Magician': f"{base_url}/d/de/RWS_Tarot_01_Magician.jpg",
            'The High Priestess': f"{base_url}/8/88/RWS_Tarot_02_High_Priestess.jpg",
            'The Empress': f"{base_url}/d/d2/RWS_Tarot_03_Empress.jpg",
            'The Emperor': f"{base_url}/c/c3/RWS_Tarot_04_Emperor.jpg",
            'The Hierophant': f"{base_url}/8/8d/RWS_Tarot_05_Hierophant.jpg",
            'The Lovers': f"{base_url}/3/3a/TheLovers.jpg",
            'The Chariot': f"{base_url}/9/9b/RWS_Tarot_07_Chariot.jpg",
            'Strength': f"{base_url}/f/f5/RWS_Tarot_08_Strength.jpg",
            'The Hermit': f"{base_url}/4/4d/RWS_Tarot_09_Hermit.jpg",
            'Wheel of Fortune': f"{base_url}/3/3c/RWS_Tarot_10_Wheel_of_Fortune.jpg",
            'Justice': f"{base_url}/e/e0/RWS_Tarot_11_Justice.jpg",
            'The Hanged Man': f"{base_url}/2/2b/RWS_Tarot_12_Hanged_Man.jpg",
            'Death': f"{base_url}/d/d7/RWS_Tarot_13_Death.jpg",
            'Temperance': f"{base_url}/f/f8/RWS_Tarot_14_Temperance.jpg",
            'The Devil': f"{base_url}/5/55/RWS_Tarot_15_Devil.jpg",
            'The Tower': f"{base_url}/5/53/RWS_Tarot_16_Tower.jpg",
            'The Star': f"{base_url}/d/db/RWS_Tarot_17_Star.jpg",
            'The Moon': f"{base_url}/7/7f/RWS_Tarot_18_Moon.jpg",
            'The Sun': f"{base_url}/1/17/RWS_Tarot_19_Sun.jpg",
            'Judgement': f"{base_url}/d/dd/RWS_Tarot_20_Judgement.jpg",
            'The World': f"{base_url}/f/ff/RWS_Tarot_21_World.jpg",
            
            # Minor Arcana - Cups (14 cards)
            'Ace of Cups': f"{base_url}/3/36/Cups01.jpg",
            'Two of Cups': f"{base_url}/f/f8/Cups02.jpg",
            'Three of Cups': f"{base_url}/7/7a/Cups03.jpg",
            'Four of Cups': f"{base_url}/3/35/Cups04.jpg",
            'Five of Cups': f"{base_url}/d/d7/Cups05.jpg",
            'Six of Cups': f"{base_url}/1/17/Cups06.jpg",
            'Seven of Cups': f"{base_url}/a/ae/Cups07.jpg",
            'Eight of Cups': f"{base_url}/6/60/Cups08.jpg",
            'Nine of Cups': f"{base_url}/2/24/Cups09.jpg",
            'Ten of Cups': f"{base_url}/8/84/Cups10.jpg",
            'Page of Cups': f"{base_url}/a/ad/Cups11.jpg",
            'Knight of Cups': f"{base_url}/f/fa/Cups12.jpg",
            'Queen of Cups': f"{base_url}/6/62/Cups13.jpg",
            'King of Cups': f"{base_url}/0/04/Cups14.jpg",
            
            # Minor Arcana - Pentacles (14 cards)
            'Ace of Pentacles': f"{base_url}/f/fd/Pents01.jpg",
            'Two of Pentacles': f"{base_url}/9/9f/Pents02.jpg",
            'Three of Pentacles': f"{base_url}/4/42/Pents03.jpg",
            'Four of Pentacles': f"{base_url}/3/35/Pents04.jpg",
            'Five of Pentacles': f"{base_url}/9/96/Pents05.jpg",
            'Six of Pentacles': f"{base_url}/a/a6/Pents06.jpg",
            'Seven of Pentacles': f"{base_url}/6/6a/Pents07.jpg",
            'Eight of Pentacles': f"{base_url}/4/49/Pents08.jpg",
            'Nine of Pentacles': f"{base_url}/f/f0/Pents09.jpg",
            'Ten of Pentacles': f"{base_url}/4/42/Pents10.jpg",
            'Page of Pentacles': f"{base_url}/e/ec/Pents11.jpg",
            'Knight of Pentacles': f"{base_url}/d/d5/Pents12.jpg",
            'Queen of Pentacles': f"{base_url}/8/88/Pents13.jpg",
            'King of Pentacles': f"{base_url}/1/1c/Pents14.jpg",
            
            # Minor Arcana - Swords (14 cards)
            'Ace of Swords': f"{base_url}/1/1a/Swords01.jpg",
            'Two of Swords': f"{base_url}/9/9e/Swords02.jpg",
            'Three of Swords': f"{base_url}/0/02/Swords03.jpg",
            'Four of Swords': f"{base_url}/b/bf/Swords04.jpg",
            'Five of Swords': f"{base_url}/2/23/Swords05.jpg",
            'Six of Swords': f"{base_url}/2/29/Swords06.jpg",
            'Seven of Swords': f"{base_url}/3/34/Swords07.jpg",
            'Eight of Swords': f"{base_url}/a/a7/Swords08.jpg",
            'Nine of Swords': f"{base_url}/2/2f/Swords09.jpg",
            'Ten of Swords': f"{base_url}/d/d4/Swords10.jpg",
            'Page of Swords': f"{base_url}/4/4c/Swords11.jpg",
            'Knight of Swords': f"{base_url}/b/b0/Swords12.jpg",
            'Queen of Swords': f"{base_url}/d/d4/Swords13.jpg",
            'King of Swords': f"{base_url}/3/33/Swords14.jpg",
            
            # Minor Arcana - Wands (14 cards)
            'Ace of Wands': f"{base_url}/1/11/Wands01.jpg",
            'Two of Wands': f"{base_url}/0/0f/Wands02.jpg",
            'Three of Wands': f"{base_url}/f/ff/Wands03.jpg",
            'Four of Wands': f"{base_url}/a/a4/Wands04.jpg",
            'Five of Wands': f"{base_url}/9/9d/Wands05.jpg",
            'Six of Wands': f"{base_url}/3/3b/Wands06.jpg",
            'Seven of Wands': f"{base_url}/e/e4/Wands07.jpg",
            'Eight of Wands': f"{base_url}/6/6b/Wands08.jpg",
            'Nine of Wands': f"{base_url}/4/4d/Wands09.jpg",
            'Ten of Wands': f"{base_url}/0/0b/Wands10.jpg",
            'Page of Wands': f"{base_url}/6/6a/Wands11.jpg",
            'Knight of Wands': f"{base_url}/1/16/Wands12.jpg",
            'Queen of Wands': f"{base_url}/0/0d/Wands13.jpg",
            'King of Wands': f"{base_url}/c/ce/Wands14.jpg",
        }
        
        success_count = 0
        
        for card in TarotCard.objects.all():
            url = manual_urls.get(card.name_en)
            if url:
                card.image_url = url
                card.save()
                self.stdout.write(
                    self.style.SUCCESS(f"✅ {card.name} - {url}")
                )
                success_count += 1
        
        self.stdout.write(f"\n📊 Güncellenen: {success_count}")
