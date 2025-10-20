from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.core.paginator import Paginator

from .models import TarotReading, TarotCard, TarotSpread, DailyCard, SiteSettings
from accounts.models import User


def is_staff(user):
    """Staff kontrolü"""
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_staff)
def admin_dashboard(request):
    """Admin dashboard ana sayfa"""
    
    # Temel istatistikler
    total_users = User.objects.count()
    total_readings = TarotReading.objects.count()
    total_cards = TarotCard.objects.count()
    total_spreads = TarotSpread.objects.filter(is_active=True).count()
    
    # Bu ay istatistikleri
    current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    monthly_users = User.objects.filter(date_joined__gte=current_month).count()
    monthly_readings = TarotReading.objects.filter(created_at__gte=current_month).count()
    
    # Bugünkü istatistikler
    today = timezone.now().date()
    daily_readings = TarotReading.objects.filter(created_at__date=today).count()
    daily_users = User.objects.filter(last_login__date=today).count()
    
    # Son okumalar
    recent_readings = TarotReading.objects.select_related('user', 'spread').order_by('-created_at')[:10]
    
    # Popüler yayılımlar
    popular_spreads = TarotReading.objects.values('spread__name', 'spread__slug').annotate(
        reading_count=Count('id')
    ).order_by('-reading_count')[:5]
    
    # En aktif kullanıcılar
    active_users = User.objects.annotate(
        reading_count=Count('tarotreading')
    ).order_by('-reading_count')[:10]
    
    # Haftalık grafik verisi
    week_ago = timezone.now() - timedelta(days=7)
    daily_stats = []
    for i in range(7):
        date = (week_ago + timedelta(days=i)).date()
        readings_count = TarotReading.objects.filter(created_at__date=date).count()
        daily_stats.append({
            'date': date.strftime('%m/%d'),
            'readings': readings_count
        })
    
    import json
    daily_stats_json = json.dumps(daily_stats)
    
    context = {
        'title': 'Admin Dashboard - Tarot Yorum',
        'total_users': total_users,
        'total_readings': total_readings,
        'total_cards': total_cards,
        'total_spreads': total_spreads,
        'monthly_users': monthly_users,
        'monthly_readings': monthly_readings,
        'daily_readings': daily_readings,
        'daily_users': daily_users,
        'recent_readings': recent_readings,
        'popular_spreads': popular_spreads,
        'active_users': active_users,
        'daily_stats': daily_stats_json,
    }
    
    return render(request, 'tarot/admin/dashboard.html', context)


@login_required
@user_passes_test(is_staff)
def admin_users(request):
    """Kullanıcı yönetimi"""
    
    # Filtreleme
    search = request.GET.get('search', '')
    status = request.GET.get('status', 'all')
    
    users = User.objects.all()
    
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    if status == 'active':
        users = users.filter(is_active=True)
    elif status == 'inactive':
        users = users.filter(is_active=False)
    elif status == 'staff':
        users = users.filter(is_staff=True)
    
    # Okuma sayısı ekleme
    users = users.annotate(reading_count=Count('tarotreading')).order_by('-date_joined')
    
    # Sayfalama
    paginator = Paginator(users, 20)
    page = request.GET.get('page')
    users_page = paginator.get_page(page)
    
    context = {
        'title': 'Kullanıcı Yönetimi - Admin',
        'users': users_page,
        'search': search,
        'status': status,
        'total_users': users.count(),
    }
    
    return render(request, 'tarot/admin/users.html', context)


