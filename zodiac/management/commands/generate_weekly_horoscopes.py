from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from zodiac.models import ZodiacSign, WeeklyHoroscope
from zodiac.services import ZodiacAIService


class Command(BaseCommand):
    help = 'Haftalık burç yorumlarını oluşturur'

    def add_arguments(self, parser):
        parser.add_argument(
            '--week-start',
            type=str,
            help='Hafta başlangıç tarihi (YYYY-MM-DD formatında). Belirtilmezse bu haftanın pazartesi kullanılır.'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Mevcut yorumları güncelle'
        )

    def handle(self, *args, **options):
        # Hafta başlangıç tarihini belirle (Pazartesi)
        if options['week_start']:
            from datetime import datetime
            week_start = datetime.strptime(options['week_start'], '%Y-%m-%d').date()
        else:
            today = timezone.now().date()
            week_start = today - timedelta(days=today.weekday())  # Bu haftanın pazartesi

        week_end = week_start + timedelta(days=6)
        
        self.stdout.write(f"📅 Hafta: {week_start.strftime('%d.%m.%Y')} - {week_end.strftime('%d.%m.%Y')}")
        self.stdout.write("🌟 Haftalık burç yorumları oluşturuluyor...\n")

        ai_service = ZodiacAIService()
        zodiac_signs = ZodiacSign.objects.all().order_by('order')
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0

        for sign in zodiac_signs:
            try:
                # Mevcut yorum var mı kontrol et
                existing = WeeklyHoroscope.objects.filter(
                    zodiac_sign=sign,
                    week_start=week_start
                ).first()

                if existing and not options['force']:
                    self.stdout.write(f"  ⏭️  {sign.name}: Zaten var, atlanıyor")
                    skipped_count += 1
                    continue

                self.stdout.write(f"  {'🔄' if existing else '🆕'} {sign.name}: {'Güncelleniyor' if existing else 'Oluşturuluyor'}...")

                # AI ile yorum oluştur
                horoscope_data = ai_service.generate_weekly_horoscope(sign, week_start)

                if existing:
                    # Güncelle
                    for key, value in horoscope_data.items():
                        setattr(existing, key, value)
                    existing.save()
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f"  ✓  {sign.name}: Güncellendi"))
                else:
                    # Yeni oluştur
                    WeeklyHoroscope.objects.create(
                        zodiac_sign=sign,
                        week_start=week_start,
                        week_end=week_end,
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
