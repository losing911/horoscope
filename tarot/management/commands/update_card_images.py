"""
Tarot kartlarına Rider-Waite Smith görsellerini ekleyen management komutu.
Kullanım: python manage.py update_card_images
"""
from django.core.management.base import BaseCommand
from tarot.models import TarotCard


class Command(BaseCommand):
    help = 'Tarot kartlarına Rider-Waite Smith görsellerini ekler'

    def handle(self, *args, **kwargs):
        # Sacred Texts ve diğer public domain kaynaklardan Rider-Waite Smith görselleri
        # Base URL - sacred-texts.com tarot görselleri (public domain)
        base_url = "https://www.sacred-texts.com/tarot/pkt/img/"
        
        # Major Arcana görselleri
        major_arcana_images = {
            "The Fool": f"{base_url}ar00.jpg",
            "The Magician": f"{base_url}ar01.jpg",
            "The High Priestess": f"{base_url}ar02.jpg",
            "The Empress": f"{base_url}ar03.jpg",
            "The Emperor": f"{base_url}ar04.jpg",
            "The Hierophant": f"{base_url}ar05.jpg",
            "The Lovers": f"{base_url}ar06.jpg",
            "The Chariot": f"{base_url}ar07.jpg",
            "Strength": f"{base_url}ar08.jpg",
            "The Hermit": f"{base_url}ar09.jpg",
            "Wheel of Fortune": f"{base_url}ar10.jpg",
            "Justice": f"{base_url}ar11.jpg",
            "The Hanged Man": f"{base_url}ar12.jpg",
            "Death": f"{base_url}ar13.jpg",
            "Temperance": f"{base_url}ar14.jpg",
            "The Devil": f"{base_url}ar15.jpg",
            "The Tower": f"{base_url}ar16.jpg",
            "The Star": f"{base_url}ar17.jpg",
            "The Moon": f"{base_url}ar18.jpg",
            "The Sun": f"{base_url}ar19.jpg",
            "Judgement": f"{base_url}ar20.jpg",
            "The World": f"{base_url}ar21.jpg",
        }
        
        # Cups (Kupa) görselleri
        cups_images = {
            "Ace of Cups": f"{base_url}cuac.jpg",
            "Two of Cups": f"{base_url}cu02.jpg",
            "Three of Cups": f"{base_url}cu03.jpg",
            "Four of Cups": f"{base_url}cu04.jpg",
            "Five of Cups": f"{base_url}cu05.jpg",
            "Six of Cups": f"{base_url}cu06.jpg",
            "Seven of Cups": f"{base_url}cu07.jpg",
            "Eight of Cups": f"{base_url}cu08.jpg",
            "Nine of Cups": f"{base_url}cu09.jpg",
            "Ten of Cups": f"{base_url}cu10.jpg",
            "Page of Cups": f"{base_url}cupa.jpg",
            "Knight of Cups": f"{base_url}cukn.jpg",
            "Queen of Cups": f"{base_url}cuqu.jpg",
            "King of Cups": f"{base_url}cuki.jpg",
        }
        
        # Pentacles (Tılsım) görselleri
        pentacles_images = {
            "Ace of Pentacles": f"{base_url}peac.jpg",
            "Two of Pentacles": f"{base_url}pe02.jpg",
            "Three of Pentacles": f"{base_url}pe03.jpg",
            "Four of Pentacles": f"{base_url}pe04.jpg",
            "Five of Pentacles": f"{base_url}pe05.jpg",
            "Six of Pentacles": f"{base_url}pe06.jpg",
            "Seven of Pentacles": f"{base_url}pe07.jpg",
            "Eight of Pentacles": f"{base_url}pe08.jpg",
            "Nine of Pentacles": f"{base_url}pe09.jpg",
            "Ten of Pentacles": f"{base_url}pe10.jpg",
            "Page of Pentacles": f"{base_url}pepa.jpg",
            "Knight of Pentacles": f"{base_url}pekn.jpg",
            "Queen of Pentacles": f"{base_url}pequ.jpg",
            "King of Pentacles": f"{base_url}peki.jpg",
        }
        
        # Swords (Kılıç) görselleri
        swords_images = {
            "Ace of Swords": f"{base_url}swac.jpg",
            "Two of Swords": f"{base_url}sw02.jpg",
            "Three of Swords": f"{base_url}sw03.jpg",
            "Four of Swords": f"{base_url}sw04.jpg",
            "Five of Swords": f"{base_url}sw05.jpg",
            "Six of Swords": f"{base_url}sw06.jpg",
            "Seven of Swords": f"{base_url}sw07.jpg",
            "Eight of Swords": f"{base_url}sw08.jpg",
            "Nine of Swords": f"{base_url}sw09.jpg",
            "Ten of Swords": f"{base_url}sw10.jpg",
            "Page of Swords": f"{base_url}swpa.jpg",
            "Knight of Swords": f"{base_url}swkn.jpg",
            "Queen of Swords": f"{base_url}swqu.jpg",
            "King of Swords": f"{base_url}swki.jpg",
        }
        
        # Wands (Değnek) görselleri
        wands_images = {
            "Ace of Wands": f"{base_url}waac.jpg",
            "Two of Wands": f"{base_url}wa02.jpg",
            "Three of Wands": f"{base_url}wa03.jpg",
            "Four of Wands": f"{base_url}wa04.jpg",
            "Five of Wands": f"{base_url}wa05.jpg",
            "Six of Wands": f"{base_url}wa06.jpg",
            "Seven of Wands": f"{base_url}wa07.jpg",
            "Eight of Wands": f"{base_url}wa08.jpg",
            "Nine of Wands": f"{base_url}wa09.jpg",
            "Ten of Wands": f"{base_url}wa10.jpg",
            "Page of Wands": f"{base_url}wapa.jpg",
            "Knight of Wands": f"{base_url}wakn.jpg",
            "Queen of Wands": f"{base_url}waqu.jpg",
            "King of Wands": f"{base_url}waki.jpg",
        }
        
        # Tüm görselleri birleştir
        all_images = {
            **major_arcana_images,
            **cups_images,
            **pentacles_images,
            **swords_images,
            **wands_images
        }
        
        # Kartları güncelle
        updated_count = 0
        not_found = []
        
        for card in TarotCard.objects.all():
            if card.name_en in all_images:
                card.image_url = all_images[card.name_en]
                card.save()
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {card.name} ({card.name_en}) - görsel eklendi')
                )
            else:
                not_found.append(card.name_en)
                self.stdout.write(
                    self.style.WARNING(f'⚠ {card.name} ({card.name_en}) - görsel bulunamadı')
                )
        
        # Özet
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS(f'\n✓ Güncellenen kart sayısı: {updated_count}'))
        
        if not_found:
            self.stdout.write(self.style.WARNING(f'\n⚠ Görseli bulunamayan kartlar ({len(not_found)}):'))
            for card_name in not_found:
                self.stdout.write(f'  - {card_name}')
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS('\n✓ Kart görselleri başarıyla güncellendi!'))
