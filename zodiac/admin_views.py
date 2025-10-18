"""
Admin view for downloading horoscope images
"""
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, FileResponse, Http404
from django.conf import settings
from datetime import date, timedelta
import os
from zodiac.models import ZodiacSign, DailyHoroscope
from django.core.management import call_command
from io import StringIO


@staff_member_required
def horoscope_images_view(request):
    """Burç görselleri indirme sayfası"""
    
    # Tarih seçimi
    selected_date = request.GET.get('date', str(date.today()))
    try:
        target_date = date.fromisoformat(selected_date)
    except:
        target_date = date.today()
    
    # Önceki/sonraki günler
    prev_date = target_date - timedelta(days=1)
    next_date = target_date + timedelta(days=1)
    
    # Burç listesi ve görselleri
    signs = ZodiacSign.objects.all().order_by('id')
    
    images_data = []
    media_dir = os.path.join(settings.MEDIA_ROOT, 'horoscope_images')
    
    for sign in signs:
        # Yorum var mı?
        horoscope = DailyHoroscope.objects.filter(
            zodiac_sign=sign,
            date=target_date
        ).first()
        
        # Görsel var mı?
        image_filename = f"{sign.slug}_{target_date}.jpg"
        image_path = os.path.join(media_dir, image_filename)
        image_exists = os.path.exists(image_path)
        
        image_url = None
        if image_exists:
            image_url = f"{settings.MEDIA_URL}horoscope_images/{image_filename}"
        
        images_data.append({
            'sign': sign,
            'horoscope': horoscope,
            'image_exists': image_exists,
            'image_url': image_url,
            'image_filename': image_filename,
        })
    
    context = {
        'title': 'Burç Görselleri',
        'images_data': images_data,
        'selected_date': target_date,
        'prev_date': prev_date,
        'next_date': next_date,
        'has_opts': True,  # Admin template için
        'site_header': 'Burç Görselleri Yönetimi',
    }
    
    return render(request, 'admin/horoscope_images.html', context)


@staff_member_required
def generate_horoscope_image(request, sign_slug, date_str):
    """Tek bir burç için görsel oluştur"""
    
    try:
        target_date = date.fromisoformat(date_str)
    except:
        return JsonResponse({'error': 'Geçersiz tarih formatı'}, status=400)
    
    try:
        sign = ZodiacSign.objects.get(slug=sign_slug)
    except ZodiacSign.DoesNotExist:
        return JsonResponse({'error': 'Burç bulunamadı'}, status=404)
    
    # Yorum var mı?
    horoscope = DailyHoroscope.objects.filter(
        zodiac_sign=sign,
        date=target_date
    ).first()
    
    if not horoscope:
        return JsonResponse({'error': 'Bu tarih için yorum bulunamadı'}, status=404)
    
    # Görseli oluştur
    try:
        # Management command'ı çağır
        out = StringIO()
        call_command(
            'share_horoscope_instagram',
            zodiac_sign=sign_slug,
            date=date_str,
            test=True,
            stdout=out
        )
        
        # Görsel URL'ini döndür
        image_filename = f"{sign_slug}_{target_date}.jpg"
        image_url = f"{settings.MEDIA_URL}horoscope_images/{image_filename}"
        
        return JsonResponse({
            'success': True,
            'image_url': image_url,
            'message': f'{sign.name} için görsel oluşturuldu'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
def generate_all_horoscope_images(request, date_str):
    """Tüm burçlar için görseller oluştur"""
    
    try:
        target_date = date.fromisoformat(date_str)
    except:
        return JsonResponse({'error': 'Geçersiz tarih formatı'}, status=400)
    
    try:
        # Management command'ı çağır
        out = StringIO()
        call_command(
            'share_horoscope_instagram',
            date=date_str,
            test=True,
            stdout=out
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Tüm burçlar için görseller oluşturuldu',
            'output': out.getvalue()
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
def download_horoscope_image(request, sign_slug, date_str):
    """Görseli indir"""
    
    try:
        target_date = date.fromisoformat(date_str)
    except:
        raise Http404("Geçersiz tarih")
    
    image_filename = f"{sign_slug}_{target_date}.jpg"
    image_path = os.path.join(settings.MEDIA_ROOT, 'horoscope_images', image_filename)
    
    if not os.path.exists(image_path):
        raise Http404("Görsel bulunamadı")
    
    response = FileResponse(open(image_path, 'rb'), content_type='image/jpeg')
    response['Content-Disposition'] = f'attachment; filename="{image_filename}"'
    
    return response
