from django.contrib import admin
from django import forms
from .models import TarotCard, TarotSpread, TarotReading, DailyCard, SiteSettings, HeroSection


@admin.register(HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    """Hero bölümü admin paneli"""
    list_display = ('title_line1', 'is_active', 'show_announcement', 'show_video', 'updated_at')
    list_filter = ('is_active', 'show_announcement', 'show_video')
    search_fields = ('title_line1', 'title_line2', 'subtitle', 'video_title')
    
    fieldsets = (
        ('📋 Ana Başlık', {
            'fields': ('title_line1', 'title_line2'),
            'description': 'Hero bölümünün ana başlık satırları'
        }),
        ('📝 Alt Başlık', {
            'fields': ('subtitle',),
        }),
        ('🎬 YouTube Video', {
            'fields': ('show_video', 'video_url', 'video_title'),
            'description': '<div style="background:#e3f2fd;padding:12px;border-radius:8px;margin:10px 0;">'
                          '<strong>🎥 Video Ekleme:</strong><br>'
                          '1. YouTube video URL\'sini yapıştırın (watch?v= veya youtu.be/ formatında)<br>'
                          '2. Video başlığı opsiyoneldir (boş bırakılırsa YouTube\'dan alınır)<br>'
                          '3. Video kartların yerine sağ tarafta gösterilir<br>'
                          '<strong>Örnek:</strong> https://www.youtube.com/watch?v=dQw4w9WgXcQ</div>',
            'classes': ('collapse',)
        }),
        ('📢 Duyuru/Bildirim', {
            'fields': ('show_announcement', 'announcement_text', 'announcement_icon', 'announcement_link', 'announcement_color'),
            'description': '<div style="background:#fff3cd;padding:12px;border-radius:8px;margin:10px 0;">'
                          '<strong>💡 İpucu:</strong> Yeni video veya önemli güncellemeleri duyurmak için kullanın.<br>'
                          '<strong>Font Awesome İkonlar:</strong> fas fa-video, fas fa-star, fas fa-gift, vb.</div>',
            'classes': ('collapse',)
        }),
        ('🔘 Butonlar', {
            'fields': ('primary_button_text', 'primary_button_url', 'secondary_button_text', 'secondary_button_url'),
            'classes': ('collapse',)
        }),
        ('🎨 Görsel Ayarlar', {
            'fields': ('background_gradient_start', 'background_gradient_end'),
            'description': 'Hex renk kodları kullanın (örn: #6B1B3D)',
            'classes': ('collapse',)
        }),
        ('⚙️ Durum', {
            'fields': ('is_active',),
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # Yeni kayıt aktif olarak kaydedildiğinde diğerlerini pasif yap
        if obj.is_active:
            HeroSection.objects.exclude(pk=obj.pk).update(is_active=False)
        super().save_model(request, obj, form, change)


class SiteSettingsAdminForm(forms.ModelForm):
    """Site ayarları için özel form"""
    
    class Meta:
        model = SiteSettings
        fields = '__all__'

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Site ayarları admin paneli"""
    form = SiteSettingsAdminForm
    
    def has_add_permission(self, request):
        # Singleton - sadece bir kayıt olabilir
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Singleton - silinmesine izin verme
        return False
    
    class Media:
        css = {
            'all': ('css/admin_model_selector.css',)
        }
    
    fieldsets = (
        ('Genel Ayarlar', {
            'fields': ('site_title', 'site_description', 'site_keywords'),
            'description': '<div style="background:#e8f5e9;padding:15px;border-radius:8px;margin:10px 0;">'
                          '<strong>🤖 AI Ayarları:</strong><br>'
                          'OpenRouter.ai üzerinden tek bir API ile tüm AI modellerine erişim sağlanıyor.<br>'
                          'AI yapılandırması artık .env dosyası üzerinden yapılmaktadır.</div>'
        }),
        ('Kullanıcı Limitleri', {
            'fields': ('daily_reading_limit', 'max_question_length'),
            'classes': ('collapse',)
        }),
        ('Site Durumu', {
            'fields': ('maintenance_mode', 'maintenance_message', 'allow_registration', 'allow_guest_reading'),
            'classes': ('collapse',)
        }),
        ('İletişim Bilgileri', {
            'fields': ('contact_email', 'support_phone'),
            'classes': ('collapse',)
        }),
        ('Sosyal Medya', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url'),
            'classes': ('collapse',)
        }),
        ('Cache Ayarları', {
            'fields': ('cache_timeout',),
            'classes': ('collapse',)
        }),
    )

@admin.register(TarotCard)
class TarotCardAdmin(admin.ModelAdmin):
    list_display = ('name', 'suit', 'number', 'name_en')
    list_filter = ('suit',)
    search_fields = ('name', 'name_en')
    ordering = ('suit', 'number')
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'name_en', 'suit', 'number', 'image_url')
        }),
        ('Anlamlar', {
            'fields': ('upright_meaning', 'reversed_meaning', 'description')
        }),
    )

@admin.register(TarotSpread)
class TarotSpreadAdmin(admin.ModelAdmin):
    list_display = ('name', 'card_count', 'difficulty_level', 'token_cost', 'is_premium_only', 'is_active', 'created_at')
    list_filter = ('difficulty_level', 'is_active', 'is_premium_only', 'token_cost')
    search_fields = ('name', 'description')
    prepopulated_fields = {"slug": ("name",)}
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'slug', 'description', 'card_count')
        }),
        ('Ayarlar', {
            'fields': ('difficulty_level', 'is_active')
        }),
        ('💰 Jeton Ayarları', {
            'fields': ('token_cost', 'is_premium_only'),
            'description': '<div style="background:#e3f2fd;padding:12px;border-radius:8px;margin:10px 0;">'
                          '<strong>📊 Jeton Maliyeti:</strong><br>'
                          '• Jeton Maliyeti: Bu yayılımı kullanmak için gereken jeton sayısı (0 = Ücretsiz)<br>'
                          '• Sadece Premium: İşaretlenirse yalnızca premium üyelere açık<br>'
                          '<strong>Örnekler:</strong><br>'
                          '- Günlük Kart: 0 jeton (ücretsiz)<br>'
                          '- 3 Kartlı Yayılım: 5 jeton<br>'
                          '- Hayat Yolculuğu: 15 jeton</div>'
        }),
        ('Pozisyon Anlamları', {
            'fields': ('positions',),
            'description': 'JSON formatında pozisyon anlamları',
            'classes': ('collapse',)
        }),
    )

@admin.register(TarotReading)
class TarotReadingAdmin(admin.ModelAdmin):
    list_display = ('user', 'spread', 'ai_provider', 'is_public', 'created_at')
    list_filter = ('ai_provider', 'is_public', 'spread', 'created_at')
    search_fields = ('user__username', 'question')
    readonly_fields = ('id', 'created_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Okuma Bilgileri', {
            'fields': ('user', 'spread', 'question', 'ai_provider')
        }),
        ('Sonuçlar', {
            'fields': ('cards', 'interpretation'),
            'classes': ('collapse',)
        }),
        ('Ayarlar', {
            'fields': ('is_public',)
        }),
        ('Sistem', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(DailyCard)
class DailyCardAdmin(admin.ModelAdmin):
    list_display = ('user', 'card', 'date', 'is_reversed', 'ai_provider')
    list_filter = ('is_reversed', 'ai_provider', 'date')
    search_fields = ('user__username', 'card__name')
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Kart Bilgileri', {
            'fields': ('user', 'card', 'date', 'is_reversed')
        }),
        ('Yorum', {
            'fields': ('interpretation', 'ai_provider')
        }),
    )
