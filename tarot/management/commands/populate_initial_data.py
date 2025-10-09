from django.core.management.base import BaseCommand
from tarot.models import SiteSettings, AIProvider, TarotSpread, TarotCard


class Command(BaseCommand):
    help = 'Site için başlangıç verilerini yükler'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Başlangıç verileri yükleniyor...'))
        
        # Site ayarlarını oluştur
        self.create_site_settings()
        
        # AI sağlayıcıları oluştur
        self.create_ai_providers()
        
        # Tarot yayılımları oluştur
        self.create_tarot_spreads()
        
        # Basit tarot kartları oluştur
        self.create_basic_tarot_cards()
        
        self.stdout.write(self.style.SUCCESS('Başlangıç verileri başarıyla yüklendi!'))

    def create_site_settings(self):
        """Site ayarlarını oluştur"""
        settings, created = SiteSettings.objects.get_or_create(pk=1)
        if created:
            self.stdout.write('Site ayarları oluşturuldu.')
        else:
            self.stdout.write('Site ayarları zaten mevcut.')

    def create_ai_providers(self):
        """AI sağlayıcıları oluştur"""
        providers = [
            {
                'name': 'openai',
                'display_name': 'OpenAI GPT',
                'max_tokens': 1000,
                'temperature': 0.7,
                'system_prompt': 'Sen uzman bir tarot yorumcususun. Kartların anlamlarını detaylı, anlayışlı ve pozitif bir şekilde açıkla.'
            },
            {
                'name': 'gemini',
                'display_name': 'Google Gemini',
                'max_tokens': 1000,
                'temperature': 0.8,
                'system_prompt': 'Sen deneyimli bir tarot okuyucususun. Kartları yaratıcı ve derinlemesine yorumla.'
            }
        ]
        
        for provider_data in providers:
            provider, created = AIProvider.objects.get_or_create(
                name=provider_data['name'],
                defaults=provider_data
            )
            if created:
                self.stdout.write(f'AI sağlayıcı oluşturuldu: {provider.display_name}')
            else:
                self.stdout.write(f'AI sağlayıcı zaten mevcut: {provider.display_name}')

    def create_tarot_spreads(self):
        """Temel tarot yayılımları oluştur"""
        spreads = [
            {
                'name': 'Tek Kart',
                'slug': 'single-card',
                'description': 'Günlük rehberlik için tek kart çekimi',
                'card_count': 1,
                'positions': {
                    '1': 'Ana mesaj'
                },
                'difficulty_level': 'beginner'
            },
            {
                'name': 'Üç Kart - Geçmiş, Şimdi, Gelecek',
                'slug': 'three-card',
                'description': 'Klasik üç kart yayılımı',
                'card_count': 3,
                'positions': {
                    '1': 'Geçmiş',
                    '2': 'Şimdi',
                    '3': 'Gelecek'
                },
                'difficulty_level': 'beginner'
            },
            {
                'name': 'Aşk Yayılımı',
                'slug': 'love-spread',
                'description': 'Aşk ve ilişkiler için özel yayılım',
                'card_count': 4,
                'positions': {
                    '1': 'Şu anki durum',
                    '2': 'Partner hakkında',
                    '3': 'İlişkinin gidişatı',
                    '4': 'Tavsiye'
                },
                'difficulty_level': 'intermediate'
            },
            {
                'name': 'Kariyer Yayılımı',
                'slug': 'career-spread',
                'description': 'İş ve kariyer rehberliği',
                'card_count': 5,
                'positions': {
                    '1': 'Mevcut durum',
                    '2': 'Güçlü yanlar',
                    '3': 'Zorluklar',
                    '4': 'Fırsatlar',
                    '5': 'Sonuç'
                },
                'difficulty_level': 'intermediate'
            },
            {
                'name': 'Kelt Haçı',
                'slug': 'celtic-cross',
                'description': 'En detaylı tarot yayılımı',
                'card_count': 10,
                'positions': {
                    '1': 'Şu anki durum',
                    '2': 'Zorluk',
                    '3': 'Uzak geçmiş',
                    '4': 'Yakın geçmiş',
                    '5': 'Olası gelecek',
                    '6': 'Yakın gelecek',
                    '7': 'Yaklaşımınız',
                    '8': 'Çevre etkisi',
                    '9': 'Umutlar ve korkular',
                    '10': 'Nihai sonuç'
                },
                'difficulty_level': 'advanced'
            }
        ]
        
        for spread_data in spreads:
            spread, created = TarotSpread.objects.get_or_create(
                slug=spread_data['slug'],
                defaults=spread_data
            )
            if created:
                self.stdout.write(f'Tarot yayılımı oluşturuldu: {spread.name}')
            else:
                self.stdout.write(f'Tarot yayılımı zaten mevcut: {spread.name}')

    def create_basic_tarot_cards(self):
        """Temel tarot kartları oluştur"""
        # Major Arcana kartları
        major_arcana = [
            {'name': 'Deli', 'name_en': 'The Fool', 'number': 0},
            {'name': 'Büyücü', 'name_en': 'The Magician', 'number': 1},
            {'name': 'Yüksek Rahibe', 'name_en': 'The High Priestess', 'number': 2},
            {'name': 'İmparatoriçe', 'name_en': 'The Empress', 'number': 3},
            {'name': 'İmparator', 'name_en': 'The Emperor', 'number': 4},
            {'name': 'Hierophant', 'name_en': 'The Hierophant', 'number': 5},
            {'name': 'Aşıklar', 'name_en': 'The Lovers', 'number': 6},
            {'name': 'Savaş Arabası', 'name_en': 'The Chariot', 'number': 7},
            {'name': 'Güç', 'name_en': 'Strength', 'number': 8},
            {'name': 'Ermiş', 'name_en': 'The Hermit', 'number': 9},
            {'name': 'Kader Çarkı', 'name_en': 'Wheel of Fortune', 'number': 10},
            {'name': 'Adalet', 'name_en': 'Justice', 'number': 11},
            {'name': 'Asılan Adam', 'name_en': 'The Hanged Man', 'number': 12},
            {'name': 'Ölüm', 'name_en': 'Death', 'number': 13},
            {'name': 'Ölçülülük', 'name_en': 'Temperance', 'number': 14},
            {'name': 'Şeytan', 'name_en': 'The Devil', 'number': 15},
            {'name': 'Kule', 'name_en': 'The Tower', 'number': 16},
            {'name': 'Yıldız', 'name_en': 'The Star', 'number': 17},
            {'name': 'Ay', 'name_en': 'The Moon', 'number': 18},
            {'name': 'Güneş', 'name_en': 'The Sun', 'number': 19},
            {'name': 'Yargı', 'name_en': 'Judgement', 'number': 20},
            {'name': 'Dünya', 'name_en': 'The World', 'number': 21},
        ]
        
        for card_data in major_arcana:
            card, created = TarotCard.objects.get_or_create(
                suit='major',
                number=card_data['number'],
                defaults={
                    'name': card_data['name'],
                    'name_en': card_data['name_en'],
                    'upright_meaning': f"{card_data['name']} kartının düz anlamı",
                    'reversed_meaning': f"{card_data['name']} kartının ters anlamı",
                    'description': f"{card_data['name']} kartının detaylı açıklaması"
                }
            )
            if created:
                self.stdout.write(f'Tarot kartı oluşturuldu: {card.name}')

        # Basit Minor Arcana örneği (sadece As'lar)
        suits = [
            ('cups', 'Kupa'),
            ('pentacles', 'Tılsım'),
            ('swords', 'Kılıç'),
            ('wands', 'Değnek')
        ]
        
        for suit_en, suit_tr in suits:
            card, created = TarotCard.objects.get_or_create(
                suit=suit_en,
                number=1,
                defaults={
                    'name': f'{suit_tr} Ası',
                    'name_en': f'Ace of {suit_en.title()}',
                    'upright_meaning': f'{suit_tr} Ası düz anlam',
                    'reversed_meaning': f'{suit_tr} Ası ters anlam',
                    'description': f'{suit_tr} Ası açıklaması'
                }
            )
            if created:
                self.stdout.write(f'Tarot kartı oluşturuldu: {card.name}')

        self.stdout.write(self.style.SUCCESS('Temel tarot kartları oluşturuldu.'))