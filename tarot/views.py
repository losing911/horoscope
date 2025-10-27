from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.urls import reverse
import random
import json
from .models import TarotCard, TarotSpread, TarotReading, DailyCard, SiteSettings, HeroSection
from .services import AIService, DailyCardService


def index(request):
    """Ana sayfa"""
    # Hero section içeriğini al
    hero_section = HeroSection.get_active()
    
    # Son okumaları al (herkese açık olanlar)
    recent_readings = TarotReading.objects.filter(is_public=True).order_by('-created_at')[:6]
    
    # Popüler yayılımları al
    popular_spreads = TarotSpread.objects.filter(is_active=True).order_by('difficulty_level')[:4]
    
    # YouTube videolarını al
    youtube_videos = []
    try:
        from blog.youtube_service import YouTubeService
        youtube_service = YouTubeService()
        youtube_videos = youtube_service.get_latest_videos(max_results=6)
    except Exception as e:
        print(f"YouTube videoları alınamadı: {e}")
    
    # Günlük burç yorumlarını al ve gerekirse Gemini ile oluştur
    daily_horoscopes = []
    try:
        from zodiac.models import ZodiacSign, DailyHoroscope
        from zodiac.views import generate_daily_horoscope
        
        # İlk 6 burcu al
        zodiac_signs = ZodiacSign.objects.all().order_by('order')[:6]
        today = timezone.now().date()
        
        for sign in zodiac_signs:
            # Bugünün yorumu var mı kontrol et
            horoscope = DailyHoroscope.objects.filter(
                zodiac_sign=sign,
                date=today
            ).first()
            
            # Yoksa Gemini ile otomatik oluştur
            if not horoscope:
                try:
                    horoscope = generate_daily_horoscope(sign, today)
                except Exception as e:
                    print(f"Günlük yorum oluşturma hatası ({sign.name}): {e}")
                    # Hata durumunda boş geç
                    continue
            
            if horoscope:
                daily_horoscopes.append({
                    'sign': sign,
                    'horoscope': horoscope
                })
    except ImportError:
        pass  # Zodiac app henüz yüklü değil
    except Exception as e:
        print(f"Günlük burç yorumları yükleme hatası: {e}")
    
    context = {
        'title': 'İçsel Yolculuk - AI Destekli Kişisel Gelişim ve Farkındalık',
        'description': 'Yapay zeka destekli kişisel gelişim ve duygusal farkındalık rehberliği',
        'hero_section': hero_section,
        'recent_readings': recent_readings,
        'popular_spreads': popular_spreads,
        'daily_horoscopes': daily_horoscopes,
        'youtube_videos': youtube_videos,
    }
    return render(request, 'tarot/index.html', context)


def spreads_list(request):
    """Rehberlik yöntemleri listesi"""
    spreads = TarotSpread.objects.filter(is_active=True).order_by('difficulty_level', 'card_count')
    
    context = {
        'title': 'Rehberlik Yöntemleri',
        'spreads': spreads,
    }
    return render(request, 'tarot/spreads_list.html', context)


def spread_detail(request, slug):
    """Yayılım detayı ve rehberlik seansı başlatma"""
    spread = get_object_or_404(TarotSpread, slug=slug, is_active=True)
    
    context = {
        'title': f'{spread.name} - Rehberlik Yöntemi',
        'spread': spread,
    }
    return render(request, 'tarot/spread_detail.html', context)


@login_required
@require_POST
def create_reading(request):
    """Yeni kişisel rehberlik seansı oluştur"""
    try:
        # Site ayarlarını kontrol et
        settings = SiteSettings.load()
        
        # TEST AŞAMASI: Günlük okuma sınırı devre dışı
        # if not request.user.can_read_today():
        #     return JsonResponse({
        #         'success': False,
        #         'error': f'Günlük okuma limitiniz ({settings.daily_reading_limit}) dolmuş.'
        #     })
        
        # Form verilerini al
        spread_id = request.POST.get('spread_id')
        question = request.POST.get('question', '').strip()
        
        if not question:
            return JsonResponse({
                'success': False,
                'error': 'Lütfen bir soru girin.'
            })
        
        if len(question) > settings.max_question_length:
            return JsonResponse({
                'success': False,
                'error': f'Soru en fazla {settings.max_question_length} karakter olabilir.'
            })
        
        # Yayılımı al
        spread = get_object_or_404(TarotSpread, id=spread_id, is_active=True)
        
        # Her zaman rastgele kartları çek
        all_cards = list(TarotCard.objects.all())
        if len(all_cards) < spread.card_count:
            return JsonResponse({
                'success': False,
                'error': 'Yeterli kart yok.'
            })
        selected_cards = random.sample(all_cards, spread.card_count)
        
        # Kartların bilgilerini hazırla
        cards_data = []
        for i, card in enumerate(selected_cards, 1):
            is_reversed = random.choice([True, False])
            position_meaning = spread.positions.get(str(i), f'Pozisyon {i}')
            
            cards_data.append({
                'id': card.id,
                'name': card.name,
                'position': i,
                'position_meaning': position_meaning,
                'is_reversed': is_reversed,
                'meaning': card.reversed_meaning if is_reversed else card.upright_meaning,
                'image_url': card.image_url if card.image_url else None
            })
        
        # AI yorumu oluştur
        try:
            # Kullanıcının seçili dilini al
            from django.utils.translation import get_language
            current_language = get_language()
            
            ai_service = AIService()
            # Kartları AI servisi için hazırla
            ai_cards = []
            for card_data in cards_data:
                card_obj = TarotCard.objects.get(id=card_data['id'])
                ai_cards.append({
                    'card': card_obj,
                    'position': card_data['position'],
                    'is_reversed': card_data['is_reversed']
                })
            
            interpretation = ai_service.generate_interpretation(
                question=question,
                cards=ai_cards,
                spread_name=spread.name,
                language=current_language
            )
        except Exception as e:
            print(f"AI Service Error: {e}")
            # Fallback yorum
            interpretation = f"## {spread.name} Yorumu\n\n**Sorunuz:** {question}\n\n"
            for card_data in cards_data:
                interpretation += f"**{card_data['position']}. Pozisyon - {card_data['name']}:** "
                interpretation += f"{card_data['meaning']}\n\n"
        
        # Okuma kaydı oluştur
        reading = TarotReading.objects.create(
            user=request.user,
            spread=spread,
            question=question,
            cards=cards_data,
            interpretation=interpretation,
            ai_provider=request.user.preferred_ai_provider,
            is_public=False
        )
        
        return JsonResponse({
            'success': True,
            'reading_id': str(reading.id),
            'redirect_url': reverse('tarot:reading_detail', kwargs={'reading_id': reading.id})
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Bir hata oluştu: {str(e)}'
        })