@login_required
@user_passes_test(is_staff)
def admin_readings(request):
    """Okuma yönetimi"""
    
    # Filtreleme
    search = request.GET.get('search', '')
    spread_filter = request.GET.get('spread', 'all')
    date_filter = request.GET.get('date', 'all')
    
    readings = TarotReading.objects.select_related('user', 'spread').all()
    
    if search:
        readings = readings.filter(
            Q(user__username__icontains=search) |
            Q(question__icontains=search) |
            Q(spread__name__icontains=search)
        )
    
    if spread_filter != 'all':
        readings = readings.filter(spread__slug=spread_filter)
    
    if date_filter == 'today':
        readings = readings.filter(created_at__date=timezone.now().date())
    elif date_filter == 'week':
        week_ago = timezone.now() - timedelta(days=7)
        readings = readings.filter(created_at__gte=week_ago)
    elif date_filter == 'month':
        month_ago = timezone.now() - timedelta(days=30)
        readings = readings.filter(created_at__gte=month_ago)
    
    readings = readings.order_by('-created_at')
    
    # Sayfalama
    paginator = Paginator(readings, 20)
    page = request.GET.get('page')
    readings_page = paginator.get_page(page)
    
    # Yayılım listesi
    spreads = TarotSpread.objects.filter(is_active=True)
    
    context = {
        'title': 'Okuma Yönetimi - Admin',
        'readings': readings_page,
        'spreads': spreads,
        'search': search,
        'spread_filter': spread_filter,
        'date_filter': date_filter,
        'total_readings': readings.count(),
    }
    
    return render(request, 'tarot/admin/readings.html', context)


@login_required
@user_passes_test(is_staff)
def admin_settings(request):
    """Site ayarları"""
    
    settings = SiteSettings.load()
    
    if request.method == 'POST':
        # Site ayarlarını güncelle
        settings.site_title = request.POST.get('site_title', settings.site_title)
        settings.site_description = request.POST.get('site_description', settings.site_description)
        settings.daily_reading_limit = int(request.POST.get('daily_reading_limit', settings.daily_reading_limit))
        settings.max_question_length = int(request.POST.get('max_question_length', settings.max_question_length))
        
        # Site durumu
        settings.maintenance_mode = request.POST.get('maintenance_mode') == 'on'
        settings.allow_registration = request.POST.get('allow_registration') == 'on'
        settings.allow_guest_reading = request.POST.get('allow_guest_reading') == 'on'
        
        settings.save()
        messages.success(request, 'Site ayarları başarıyla güncellendi!')
        return redirect('tarot:admin_settings')
    
    context = {
        'title': 'Site Ayarları - Admin',
        'settings': settings,
    }
    
    return render(request, 'tarot/admin/settings.html', context)


@login_required
@user_passes_test(is_staff)
def admin_statistics(request):
    """İstatistikler sayfası"""
    
    # Zaman filtreleri
    period = request.GET.get('period', '30')  # 7, 30, 90 gün
    days = int(period)
    
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Günlük istatistikler
    daily_stats = []
    for i in range(days):
        date = (start_date + timedelta(days=i)).date()
        readings_count = TarotReading.objects.filter(created_at__date=date).count()
        users_count = User.objects.filter(date_joined__date=date).count()
        daily_stats.append({
            'date': date.strftime('%Y-%m-%d'),
            'readings': readings_count,
            'users': users_count
        })
    
    import json
    daily_stats_json = json.dumps(daily_stats)
    
    # En popüler yayılımlar
    popular_spreads = TarotReading.objects.filter(
        created_at__gte=start_date
    ).values('spread__name').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Kullanıcı aktivitesi
    user_activity = User.objects.filter(
        date_joined__gte=start_date
    ).annotate(
        reading_count=Count('tarotreading')
    ).order_by('-reading_count')[:10]
    
    context = {
        'title': 'İstatistikler - Admin',
        'daily_stats': daily_stats_json,
        'popular_spreads': popular_spreads,
        'user_activity': user_activity,
        'period': period,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
    }
    
    return render(request, 'tarot/admin/statistics.html', context)


@login_required
@user_passes_test(is_staff)
def toggle_user_status(request, user_id):
    """Kullanıcı durumunu değiştir (AJAX)"""
    
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            user.is_active = not user.is_active
            user.save()
            
            return JsonResponse({
                'success': True,
                'status': user.is_active,
                'message': f'Kullanıcı {"aktif" if user.is_active else "pasif"} yapıldı.'
            })
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Kullanıcı bulunamadı.'
            })
    
    return JsonResponse({'success': False, 'message': 'Geçersiz istek.'})


@login_required
@user_passes_test(is_staff)
def delete_reading(request, reading_id):
    """Okuma silme (AJAX)"""
    
    if request.method == 'POST':
        try:
            reading = TarotReading.objects.get(id=reading_id)
            reading.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Okuma başarıyla silindi.'
            })
        except TarotReading.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Okuma bulunamadı.'
            })
    
    return JsonResponse({'success': False, 'message': 'Geçersiz istek.'})