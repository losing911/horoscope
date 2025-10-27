from django.urls import path
from . import views
from . import admin_views

app_name = 'tarot'

urlpatterns = [
    # Ana sayfalar
    path('', views.index, name='index'),
    path('spreads/', views.spreads_list, name='spreads'),
    path('spread/<slug:slug>/', views.spread_detail, name='spread_detail'),
    
    # Okuma işlemleri
    path('create-reading/', views.create_reading, name='create_reading'),
    path('reading/<uuid:reading_id>/', views.reading_detail, name='reading_detail'),
    path('reading/<uuid:reading_id>/toggle-public/', views.toggle_reading_public, name='toggle_reading_public'),
    path('my-readings/', views.user_readings, name='user_readings'),
    
    # Özel özellikler
    path('daily-card/', views.daily_card, name='daily_card'),
    path('public-readings/', views.public_readings, name='public_readings'),
    
    # Custom Dashboard URL'leri (Django admin ile çakışmaması için dashboard/ altında)
    path('dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/users/', admin_views.admin_users, name='admin_users'), 
    path('dashboard/readings/', admin_views.admin_readings, name='admin_readings'),
    path('dashboard/settings/', admin_views.admin_settings, name='admin_settings'),
    path('dashboard/statistics/', admin_views.admin_statistics, name='admin_statistics'),
    path('dashboard/toggle-user/<int:user_id>/', admin_views.toggle_user_status, name='toggle_user_status'),
    path('dashboard/delete-reading/<uuid:reading_id>/', admin_views.delete_reading, name='delete_reading'),
]