def reading_detail(request, reading_id):
    """Okuma detayını göster"""
    reading = get_object_or_404(TarotReading, id=reading_id)
    
    # Okuma sahibi veya herkese açık okuma kontrolü
    if reading.user != request.user and not reading.is_public:
        messages.error(request, 'Bu okumayı görme yetkiniz yok.')
        return redirect('tarot:index')
    
    context = {
        'title': f'{reading.spread.name} Okuma',
        'reading': reading,
    }
    return render(request, 'tarot/reading_detail.html', context)


@login_required
def toggle_reading_public(request, reading_id):
    """Okumayı herkese açık/gizli yap"""
    reading = get_object_or_404(TarotReading, id=reading_id)
    
    # Sadece okuma sahibi değiştirebilir
    if reading.user != request.user:
        messages.error(request, 'Bu işlemi yapma yetkiniz yok.')
        return redirect('tarot:reading_detail', reading_id=reading.id)
    
    # Durumu tersine çevir
    reading.is_public = not reading.is_public
    reading.save()
    
    if reading.is_public:
        messages.success(request, 'Okuma herkese açık hale getirildi.')
    else:
        messages.success(request, 'Okuma gizli hale getirildi.')
    
    return redirect('tarot:reading_detail', reading_id=reading.id)


@login_required
def user_readings(request):
    """Kullanıcının okumalarını listele"""
    readings = TarotReading.objects.filter(user=request.user).order_by('-created_at')
    
    paginator = Paginator(readings, 12)
    page = request.GET.get('page')
    readings_page = paginator.get_page(page)
    
    context = {
        'title': 'Okumalarım',
        'readings': readings_page,
    }
    return render(request, 'tarot/user_readings.html', context)


@login_required
def daily_card(request):
    """Günlük ilham kaynağı"""
    today = timezone.now().date()
    
    # Bugün çekilmiş sembol var mı kontrol et
    daily_card_obj = DailyCard.objects.filter(user=request.user, date=today).first()
    
    if not daily_card_obj:
        # Yeni günlük ilham kaynağı seç
        all_cards = list(TarotCard.objects.all())
        if all_cards:
            random_card = random.choice(all_cards)
            is_reversed = random.choice([True, False])
            
            # AI yorumu oluştur
            try:
                # Kullanıcının seçili dilini al
                from django.utils.translation import get_language
                current_language = get_language()
                
                daily_service = DailyCardService()
                interpretation = daily_service.generate_daily_interpretation(
                    random_card, 
                    is_reversed,
                    language=current_language
                )
            except Exception as e:
                print(f"Daily card interpretation error: {e}")
                meaning = random_card.reversed_meaning if is_reversed else random_card.upright_meaning
                interpretation = f"## Günün İlham Kaynağı: {random_card.name}\n\nBugün sizin için {random_card.name} rehberlik sembolü seçildi.\n\n{meaning}"
            
            daily_card_obj = DailyCard.objects.create(
                user=request.user,
                card=random_card,
                date=today,
                is_reversed=is_reversed,
                interpretation=interpretation
            )
    
    context = {
        'title': 'Günlük İlham Kaynağı',
        'daily_card': daily_card_obj,
    }
    return render(request, 'tarot/daily_card.html', context)


def public_readings(request):
    """Paylaşılan rehberlik deneyimleri"""
    readings = TarotReading.objects.filter(is_public=True).order_by('-created_at')
    
    # Yayılımlara göre grupla
    readings_by_spread = {}
    for reading in readings:
        spread_name = reading.spread.name if reading.spread else "Diğer"
        if spread_name not in readings_by_spread:
            readings_by_spread[spread_name] = []
        readings_by_spread[spread_name].append(reading)
    
    paginator = Paginator(readings, 12)
    page = request.GET.get('page')
    readings_page = paginator.get_page(page)
    
    context = {
        'title': 'Paylaşılan Rehberlik Deneyimleri',
        'readings': readings_page,
        'readings_by_spread': readings_by_spread,
    }
    return render(request, 'tarot/public_readings.html', context)
