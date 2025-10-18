"""
Kullanıcıya Özel Burç Yorumları Views
Her kullanıcı günde 1, haftada 1, ayda 1 yorum hakkına sahiptir
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
import logging

from .models import (
    ZodiacSign, UserDailyHoroscope, UserWeeklyHoroscope, 
    UserMonthlyHoroscope, PersonalHoroscope
)
from .services import ZodiacAIService

logger = logging.getLogger(__name__)


@login_required
def my_daily_horoscope(request):
    """Kullanıcının günlük burç yorumu"""
    # Kullanıcının burcu kontrolü
    user_sign = request.user.zodiac_sign
    
    # Burç yoksa, burç seçim sayfasına yönlendir
    if not user_sign:
        messages.warning(request, '⚠️ Lütfen önce burcunuzu seçin.')
        return redirect('zodiac:select_my_sign')
    
    today = timezone.now().date()
    
    # Bugünün yorumu var mı kontrol et
    daily_horoscope = UserDailyHoroscope.objects.filter(
        user=request.user,
        date=today
    ).first()
    
    # Yoksa ve kullanıcı istiyorsa oluştur
    can_generate = daily_horoscope is None
    
    if request.method == 'POST' and can_generate:
        try:
            ai_service = ZodiacAIService()
            horoscope_data = ai_service.generate_daily_horoscope(user_sign, today)
            
            # get_or_create kullan - race condition'ı önle
            daily_horoscope, created = UserDailyHoroscope.objects.get_or_create(
                user=request.user,
                date=today,
                defaults={
                    'zodiac_sign': user_sign,
                    **horoscope_data
                }
            )
            
            if created:
                messages.success(request, f'🌟 {user_sign.name} burcunuz için günlük yorum oluşturuldu!')
                logger.info(f"Günlük yorum oluşturuldu: {request.user.username} - {user_sign.name}")
            else:
                messages.info(request, f'Bu tarih için zaten bir yorum var.')
            
        except Exception as e:
            messages.error(request, f'Yorum oluşturulurken hata: {str(e)}')
            logger.error(f"Günlük yorum hatası: {request.user.username} - {e}")
    
    context = {
        'title': 'Günlük Burç Yorumum',
        'user_sign': user_sign,
        'daily_horoscope': daily_horoscope,
        'can_generate': can_generate,
        'date': today,
    }
    return render(request, 'zodiac/my_daily_horoscope.html', context)


@login_required
def my_weekly_horoscope(request):
    """Kullanıcının haftalık burç yorumu"""
    # Kullanıcının burcu kontrolü
    user_sign = request.user.zodiac_sign
    
    if not user_sign:
        messages.warning(request, '⚠️ Lütfen önce burcunuzu seçin.')
        return redirect('zodiac:select_my_sign')
    
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())  # Pazartesi
    week_end = week_start + timedelta(days=6)
    
    # Bu haftanın yorumu var mı kontrol et
    weekly_horoscope = UserWeeklyHoroscope.objects.filter(
        user=request.user,
        week_start=week_start
    ).first()
    
    can_generate = weekly_horoscope is None
    
    if request.method == 'POST' and can_generate:
        try:
            ai_service = ZodiacAIService()
            horoscope_data = ai_service.generate_weekly_horoscope(user_sign, week_start)
            
            # get_or_create kullan - race condition'ı önle
            weekly_horoscope, created = UserWeeklyHoroscope.objects.get_or_create(
                user=request.user,
                week_start=week_start,
                defaults={
                    'zodiac_sign': user_sign,
                    'week_end': week_end,
                    **horoscope_data
                }
            )
            
            if created:
                messages.success(request, f'🌟 {user_sign.name} burcunuz için haftalık yorum oluşturuldu!')
                logger.info(f"Haftalık yorum oluşturuldu: {request.user.username} - {user_sign.name}")
            else:
                messages.info(request, f'Bu hafta için zaten bir yorum var.')
            
        except Exception as e:
            messages.error(request, f'Yorum oluşturulurken hata: {str(e)}')
            logger.error(f"Haftalık yorum hatası: {request.user.username} - {e}")
    
    context = {
        'title': 'Haftalık Burç Yorumum',
        'user_sign': user_sign,
        'weekly_horoscope': weekly_horoscope,
        'can_generate': can_generate,
        'week_start': week_start,
        'week_end': week_end,
    }
    return render(request, 'zodiac/my_weekly_horoscope.html', context)


@login_required
def my_monthly_horoscope(request):
    """Kullanıcının aylık burç yorumu"""
    # Kullanıcının burcu kontrolü
    user_sign = request.user.zodiac_sign
    
    if not user_sign:
        messages.warning(request, '⚠️ Lütfen önce burcunuzu seçin.')
        return redirect('zodiac:select_my_sign')
    
    today = timezone.now().date()
    year = today.year
    month = today.month
    
    # Bu ayın yorumu var mı kontrol et
    monthly_horoscope = UserMonthlyHoroscope.objects.filter(
        user=request.user,
        year=year,
        month=month
    ).first()
    
    can_generate = monthly_horoscope is None
    
    if request.method == 'POST' and can_generate:
        try:
            ai_service = ZodiacAIService()
            horoscope_data = ai_service.generate_monthly_horoscope(user_sign, year, month)
            
            # get_or_create kullan - race condition'ı önle
            monthly_horoscope, created = UserMonthlyHoroscope.objects.get_or_create(
                user=request.user,
                year=year,
                month=month,
                defaults={
                    'zodiac_sign': user_sign,
                    **horoscope_data
                }
            )
            
            if created:
                messages.success(request, f'🌟 {user_sign.name} burcunuz için aylık yorum oluşturuldu!')
                logger.info(f"Aylık yorum oluşturuldu: {request.user.username} - {user_sign.name}")
            else:
                messages.info(request, f'Bu ay için zaten bir yorum var.')
            
        except Exception as e:
            messages.error(request, f'Yorum oluşturulurken hata: {str(e)}')
            logger.error(f"Aylık yorum hatası: {request.user.username} - {e}")
    
    month_names = ['', 'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran',
                   'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
    
    context = {
        'title': f'{month_names[month]} Aylık Burç Yorumum',
        'user_sign': user_sign,
        'monthly_horoscope': monthly_horoscope,
        'can_generate': can_generate,
        'year': year,
        'month': month,
        'month_name': month_names[month],
    }
    return render(request, 'zodiac/my_monthly_horoscope.html', context)


@login_required
def select_my_sign(request):
    """Kullanıcının burcunu seçme/belirleme"""
    zodiac_signs = ZodiacSign.objects.all().order_by('order')
    selected_sign = request.user.zodiac_sign  # User modelinden direkt al
    
    if request.method == 'POST':
        sign_id = request.POST.get('sign_id')
        birth_month = request.POST.get('birth_month')
        birth_day = request.POST.get('birth_day')
        
        try:
            if sign_id:
                # Direkt burç seçimi
                selected_sign = get_object_or_404(ZodiacSign, id=sign_id)
                request.user.zodiac_sign = selected_sign
                request.user.save()
                messages.success(request, f'✅ {selected_sign.name} burcu seçildi!')
            elif birth_month and birth_day:
                # Doğum tarihinden burç belirleme
                month = int(birth_month)
                day = int(birth_day)
                selected_sign = ZodiacSign.get_sign_by_date(month, day)
                
                if selected_sign:
                    # Doğum tarihini ve burcu kaydet
                    from datetime import date
                    request.user.birth_date = date(2000, month, day)  # Yıl önemli değil
                    request.user.zodiac_sign = selected_sign
                    request.user.save()
                    messages.success(request, f'✅ Burcunuz: {selected_sign.name}')
                else:
                    messages.error(request, '❌ Geçersiz tarih!')
            
            return redirect('zodiac:my_daily_horoscope')
            
        except Exception as e:
            messages.error(request, f'❌ Hata: {str(e)}')
            logger.error(f"Burç seçme hatası: {e}")
    
    context = {
        'title': 'Burcumu Seç',
        'zodiac_signs': zodiac_signs,
        'selected_sign': selected_sign,
    }
    return render(request, 'zodiac/select_my_sign.html', context)


@login_required
def my_horoscope_history(request):
    """Kullanıcının burç yorumu geçmişi"""
    daily_horoscopes = UserDailyHoroscope.objects.filter(
        user=request.user
    ).order_by('-date')[:30]
    
    weekly_horoscopes = UserWeeklyHoroscope.objects.filter(
        user=request.user
    ).order_by('-week_start')[:10]
    
    monthly_horoscopes = UserMonthlyHoroscope.objects.filter(
        user=request.user
    ).order_by('-year', '-month')[:12]
    
    context = {
        'title': 'Burç Yorumlarım',
        'daily_horoscopes': daily_horoscopes,
        'weekly_horoscopes': weekly_horoscopes,
        'monthly_horoscopes': monthly_horoscopes,
    }
    return render(request, 'zodiac/my_horoscope_history.html', context)
