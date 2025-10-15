from django.urls import path
from . import views
from . import views_personal
from . import views_advanced

app_name = 'zodiac'

urlpatterns = [
    path('', views.zodiac_home, name='home'),
    path('signs/', views.zodiac_signs_list, name='signs_list'),
    path('sign/<slug:sign_slug>/', views.zodiac_sign_detail, name='sign_detail'),
    
    # Genel burç yorumları (eski - kullanım dışı)
    path('daily/', views.daily_horoscopes, name='daily_horoscopes'),
    path('weekly/', views.weekly_horoscopes, name='weekly_horoscopes'),
    path('monthly/', views.monthly_horoscopes, name='monthly_horoscopes'),
    
    # Kişisel burç yorumları (kullanıcıya özel)
    path('my/daily/', views_personal.my_daily_horoscope, name='my_daily_horoscope'),
    path('my/weekly/', views_personal.my_weekly_horoscope, name='my_weekly_horoscope'),
    path('my/monthly/', views_personal.my_monthly_horoscope, name='my_monthly_horoscope'),
    path('my/select-sign/', views_personal.select_my_sign, name='select_my_sign'),
    path('my/history/', views_personal.my_horoscope_history, name='my_horoscope_history'),
    
    # İleri seviye özellikler
    path('moon-sign/', views_advanced.moon_sign_calculator, name='moon_sign'),
    path('ascendant/', views_advanced.ascendant_calculator, name='ascendant'),
    path('birth-chart/', views_advanced.birth_chart, name='birth_chart'),
    
    path('find-sign/', views.find_my_sign, name='find_sign'),
    path('compatibility/', views.compatibility_check, name='compatibility'),
    path('ai-assistant/', views.ai_zodiac_assistant, name='ai_assistant'),
    
    # Teknoloji ve bilimsel açıklamalar
    path('technology/', views.technology, name='technology'),
]
