"""
İleri Seviye Astroloji Özellikleri
- Ay Burcu Hesaplama
- Yükselen Burç Hesaplama  
- Doğum Haritası Oluşturma
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
import logging

from .models import (
    ZodiacSign, MoonSign, Ascendant, BirthChart,
    PersonalHoroscope
)
from tarot.services import AIService
from .astronomy import AstronomyService

logger = logging.getLogger(__name__)


@login_required
def moon_sign_calculator(request):
    """Ay Burcu Hesaplama"""
    moon_sign_result = None
    
    if request.method == 'POST':
        try:
            birth_date = request.POST.get('birth_date')
            birth_time = request.POST.get('birth_time', '12:00')  # Varsayılan öğle
            birth_place = request.POST.get('birth_place', 'İstanbul, Türkiye')
            
            # Datetime objesi oluştur
            date_str = f"{birth_date} {birth_time}"
            date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
            
            # Swiss Ephemeris ile gerçek hesaplama
            astro_service = AstronomyService()
            moon_zodiac = astro_service.calculate_moon_sign(
                birth_date=date_obj,
                birth_place=birth_place
            )
            
            if not moon_zodiac:
                messages.error(request, '❌ Ay burcu hesaplanamadı. Lütfen bilgileri kontrol edin.')
                return redirect('zodiac:moon_sign')
            
            # AI ile yorum oluştur
            ai_service = AIService()
            prompt = f"""Sen profesyonel bir astrolog ve burç yorumcususun.

Bir kişinin Ay Burcu {moon_zodiac.name} olarak hesaplandı.

Ay Burcu kişinin:
- Duygusal yapısını
- İç dünyasını
- Sezgilerini  
- Aile ilişkilerini
- Güvenlik ihtiyaçlarını
temsil eder.

{moon_zodiac.name} Ay Burcu için detaylı bir yorum yap:
- Bu kişinin duygusal özellikleri nelerdir?
- İç dünyası nasıldır?
- İlişkilerde ne arar?
- Kendini nasıl güvende hisseder?

4-5 paragraf halinde, empatik ve içgörü dolu şekilde yaz."""

            interpretation = ai_service.generate_interpretation(
                question=prompt,
                cards=[],
                spread_name="Ay Burcu Yorumu"
            )
            
            # Kaydet
            moon_sign_result = MoonSign.objects.create(
                user=request.user,
                birth_date=date_obj.date(),
                birth_time=datetime.strptime(birth_time, '%H:%M').time() if birth_time else None,
                birth_place=birth_place,
                latitude=41.0082,  # Örnek: İstanbul
                longitude=28.9784,
                moon_sign=moon_zodiac,
                interpretation=interpretation
            )
            
            messages.success(request, f'🌙 Ay burcunuz hesaplandı: {moon_zodiac.name}!')
            
        except Exception as e:
            messages.error(request, f'Hesaplama hatası: {str(e)}')
            logger.error(f"Ay burcu hesaplama hatası: {e}")
    
    # Geçmiş hesaplamalar
    past_calculations = MoonSign.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]
    
    context = {
        'title': 'Ay Burcu Hesaplama',
        'moon_sign_result': moon_sign_result,
        'past_calculations': past_calculations,
    }
    return render(request, 'zodiac/moon_sign.html', context)


@login_required
def ascendant_calculator(request):
    """Yükselen Burç Hesaplama"""
    ascendant_result = None
    
    if request.method == 'POST':
        try:
            birth_date = request.POST.get('birth_date')
            birth_time = request.POST.get('birth_time')
            birth_place = request.POST.get('birth_place', 'Türkiye')
            
            if not birth_time:
                messages.warning(request, '⚠️ Yükselen burç için doğum saati gereklidir!')
                return redirect('zodiac:ascendant')
            
            # Datetime objesi oluştur
            date_str = f"{birth_date} {birth_time}"
            date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
            
            # Swiss Ephemeris ile gerçek hesaplama
            astro_service = AstronomyService()
            
            # Koordinatları al
            lat, lon = astro_service.get_coordinates(birth_place)
            
            # Yükselen burcu hesapla
            ascendant_zodiac = astro_service.calculate_ascendant(
                birth_date=date_obj,
                latitude=lat,
                longitude=lon
            )
            
            if not ascendant_zodiac:
                messages.error(request, '❌ Yükselen burç hesaplanamadı. Lütfen bilgileri kontrol edin.')
                return redirect('zodiac:ascendant')
            
            # AI ile yorum
            ai_service = AIService()
            prompt = f"""Sen profesyonel bir astrolog ve burç yorumcususun.

