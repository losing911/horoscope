from django.contrib import admin
from django.contrib import messages
from django.utils import timezone
from django.urls import path
from django.shortcuts import redirect
from .models import (
    ZodiacSign, DailyHoroscope, WeeklyHoroscope, 
    MonthlyHoroscope, CompatibilityReading, BirthChart,
    MoonSign, Ascendant, PersonalHoroscope,
    UserDailyHoroscope, UserWeeklyHoroscope, UserMonthlyHoroscope
)
from .views import generate_daily_horoscope


# Custom admin site configuration
class HoroscopeAdminSite(admin.AdminSite):
    site_header = "Burç Yönetim Paneli"
    site_title = "Burç Admin"
    index_title = "Hoş Geldiniz"
    
    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        
        # Custom links ekle
        app_list += [
            {
                "name": "Burç Görselleri",
                "app_label": "horoscope_images",
                "models": [
                    {
                        "name": "Instagram Görselleri",
                        "object_name": "horoscope_images",
                        "admin_url": "/admin/horoscope-images/",
                        "view_only": True,
                    }
                ],
            }
        ]
        
        return app_list


# Use custom admin site (optional - sadece özelleştirilmiş menü için)
# admin_site = HoroscopeAdminSite(name='horoscope_admin')



@admin.register(ZodiacSign)
class ZodiacSignAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_en', 'symbol', 'element', 'quality', 'token_cost', 'is_premium_only', 'order']
    list_filter = ['element', 'quality', 'is_premium_only', 'token_cost']
    search_fields = ['name', 'name_en']
    ordering = ['order']
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'name_en', 'symbol', 'element', 'quality', 'ruling_planet', 'order')
        }),
        ('Tarih Bilgileri', {
            'fields': ('date_range', 'start_month', 'start_day', 'end_month', 'end_day')
        }),
        ('Açıklamalar', {
            'fields': ('description', 'traits', 'strengths', 'weaknesses', 'compatibility')
        }),
        ('Şans Faktörleri', {
            'fields': ('lucky_numbers', 'lucky_colors', 'lucky_day')
        }),
        ('💰 Jeton Ayarları', {
            'fields': ('token_cost', 'is_premium_only'),
            'description': '<div style="background:#e3f2fd;padding:12px;border-radius:8px;margin:10px 0;">'
                          '<strong>📊 Jeton Maliyeti:</strong><br>'
                          '• Jeton Maliyeti: Bu burçtan detaylı analiz almak için gereken jeton sayısı (0 = Ücretsiz)<br>'
                          '• Sadece Premium: İşaretlenirse yalnızca premium üyelere açık<br>'
                          '<strong>Örnekler:</strong><br>'
                          '- Günlük Burç: 0 jeton (ücretsiz)<br>'
                          '- Haftalık Analiz: 5 jeton<br>'
                          '- Doğum Haritası: 20 jeton</div>'
        }),
        ('Görsel', {
            'fields': ('image_url',)
        }),
    )


