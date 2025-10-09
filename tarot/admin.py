from django.contrib import admin
from django import forms
from .models import TarotCard, TarotSpread, TarotReading, DailyCard, SiteSettings, AIProvider

class SiteSettingsAdminForm(forms.ModelForm):
    """Site ayarları için özel form"""
    
    class Meta:
        model = SiteSettings
        fields = '__all__'
        widgets = {
            'openai_model': forms.RadioSelect(attrs={
                'class': 'model-selector',
            }),
            'gemini_model': forms.RadioSelect(attrs={
                'class': 'model-selector',
            }),
        }
        help_texts = {
            'default_ai_provider': '🤖 AstroTarot AI motor seçimi',
            'openai_model': '🎯 AstroTarot AI model seçimi - Maliyet ve kalite dengesine göre seçim yapın',
            'gemini_model': '🆓 AstroTarot AI alternatif motor - Günlük limit vardır (50 istek)',
        }

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
            'fields': ('site_title', 'site_description', 'site_keywords')
        }),
        ('🤖 AI Servis Ayarları', {
            'fields': (
                'default_ai_provider',
                'openai_api_key',
                'openai_model',
                'gemini_api_key', 
                'gemini_model',
                'ai_response_max_length'
            ),
            'description': '<div style="background:#e8f5e9;padding:15px;border-radius:8px;margin:10px 0;">'
                          '<strong>🤖 AstroTarot AI Model Rehberi:</strong><br>'
                          '<b>Standard (gpt-4o-mini):</b> Hızlı, ekonomik, günlük kullanım (~$0.001/yorum) ✅<br>'
                          '<b>Advanced (gpt-4o):</b> Daha güçlü, karmaşık yorumlar (~$0.01/yorum)<br>'
                          '<b>Expert (o1/o1-mini):</b> En akıllı, çok detaylı analiz (~$0.10/yorum)<br>'
                          '<b>Alternative Engine:</b> Ücretsiz, günde 50 istek limiti</div>'
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

@admin.register(AIProvider)
class AIProviderAdmin(admin.ModelAdmin):
    """AI Sağlayıcı admin paneli"""
    list_display = ('display_name', 'name', 'is_active', 'max_tokens', 'temperature')
    list_filter = ('is_active',)
    search_fields = ('name', 'display_name')
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'display_name', 'is_active')
        }),
        ('API Ayarları', {
            'fields': ('api_key', 'max_tokens', 'temperature')
        }),
        ('Sistem Mesajı', {
            'fields': ('system_prompt',),
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
    list_display = ('name', 'card_count', 'difficulty_level', 'is_active', 'created_at')
    list_filter = ('difficulty_level', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {"slug": ("name",)}
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'slug', 'description', 'card_count')
        }),
        ('Ayarlar', {
            'fields': ('difficulty_level', 'is_active')
        }),
        ('Pozisyon Anlamları', {
            'fields': ('positions',),
            'description': 'JSON formatında pozisyon anlamları'
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
