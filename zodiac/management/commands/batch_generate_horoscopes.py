"""
Günlük burç yorumlarını toplu olarak oluştur
Her gün sabah 6'da çalıştırılabilir (cron job)
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from zodiac.models import ZodiacSign, DailyHoroscope
from zodiac.views import generate_daily_horoscope
import logging
import time

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Tüm burçlar için günlük yorumları batch olarak oluştur'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Belirli bir tarih için oluştur (YYYY-MM-DD formatında)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Mevcut yorumları yeniden oluştur',
        )
        parser.add_argument(
            '--delay',
            type=int,
            default=15,
            help='Her yorum arasında bekleme süresi (saniye). Varsayılan: 15',
        )

    def handle(self, *args, **options):
        # Tarih belirtildiyse onu kullan, yoksa bugünü al
        if options['date']:
            try:
                target_date = datetime.strptime(options['date'], '%Y-%m-%d').date()
            except ValueError:
                self.stdout.write(self.style.ERROR('❌ Geçersiz tarih formatı! YYYY-MM-DD kullanın.'))
                return
        else:
            target_date = timezone.now().date()
        
        force = options['force']
        delay = options['delay']
        
        self.stdout.write(self.style.SUCCESS(f'\n{"="*60}'))
        self.stdout.write(self.style.SUCCESS(f'  📅 GÜNLÜK BURÇ BATCH GENERATION'))
        self.stdout.write(self.style.SUCCESS(f'{"="*60}\n'))
        self.stdout.write(f'Tarih: {target_date}')
        self.stdout.write(f'Force Mode: {"Evet" if force else "Hayır"}')
        self.stdout.write(f'Delay: {delay} saniye\n')
        
        # Tüm burçları al
        signs = ZodiacSign.objects.all().order_by('name')
        total_signs = signs.count()
        
        if total_signs == 0:
            self.stdout.write(self.style.ERROR('❌ Hiç burç bulunamadı!'))
            return
        
        self.stdout.write(f'Toplam {total_signs} burç için yorum oluşturulacak...\n')
        
        success_count = 0
        skip_count = 0
        error_count = 0
        
        for index, sign in enumerate(signs, 1):
            try:
                # Mevcut yorum var mı kontrol et
                existing = DailyHoroscope.objects.filter(
                    zodiac_sign=sign,
                    date=target_date
                ).exists()
                
                if existing and not force:
                    self.stdout.write(f'⏭️  [{index}/{total_signs}] {sign.symbol} {sign.name} - Zaten mevcut, atlanıyor')
                    skip_count += 1
                    continue
                
                # Yorum oluştur
                self.stdout.write(f'🔮 [{index}/{total_signs}] {sign.symbol} {sign.name} için yorum oluşturuluyor...')
                
                # Mevcut varsa sil (force mode)
                if existing and force:
                    DailyHoroscope.objects.filter(
                        zodiac_sign=sign,
                        date=target_date
                    ).delete()
                    self.stdout.write('   ♻️  Mevcut yorum silindi')
                
                # Yeni yorum oluştur
                horoscope = generate_daily_horoscope(sign, target_date)
                
                if horoscope:
                    success_count += 1
                    provider_emoji = '🤖' if horoscope.ai_provider == 'openai' else '🆓' if horoscope.ai_provider == 'gemini' else '📝'
                    self.stdout.write(self.style.SUCCESS(
                        f'   ✅ Başarılı! (Provider: {provider_emoji} {horoscope.ai_provider})'
                    ))
                    
                    # Son burç değilse bekle
                    if index < total_signs:
                        self.stdout.write(f'   ⏳ {delay} saniye bekleniyor...')
                        time.sleep(delay)
                else:
                    error_count += 1
                    self.stdout.write(self.style.ERROR('   ❌ Yorum oluşturulamadı'))
                
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f'   ❌ Hata: {str(e)}'))
                logger.error(f'Batch generation error for {sign.name}: {e}', exc_info=True)
        
        # Özet
        self.stdout.write(f'\n{"="*60}')
        self.stdout.write(self.style.SUCCESS('  📊 ÖZET'))
        self.stdout.write(f'{"="*60}')
        self.stdout.write(f'✅ Başarılı: {success_count}')
        self.stdout.write(f'⏭️  Atlanan: {skip_count}')
        self.stdout.write(f'❌ Hatalı: {error_count}')
        self.stdout.write(f'{"="*60}\n')
        
        if error_count == 0:
            self.stdout.write(self.style.SUCCESS('🎉 Tüm yorumlar başarıyla oluşturuldu!'))
        elif success_count > 0:
            self.stdout.write(self.style.WARNING('⚠️  Bazı yorumlar oluşturulamadı.'))
        else:
            self.stdout.write(self.style.ERROR('❌ Hiçbir yorum oluşturulamadı!'))
