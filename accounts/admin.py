from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Özelleştirilmiş kullanıcı admin paneli"""
    list_display = ('username', 'email', 'first_name', 'last_name', 'birth_date', 'preferred_ai_provider', 'is_staff')
    list_filter = ('preferred_ai_provider', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Tarot Bilgileri', {
            'fields': ('birth_date', 'preferred_ai_provider', 'daily_reading_limit')
        }),
    )