@admin.register(DailyHoroscope)
class DailyHoroscopeAdmin(admin.ModelAdmin):
    list_display = ['zodiac_sign', 'date', 'mood_score', 'lucky_number', 'ai_provider', 'created_at']
    list_filter = ['date', 'zodiac_sign', 'ai_provider']
    search_fields = ['zodiac_sign__name']
    date_hierarchy = 'date'
    ordering = ['-date', 'zodiac_sign']
    actions = ['generate_horoscopes_for_today']

    @admin.action(description="🌟 Bugün için tüm burçların günlük yorumunu oluştur (AI)")
    def generate_horoscopes_for_today(self, request, queryset):
        """Tüm burçlar için bugünün günlük yorumunu oluşturur"""
        today = timezone.now().date()
        zodiac_signs = ZodiacSign.objects.all().order_by('order')
        
        created_count = 0
        updated_count = 0
        error_count = 0
        fallback_count = 0
        quota_exceeded = False
        
        for sign in zodiac_signs:
            try:
                # Bugün için yorum var mı kontrol et
                existing = DailyHoroscope.objects.filter(
                    zodiac_sign=sign,
                    date=today
                ).first()
                
                if existing:
                    # Varolan yorumu sil ve yeniden oluştur
                    existing.delete()
                    result = generate_daily_horoscope(sign, today)
                    if result:
                        # Fallback içerik mi kontrol et
                        if result.general.startswith('[FALLBACK]') or result.general == "Bugün sizin için güzel bir gün olacak.":
                            fallback_count += 1
                        else:
                            updated_count += 1
                    else:
                        error_count += 1
                else:
                    # Yeni yorum oluştur
                    result = generate_daily_horoscope(sign, today)
                    if result:
                        # Fallback içerik mi kontrol et
                        if result.general.startswith('[FALLBACK]') or result.general == "Bugün sizin için güzel bir gün olacak.":
                            fallback_count += 1
                        else:
                            created_count += 1
                    else:
                        error_count += 1
                        
            except Exception as e:
                error_str = str(e)
                # Quota hatası mı kontrol et
                if '429' in error_str or 'quota' in error_str.lower() or 'ResourceExhausted' in error_str:
                    quota_exceeded = True
                    
                error_count += 1
                # İlk 3 hata için detay göster
                if error_count <= 3:
                    self.message_user(
                        request,
                        f"❌ {sign.name} için hata: {error_str[:200]}",
                        level=messages.ERROR
                    )
        
        # Özet mesaj
        total = created_count + updated_count
        
        if quota_exceeded:
            self.message_user(
                request,
                "🚫 GEMINI API QUOTA AŞILDI!\n\n"
                "❌ Günlük 50 istek limitine ulaştınız.\n"
                "⏰ 24 saat sonra tekrar deneyin veya ücretli plana geçin.\n"
                "📄 Detaylar için: GEMINI_QUOTA_SORUNU.md dosyasına bakın.",
                level=messages.ERROR
            )
        elif fallback_count > 0:
            self.message_user(
                request,
                f"⚠️ UYARI: {fallback_count} burç için fallback içerik kullanıldı!\n\n"
                "Muhtemelen API quota'sı doldu veya başka bir hata oluştu.\n"
                f"✅ AI ile oluşturulan: {total}\n"
                f"⚠️ Fallback içerik: {fallback_count}\n"
                f"❌ Tamamen başarısız: {error_count}\n\n"
                "📄 Detaylar için: GEMINI_QUOTA_SORUNU.md dosyasına bakın.",
                level=messages.WARNING
            )
        elif total > 0:
            success_msg = "✅ Başarıyla tamamlandı! "
            if created_count > 0:
                success_msg += f"🆕 Yeni: {created_count} "
            if updated_count > 0:
                success_msg += f"🔄 Güncellenen: {updated_count} "
            if error_count > 0:
                success_msg += f"❌ Hata: {error_count}"
            
            self.message_user(request, success_msg, level=messages.SUCCESS)
        else:
            self.message_user(
                request,
                f"❌ Hiçbir yorum oluşturulamadı. Hata sayısı: {error_count}\n"
                "Lütfen sunucu loglarını kontrol edin.",
                level=messages.ERROR
            )


@admin.register(WeeklyHoroscope)
class WeeklyHoroscopeAdmin(admin.ModelAdmin):
    list_display = ['zodiac_sign', 'week_start', 'week_end', 'ai_provider', 'created_at']
    list_filter = ['week_start', 'zodiac_sign', 'ai_provider']
    search_fields = ['zodiac_sign__name']
    date_hierarchy = 'week_start'
    ordering = ['-week_start', 'zodiac_sign']


@admin.register(MonthlyHoroscope)
class MonthlyHoroscopeAdmin(admin.ModelAdmin):
    list_display = ['zodiac_sign', 'month', 'year', 'ai_provider', 'created_at']
    list_filter = ['year', 'month', 'zodiac_sign', 'ai_provider']
    search_fields = ['zodiac_sign__name']
    ordering = ['-year', '-month', 'zodiac_sign']


@admin.register(CompatibilityReading)
class CompatibilityReadingAdmin(admin.ModelAdmin):
    list_display = ['user', 'sign1', 'sign2', 'compatibility_score', 'ai_provider', 'created_at']
    list_filter = ['created_at', 'sign1', 'sign2', 'ai_provider']
    search_fields = ['user__username', 'sign1__name', 'sign2__name']
    ordering = ['-created_at']