Bir kişinin Yükselen Burcu {ascendant_zodiac.name} olarak hesaplandı.

Yükselen Burç kişinin:
- Dış görünüşünü ve ilk izlenimini
- Hayata bakış açısını
- Dünyaya kendini nasıl sunduğunu
- Fiziksel özelliklerini
- Yaşam tarzını
temsil eder.

{ascendant_zodiac.name} Yükselen Burç için detaylı bir yorum yap:
- Bu kişi ilk bakışta nasıl görünür?
- Hayata nasıl yaklaşır?
- Dışa karşı nasıl bir maske takar?
- Fiziksel özellikleri neler olabilir?

4-5 paragraf halinde, içgörü dolu şekilde yaz."""

            interpretation = ai_service.generate_interpretation(
                question=prompt,
                cards=[],
                spread_name="Yükselen Burç Yorumu"
            )
            
            # Kaydet
            ascendant_result = Ascendant.objects.create(
                user=request.user,
                birth_date=date_obj.date(),
                birth_time=date_obj.time(),
                birth_place=birth_place,
                latitude=lat,
                longitude=lon,
                ascendant_sign=ascendant_zodiac,
                interpretation=interpretation
            )
            
            messages.success(request, f'⬆️ Yükselen burcunuz hesaplandı: {ascendant_zodiac.name}!')
            
        except Exception as e:
            messages.error(request, f'Hesaplama hatası: {str(e)}')
            logger.error(f"Yükselen burç hatası: {e}")
    
    # Geçmiş hesaplamalar
    past_calculations = Ascendant.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]
    
    context = {
        'title': 'Yükselen Burç Hesaplama',
        'ascendant_result': ascendant_result,
        'past_calculations': past_calculations,
    }
    return render(request, 'zodiac/ascendant.html', context)


@login_required
def birth_chart(request):
    """Doğum Haritası Oluşturma"""
    chart = None
    
    if request.method == 'POST':
        try:
            name = request.POST.get('name', request.user.username)
            birth_date = request.POST.get('birth_date')
            birth_time = request.POST.get('birth_time')
            birth_place = request.POST.get('birth_place', 'Türkiye')
            
            if not birth_time:
                messages.warning(request, '⚠️ Doğum haritası için doğum saati gereklidir!')
                return redirect('zodiac:birth_chart')
            
            # Datetime objesi oluştur
            date_str = f"{birth_date} {birth_time}"
            date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
            
            # Swiss Ephemeris ile gerçek hesaplama
            astro_service = AstronomyService()
            
            # Koordinatları al
            lat, lon = astro_service.get_coordinates(birth_place)
            
            # Güneş Burcu (doğum tarihinden)
            sun_sign = ZodiacSign.get_sign_by_date(date_obj.month, date_obj.day)
            
            if not sun_sign:
                messages.error(request, 'Güneş burcu hesaplanamadı. Lütfen geçerli bir tarih girin.')
                return redirect('zodiac:birth_chart')
            
            # Ay Burcu (Swiss Ephemeris)
            moon_sign = astro_service.calculate_moon_sign(
                birth_date=date_obj,
                birth_place=birth_place
            )
            
            # Yükselen Burç (Swiss Ephemeris)
            ascendant_sign = astro_service.calculate_ascendant(
                birth_date=date_obj,
                latitude=lat,
                longitude=lon
            )
            
            if not moon_sign or not ascendant_sign:
                messages.error(request, '❌ Burç hesaplamaları yapılamadı. Lütfen bilgileri kontrol edin.')
                return redirect('zodiac:birth_chart')
            
            # Tüm gezegenleri hesapla
            planets = astro_service.calculate_all_planets(date_obj, lat, lon)
            planets_info = astro_service.get_planet_info_for_ai(planets)
            
            # AI ile kapsamlı analiz
            ai_service = AIService()
            
            # Kişilik Analizi
            personality_prompt = f"""Sen profesyonel bir astrologsun.

