from django.core.management.base import BaseCommand
from django.utils import timezone
from zodiac.models import ZodiacSign, DailyHoroscope
from zodiac.views import generate_daily_horoscope


class Command(BaseCommand):
    help = 'Tüm burçlar için günlük AI yorumları oluşturur'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Var olan yorumları da yeniden oluştur',
        )

    def handle(self, *args, **options):
        today = timezone.now().date()
        force = options.get('force', False)
        
        self.stdout.write(f'📅 Tarih: {today}')
        self.stdout.write('🌟 Günlük burç yorumları oluşturuluyor...\n')
        
        # Tüm burçları al
        zodiac_signs = ZodiacSign.objects.all().order_by('order')
        
        created_count = 0
        skipped_count = 0
        error_count = 0
        
        for sign in zodiac_signs:
            # Var olan yorumu kontrol et
            existing = DailyHoroscope.objects.filter(
                zodiac_sign=sign,
                date=today
            ).first()
            
            if existing and not force:
                self.stdout.write(f'  ⏭️  {sign.name}: Zaten var, atlanıyor')
                skipped_count += 1
                continue
            
            if existing and force:
                existing.delete()
                self.stdout.write(f'  🔄 {sign.name}: Eski yorum siliniyor')
            
            try:
                # Gemini ile yorum oluştur
                horoscope = generate_daily_horoscope(sign, today)
                
                if horoscope:
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✅ {sign.name}: Yorum oluşturuldu')
                    )
                    created_count += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(f'  ⚠️  {sign.name}: Yorum oluşturulamadı')
                    )
                    error_count += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ {sign.name}: Hata - {str(e)}')
                )
                error_count += 1
        
        # Özet
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'📊 Özet:')
        self.stdout.write(f'  ✅ Oluşturulan: {created_count}')
        self.stdout.write(f'  ⏭️  Atlanan: {skipped_count}')
        self.stdout.write(f'  ❌ Hata: {error_count}')
        self.stdout.write('='*50)
        
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\n🎉 {created_count} burç için günlük yorum başarıyla oluşturuldu!')
            )
        
        if error_count > 0:
            self.stdout.write(
                self.style.WARNING(f'\n⚠️  {error_count} burç için yorum oluşturulamadı. Lütfen hataları kontrol edin.')
            )
