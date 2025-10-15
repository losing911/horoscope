from django.core.management.base import BaseCommand
from django.utils import timezone
from zodiac.models import ZodiacSign, MonthlyHoroscope
from zodiac.services import ZodiacAIService


class Command(BaseCommand):
    help = 'Aylık burç yorumlarını oluşturur'

    def add_arguments(self, parser):
        parser.add_argument(
            '--year',
            type=int,
            help='Yıl (Belirtilmezse şu anki yıl kullanılır)'
        )
        parser.add_argument(
            '--month',
            type=int,
            help='Ay (1-12 arası. Belirtilmezse şu anki ay kullanılır)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Mevcut yorumları güncelle'
        )

    def handle(self, *args, **options):
        # Yıl ve ay belirleme
        today = timezone.now().date()
        year = options['year'] or today.year
        month = options['month'] or today.month

        if month < 1 or month > 12:
            self.stdout.write(self.style.ERROR("❌ Ay değeri 1-12 arasında olmalıdır!"))
            return

        month_names = ['', 'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran',
                       'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
        
        self.stdout.write(f"📅 Dönem: {month_names[month]} {year}")
        self.stdout.write("🌟 Aylık burç yorumları oluşturuluyor...\n")

        ai_service = ZodiacAIService()
        zodiac_signs = ZodiacSign.objects.all().order_by('order')
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0

        for sign in zodiac_signs:
            try:
                # Mevcut yorum var mı kontrol et
                existing = MonthlyHoroscope.objects.filter(
                    zodiac_sign=sign,
                    year=year,
                    month=month
                ).first()

                if existing and not options['force']:
                    self.stdout.write(f"  ⏭️  {sign.name}: Zaten var, atlanıyor")
                    skipped_count += 1
                    continue

                self.stdout.write(f"  {'🔄' if existing else '🆕'} {sign.name}: {'Güncelleniyor' if existing else 'Oluşturuluyor'}...")

                # AI ile yorum oluştur
                horoscope_data = ai_service.generate_monthly_horoscope(sign, year, month)

                if existing:
                    # Güncelle
                    for key, value in horoscope_data.items():
                        setattr(existing, key, value)
                    existing.save()
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f"  ✓  {sign.name}: Güncellendi"))
                else:
                    # Yeni oluştur
                    MonthlyHoroscope.objects.create(
                        zodiac_sign=sign,
                        year=year,
                        month=month,
                        **horoscope_data
                    )
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f"  ✓  {sign.name}: Oluşturuldu"))

            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f"  ✗  {sign.name}: Hata - {str(e)}"))

        # Özet
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("📊 Özet:")
        self.stdout.write(f"  ✅ Oluşturulan: {created_count}")
        if updated_count > 0:
            self.stdout.write(f"  🔄 Güncellenen: {updated_count}")
        if skipped_count > 0:
            self.stdout.write(f"  ⏭️  Atlanan: {skipped_count}")
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f"  ❌ Hata: {error_count}"))
        self.stdout.write("=" * 50)