Kişi Bilgileri:
- Güneş Burcu: {sun_sign.name}
- Ay Burcu: {moon_sign.name}
- Yükselen Burç: {ascendant_sign.name}

{planets_info}

Bu doğum haritasına göre kişinin genel karakterini ve kişiliğini detaylı analiz et.
Güneş, Ay ve Yükselen burcun yanı sıra diğer gezegenlerin etkilerini de dikkate al.
3-4 paragraf yaz."""

            personality = ai_service.generate_interpretation(
                question=personality_prompt,
                cards=[],
                spread_name="Kişilik Analizi"
            )
            
            # Duygusal Analiz
            emotional_prompt = f"""Ay Burcu {moon_sign.name} olan bu kişinin duygusal yapısını analiz et.
2-3 paragraf yaz."""

            emotional = ai_service.generate_interpretation(
                question=emotional_prompt,
                cards=[],
                spread_name="Duygusal Analiz"
            )
            
            # Kariyer Analizi
            career_prompt = f"""Güneş Burcu {sun_sign.name} ve Yükselen {ascendant_sign.name} olan bu kişinin kariyer yönelimlerini analiz et.
2-3 paragraf yaz."""

            career = ai_service.generate_interpretation(
                question=career_prompt,
                cards=[],
                spread_name="Kariyer Analizi"
            )
            
            # İlişki Analizi
            relationship_prompt = f"""Bu kişinin ilişki stilini ve aşk hayatını analiz et.
Güneş: {sun_sign.name}, Ay: {moon_sign.name}
2-3 paragraf yaz."""

            relationship = ai_service.generate_interpretation(
                question=relationship_prompt,
                cards=[],
                spread_name="İlişki Analizi"
            )
            
            # Yaşam Yolu
            life_path_prompt = f"""Bu doğum haritasına göre kişinin yaşam yolu ve misyonunu analiz et.
2-3 paragraf yaz."""

            life_path = ai_service.generate_interpretation(
                question=life_path_prompt,
                cards=[],
                spread_name="Yaşam Yolu"
            )
            
            # Doğum haritasını kaydet
            chart = BirthChart.objects.create(
                user=request.user,
                name=name,
                birth_date=date_obj.date(),
                birth_time=date_obj.time(),
                birth_place=birth_place,
                latitude=lat,
                longitude=lon,
                sun_sign=sun_sign,
                moon_sign=moon_sign,
                rising_sign=ascendant_sign,
                personality_analysis=personality,
                emotional_analysis=emotional,
                career_analysis=career,
                relationship_analysis=relationship,
                life_path_analysis=life_path,
                planet_positions={},
                house_positions={},
                aspects={},
                ai_provider='openai'
            )
            
            messages.success(request, f'✨ Doğum haritanız oluşturuldu!')
            
        except Exception as e:
            messages.error(request, f'Oluşturma hatası: {str(e)}')
            logger.error(f"Doğum haritası hatası: {e}")
    
    # Geçmiş haritalar
    past_charts = BirthChart.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]
    
    context = {
        'title': 'Doğum Haritası',
        'chart': chart,
        'past_charts': past_charts,
    }
    return render(request, 'zodiac/birth_chart.html', context)
