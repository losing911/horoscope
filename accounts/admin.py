from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, TokenPackage, TokenTransaction
from .legal_models import LegalDocument, UserConsent, DataDeletionRequest, ContactMessage
from .forms import CustomUserCreationForm, CustomUserChangeForm


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Özelleştirilmiş kullanıcı admin paneli"""
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    
    list_display = ('username', 'email', 'tokens', 'is_premium', 'daily_reading_limit', 'is_staff')
    list_filter = ('is_premium', 'preferred_ai_provider', 'zodiac_sign', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Premium & Jeton Sistemi', {
            'fields': ('tokens', 'is_premium', 'premium_until', 'daily_reading_limit')
        }),
        ('Astroloji Bilgileri', {
            'fields': ('birth_date', 'zodiac_sign', 'preferred_ai_provider')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Premium & Jeton Sistemi', {
            'fields': ('tokens', 'is_premium', 'premium_until', 'daily_reading_limit')
        }),
        ('Astroloji Bilgileri', {
            'fields': ('email', 'birth_date', 'zodiac_sign', 'preferred_ai_provider')
        }),
    )


@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):
    """Yasal Belgeler Yönetimi"""
    list_display = ('title', 'document_type', 'version', 'effective_date', 'is_active', 'last_updated')
    list_filter = ('document_type', 'is_active', 'effective_date')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'effective_date'


@admin.register(UserConsent)
class UserConsentAdmin(admin.ModelAdmin):
    """Kullanıcı Onayları"""
    list_display = ('user', 'document', 'document_version', 'consent_given', 'consent_date', 'ip_address')
    list_filter = ('consent_given', 'document__document_type', 'consent_date')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('consent_date', 'ip_address', 'user_agent')
    date_hierarchy = 'consent_date'


@admin.register(DataDeletionRequest)
class DataDeletionRequestAdmin(admin.ModelAdmin):
    """Veri Silme Talepleri (KVKK)"""
    list_display = ('user', 'request_date', 'status', 'processed_date', 'processed_by')
    list_filter = ('status', 'request_date', 'processed_date')
    search_fields = ('user__username', 'user__email', 'reason')
    readonly_fields = ('request_date',)
    date_hierarchy = 'request_date'
    
    fieldsets = (
        ('Talep Bilgileri', {
            'fields': ('user', 'request_date', 'reason')
        }),
        ('İşlem Bilgileri', {
            'fields': ('status', 'processed_date', 'processed_by', 'admin_notes')
        }),
    )


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """İletişim Mesajları"""
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read', 'is_replied')
    list_filter = ('is_read', 'is_replied', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at', 'ip_address')
    date_hierarchy = 'created_at'
    
    actions = ['mark_as_read', 'mark_as_replied']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Okundu olarak işaretle"
    
    def mark_as_replied(self, request, queryset):
        queryset.update(is_replied=True)
    mark_as_replied.short_description = "Yanıtlandı olarak işaretle"


@admin.register(TokenPackage)
class TokenPackageAdmin(admin.ModelAdmin):
    """Jeton Paketleri Yönetimi"""
    list_display = ('name', 'token_amount', 'bonus_tokens', 'total_tokens', 'price', 'price_usd', 'per_token_price', 'is_active', 'display_order')
    list_filter = ('is_active',)
    search_fields = ('name',)
    list_editable = ('is_active', 'display_order')
    ordering = ('display_order', 'price')


@admin.register(TokenTransaction)
class TokenTransactionAdmin(admin.ModelAdmin):
    """Jeton İşlem Geçmişi"""
    list_display = ('user', 'transaction_type', 'amount', 'balance_before', 'balance_after', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('user__username', 'user__email', 'description')
    readonly_fields = ('created_at', 'balance_before', 'balance_after')
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        # İşlem kayıtları manuel oluşturulamaz
        return False
    
    def has_delete_permission(self, request, obj=None):
        # İşlem kayıtları silinemez
        return False