@admin.register(BirthChart)
class BirthChartAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'birth_date', 'sun_sign', 'moon_sign', 'rising_sign', 'created_at']
    list_filter = ['created_at', 'sun_sign', 'moon_sign', 'rising_sign']
    search_fields = ['name', 'user__username', 'birth_place']
    date_hierarchy = 'birth_date'
    ordering = ['-created_at']
    fieldsets = (
        ('Kullanıcı Bilgileri', {
            'fields': ('user', 'name')
        }),
        ('Doğum Bilgileri', {
            'fields': ('birth_date', 'birth_time', 'birth_place', 'latitude', 'longitude')
        }),
        ('Ana Burçlar', {
            'fields': ('sun_sign', 'moon_sign', 'rising_sign')
        }),
        ('Analizler', {
            'fields': ('personality_analysis', 'emotional_analysis', 'career_analysis', 
                      'relationship_analysis', 'life_path_analysis')
        }),
        ('Detaylı Pozisyonlar', {
            'fields': ('planet_positions', 'house_positions', 'aspects'),
            'classes': ('collapse',)
        }),
        ('Diğer', {
            'fields': ('ai_provider',)
        }),
    )


@admin.register(MoonSign)
class MoonSignAdmin(admin.ModelAdmin):
    list_display = ['user', 'moon_sign', 'birth_date', 'birth_time', 'birth_place', 'created_at']
    list_filter = ['moon_sign', 'created_at']
    search_fields = ['user__username', 'birth_place']
    date_hierarchy = 'birth_date'
    ordering = ['-created_at']


@admin.register(Ascendant)
class AscendantAdmin(admin.ModelAdmin):
    list_display = ['user', 'ascendant_sign', 'birth_date', 'birth_time', 'birth_place', 'created_at']
    list_filter = ['ascendant_sign', 'created_at']
    search_fields = ['user__username', 'birth_place']
    date_hierarchy = 'birth_date'
    ordering = ['-created_at']


@admin.register(PersonalHoroscope)
class PersonalHoroscopeAdmin(admin.ModelAdmin):
    list_display = ['user', 'sun_sign', 'moon_sign', 'ascendant_sign', 'birth_date', 'created_at']
    list_filter = ['sun_sign', 'moon_sign', 'ascendant_sign']
    search_fields = ['user__username', 'birth_place']
    date_hierarchy = 'birth_date'
    ordering = ['-created_at']
    fieldsets = (
        ('Kullanıcı', {
            'fields': ('user',)
        }),
        ('Doğum Bilgileri', {
            'fields': ('birth_date', 'birth_time', 'birth_place')
        }),
        ('Burçlar', {
            'fields': ('sun_sign', 'moon_sign', 'ascendant_sign')
        }),
        ('Yorum', {
            'fields': ('interpretation',)
        }),
    )


@admin.register(UserDailyHoroscope)
class UserDailyHoroscopeAdmin(admin.ModelAdmin):
    list_display = ['user', 'zodiac_sign', 'date', 'mood_score', 'lucky_number', 'ai_provider', 'created_at']
    list_filter = ['date', 'zodiac_sign', 'ai_provider']
    search_fields = ['user__username', 'zodiac_sign__name']
    date_hierarchy = 'date'
    ordering = ['-date']


@admin.register(UserWeeklyHoroscope)
class UserWeeklyHoroscopeAdmin(admin.ModelAdmin):
    list_display = ['user', 'zodiac_sign', 'week_start', 'week_end', 'ai_provider', 'created_at']
    list_filter = ['week_start', 'zodiac_sign', 'ai_provider']
    search_fields = ['user__username', 'zodiac_sign__name']
    date_hierarchy = 'week_start'
    ordering = ['-week_start']


@admin.register(UserMonthlyHoroscope)
class UserMonthlyHoroscopeAdmin(admin.ModelAdmin):
    list_display = ['user', 'zodiac_sign', 'month', 'year', 'ai_provider', 'created_at']
    list_filter = ['year', 'month', 'zodiac_sign', 'ai_provider']
    search_fields = ['user__username', 'zodiac_sign__name']
    ordering = ['-year', '-month']
