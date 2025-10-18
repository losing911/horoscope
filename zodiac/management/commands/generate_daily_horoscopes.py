from django.core.management.base import BaseCommand
from django.utils import timezone
from zodiac.models import ZodiacSign, DailyHoroscope
from zodiac.views import generate_daily_horoscope
import time


class Command(BaseCommand):
    help = 'Tüm burçlar için günlük AI yorumları oluşturur (OpenRouter API ile teker teker)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Var olan yorumları da yeniden oluştur',
        )
        parser.add_argument(
            '--delay',
            type=int,
            default=3,
            help='Her yorum arasında bekleme süresi (saniye). Varsayılan: 3',
        )
        parser.add_argument(
            '--language',
            type=str,
            default='tr',
            choices=['tr', 'en', 'de', 'fr'],
            help='Yorum dili. Varsayılan: tr',
        )

    def handle(self, *args, **options):
        today = timezone.now().date()
        force = options.get('force', False)
        delay = options.get('delay', 3)
        language = options.get('language', 'tr')
        
        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS('🌟 Günlük Burç Yorumları Oluşturucu (OpenRouter API)'))
        self.stdout.write('='*60)
        self.stdout.write(f'📅 Tarih: {today}')
        self.stdout.write(f'� Dil: {language.upper()}')
        self.stdout.write(f'⏱️  Bekleme süresi: {delay} saniye')
        self.stdout.write(f'🔄 Force mode: {"Açık" if force else "Kapalı"}')
        self.stdout.write('='*60 + '\n')
        
        # Tüm burçları al
        zodiac_signs = ZodiacSign.objects.all().order_by('order')
        total_signs = zodiac_signs.count()
        
        created_count = 0
        skipped_count = 0
        error_count = 0
        
        for index, sign in enumerate(zodiac_signs, 1):
            self.stdout.write(f'\n[{index}/{total_signs}] 🌟 {sign.name}')
            self.stdout.write('-' * 40)
            
            # Var olan yorumu kontrol et
            existing = DailyHoroscope.objects.filter(
                zodiac_sign=sign,
                date=today
            ).first()
            
            if existing and not force:
                self.stdout.write(self.style.WARNING(f'  ⏭️  Zaten var, atlanıyor...'))
                skipped_count += 1
                continue
            
            if existing and force:
                existing.delete()
                self.stdout.write(f'  �️  Eski yorum silindi')
            
            try:
                # Yorum oluşturma başladı
                self.stdout.write(f'  🤖 AI ile yorum oluşturuluyor...')
                start_time = time.time()
                
                # OpenRouter API ile yorum oluştur
                horoscope = generate_daily_horoscope(sign, today, language)
                
                elapsed_time = time.time() - start_time
                
                if horoscope:
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✅ Başarılı! ({elapsed_time:.2f} saniye)')
                    )
                    self.stdout.write(f'     📝 Genel: {horoscope.general[:50]}...')
                    created_count += 1
                    
                    # Kotaya takılmamak için bekleme
                    if index < total_signs:  # Son burç değilse
                        self.stdout.write(f'  ⏳ {delay} saniye bekleniyor...')
                        time.sleep(delay)
                else:
                    self.stdout.write(
                        self.style.WARNING(f'  ⚠️  Yorum oluşturulamadı')
                    )
                    error_count += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Hata: {str(e)}')
                )
                error_count += 1
                
                # Hata durumunda biraz daha uzun bekle
                if index < total_signs:
                    self.stdout.write(f'  ⏳ Hata sonrası {delay * 2} saniye bekleniyor...')
                    time.sleep(delay * 2)
        
        # Özet
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('📊 İŞLEM ÖZETİ'))
        self.stdout.write('='*60)
        self.stdout.write(f'  📅 Tarih: {today}')
        self.stdout.write(f'  🌍 Dil: {language.upper()}')
        self.stdout.write(f'  📊 Toplam burç: {total_signs}')
        self.stdout.write(f'  ✅ Oluşturulan: {created_count}')
        self.stdout.write(f'  ⏭️  Atlanan: {skipped_count}')
        self.stdout.write(f'  ❌ Hata: {error_count}')
        
        # Başarı oranı
        if total_signs > 0:
            success_rate = (created_count / (total_signs - skipped_count) * 100) if (total_signs - skipped_count) > 0 else 0
            self.stdout.write(f'  📈 Başarı oranı: {success_rate:.1f}%')
        
        self.stdout.write('='*60)
        
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\n🎉 {created_count} burç için günlük yorum başarıyla oluşturuldu!')
            )
        
        if error_count > 0:
            self.stdout.write(
                self.style.WARNING(f'\n⚠️  {error_count} burç için yorum oluşturulamadı.')
            )
            self.stdout.write('💡 İpucu: --delay parametresini artırarak tekrar deneyin.')
        
        if skipped_count > 0:
            self.stdout.write(
                self.style.WARNING(f'\nℹ️  {skipped_count} burç zaten mevcut olduğu için atlandı.')
            )
            self.stdout.write('💡 İpucu: --force parametresi ile yeniden oluşturabilirsiniz.')

