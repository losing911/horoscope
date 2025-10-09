from django.urls import path
from . import views

app_name = 'zodiac'

urlpatterns = [
    path('', views.zodiac_home, name='home'),
    path('signs/', views.zodiac_signs_list, name='signs_list'),
    path('sign/<slug:sign_slug>/', views.zodiac_sign_detail, name='sign_detail'),
    path('daily/', views.daily_horoscopes, name='daily_horoscopes'),
    path('find-sign/', views.find_my_sign, name='find_sign'),
    path('compatibility/', views.compatibility_check, name='compatibility'),
    path('ai-assistant/', views.ai_zodiac_assistant, name='ai_assistant'),
]
