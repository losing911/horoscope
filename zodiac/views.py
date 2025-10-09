from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from datetime import datetime, timedelta
import random

from .models import (
    ZodiacSign, DailyHoroscope, WeeklyHoroscope,
    MonthlyHoroscope, CompatibilityReading, BirthChart
)
from tarot.services import AIService, ImageGenerationService


def zodiac_home(request):
    """Astroloji ana sayfası"""
    zodiac_signs = ZodiacSign.objects.all().order_by('order')
    
    # Kullanıcının burcu varsa bul
    user_sign = None
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        if hasattr(request.user.profile, 'birth_date') and request.user.profile.birth_date:
            user_sign = ZodiacSign.get_sign_by_date(
                request.user.profile.birth_date.month,
                request.user.profile.birth_date.day
            )
    
    context = {
        'title': 'Astroloji & Burç Yorumları',
        'zodiac_signs': zodiac_signs,
        'user_sign': user_sign,
    }
    return render(request, 'zodiac/index.html', context)


def zodiac_signs_list(request):
    """Tüm burçlar"""
    zodiac_signs = ZodiacSign.objects.all().order_by('order')
    
    context = {
        'title': 'Burçlar',
        'zodiac_signs': zodiac_signs,
    }
    return render(request, 'zodiac/signs_list.html', context)


def zodiac_sign_detail(request, sign_slug):
    """Burç detayı"""
    zodiac_sign = get_object_or_404(ZodiacSign, slug=sign_slug)
    
    # Bugünün burç yorumu
    today = timezone.now().date()
    daily_horoscope = DailyHoroscope.objects.filter(
        zodiac_sign=zodiac_sign,
        date=today
    ).first()
    
    # Yoksa oluştur
    if not daily_horoscope:
        daily_horoscope = generate_daily_horoscope(zodiac_sign, today)
    
    # AI ile burç görseli oluştur (isteğe bağlı)
    zodiac_image = None
    if request.GET.get('generate_image'):
        try:
            image_service = ImageGenerationService()
            # Element çevirisi
            element_map = {'fire': 'Ateş', 'earth': 'Toprak', 'air': 'Hava', 'water': 'Su'}
            element_display = element_map.get(zodiac_sign.element, zodiac_sign.element)
            
            zodiac_image = image_service.generate_zodiac_symbol_image(
                zodiac_name=zodiac_sign.name,
                element=element_display,
                traits=zodiac_sign.strengths[:200]
            )
        except Exception as e:
            print(f"Image generation error: {e}")
    
    context = {
        'title': f'{zodiac_sign.name} Burcu',
        'zodiac_sign': zodiac_sign,
        'daily_horoscope': daily_horoscope,
        'zodiac_image': zodiac_image,
    }
    return render(request, 'zodiac/sign_detail.html', context)


def daily_horoscopes(request):
    """Tüm burçların günlük yorumları"""
    today = timezone.now().date()
    zodiac_signs = ZodiacSign.objects.all().order_by('order')
    
    horoscopes = []
    for sign in zodiac_signs:
        horoscope = DailyHoroscope.objects.filter(
            zodiac_sign=sign,
            date=today
        ).first()
        
        # Yoksa oluştur
        if not horoscope:
            horoscope = generate_daily_horoscope(sign, today)
        
        horoscopes.append({
            'sign': sign,
            'horoscope': horoscope
        })
    
    context = {
        'title': 'Günlük Burç Yorumları',
        'date': today,
        'horoscopes': horoscopes,
    }
    return render(request, 'zodiac/daily_horoscopes.html', context)


def find_my_sign(request):
    """Burç bulma sayfası"""
    found_sign = None
    error = None
    
    if request.method == 'POST':
        try:
            month = int(request.POST.get('birth_month'))
            day = int(request.POST.get('birth_day'))
            
            found_sign = ZodiacSign.get_sign_by_date(month, day)
        except (ValueError, TypeError) as e:
            error = "Lütfen geçerli bir tarih girin."
    
    context = {
        'title': 'Burcumu Öğren',
        'found_sign': found_sign,
        'error': error,
    }
    return render(request, 'zodiac/find_sign.html', context)


@login_required
def ai_zodiac_assistant(request):
    """AI Burç Asistanı - Kullanıcı soruları"""
    zodiac_signs = ZodiacSign.objects.all().order_by('order')
    response_text = None
    error = None
    
    if request.method == 'POST':
        question = request.POST.get('question', '').strip()
        user_sign_id = request.POST.get('user_sign')
        
        if question:
            try:
                user_sign = None
                if user_sign_id:
                    user_sign = get_object_or_404(ZodiacSign, id=user_sign_id)
                
                ai_service = AIService()
                
                # Prompt oluştur
                if user_sign:
                    prompt = f"""Sen profesyonel bir astrolog ve burç danışmanısın.

Kullanıcının Burcu: {user_sign.name}
Burç Özellikleri:
- Element: {user_sign.element}
- Yöneten Gezegen: {user_sign.ruling_planet}
- Güçlü Yönler: {user_sign.strengths[:100]}
- Zayıf Yönler: {user_sign.weaknesses[:100]}

Kullanıcının Sorusu: {question}

Lütfen soruya detaylı, anlayışlı ve faydalı bir şekilde cevap ver. Kullanıcının burç özelliklerini göz önünde bulundurarak kişiselleştirilmiş tavsiyeler ver."""
                else:
                    prompt = f"""Sen profesyonel bir astrolog ve burç danışmanısın.

Kullanıcının Sorusu: {question}

Lütfen soruya detaylı, anlayışlı ve faydalı bir şekilde cevap ver. Astroloji bilgin ile kullanıcıya yol göster."""

                response_text = ai_service.generate_interpretation(
                    question=prompt,
                    cards=[],
                    spread_name="Burç Danışmanlığı"
                )
                
            except Exception as e:
                error = f"Bir hata oluştu: {str(e)}"
        else:
            error = "Lütfen bir soru yazın."
    
    context = {
        'title': 'AI Burç Asistanı',
        'zodiac_signs': zodiac_signs,
        'response_text': response_text,
        'error': error,
    }
    return render(request, 'zodiac/ai_assistant.html', context)


@login_required
def compatibility_check(request):
    """Burç uyumu kontrolü"""
    zodiac_signs = ZodiacSign.objects.all().order_by('order')
    compatibility = None
    error = None
    
    if request.method == 'POST':
        sign1_id = request.POST.get('sign1')
        sign2_id = request.POST.get('sign2')
        
        if sign1_id and sign2_id:
            try:
                sign1 = get_object_or_404(ZodiacSign, id=sign1_id)
                sign2 = get_object_or_404(ZodiacSign, id=sign2_id)
                
                # Aynı burç seçilmiş mi?
                if sign1_id == sign2_id:
                    error = "Lütfen farklı iki burç seçin."
                else:
                    # Daha önce yapılmış mı kontrol et (her iki sıra için)
                    compatibility = CompatibilityReading.objects.filter(
                        user=request.user
                    ).filter(
                        Q(sign1=sign1, sign2=sign2) | 
                        Q(sign1=sign2, sign2=sign1)
                    ).first()
                    
                    # Yoksa oluştur
                    if not compatibility:
                        compatibility = generate_compatibility(request.user, sign1, sign2)
                        
                        if not compatibility:
                            error = "Uyum analizi oluşturulurken bir hata oluştu. Lütfen tekrar deneyin."
                            
            except Exception as e:
                error = f"Bir hata oluştu: {str(e)}"
        else:
            error = "Lütfen iki burç seçin."
    
    context = {
        'title': 'Burç Uyumu',
        'zodiac_signs': zodiac_signs,
        'compatibility': compatibility,
        'error': error,
    }
    return render(request, 'zodiac/compatibility.html', context)


# Helper Functions

def generate_daily_horoscope(zodiac_sign, date):
    """AI ile günlük burç yorumu oluştur"""
    try:
        ai_service = AIService()
        
        prompt = f"""Sen profesyonel bir astrolog ve burç yorumcususun. 
        
{zodiac_sign.name} burcu için {date} tarihli günlük burç yorumu yap.

Burç Özellikleri:
- Element: {zodiac_sign.get_element_display()}
- Yöneten Gezegen: {zodiac_sign.ruling_planet}
- Güçlü Yönler: {zodiac_sign.strengths[:100]}

Aşağıdaki başlıklar altında yorumla:

1. GENEL: Günün genel enerjisi ve öneriler (2-3 cümle)
2. AŞK: Aşk hayatı ve ilişkiler (2-3 cümle)
3. KARİYER: İş hayatı ve fırsatlar (2-3 cümle)
4. SAĞLIK: Fiziksel ve mental sağlık (2-3 cümle)
5. FİNANS: Ekonomik durum ve harcamalar (2-3 cümle)

Her başlığı büyük harfle yaz ve altına yorumu ekle. Pozitif, motive edici ve yapıcı ol."""

        response = ai_service.generate_interpretation(
            question=prompt,
            cards=[],
            spread_name="Günlük Burç"
        )
        
        # Yanıtı parse et
        sections = parse_horoscope_response(response)
        
        # Şanslı sayı ve renk
        lucky_numbers = [int(n) for n in zodiac_sign.lucky_numbers.split(',') if n.strip().isdigit()]
        lucky_colors = [c.strip() for c in zodiac_sign.lucky_colors.split(',')]
        
        horoscope = DailyHoroscope.objects.create(
            zodiac_sign=zodiac_sign,
            date=date,
            general=sections.get('GENEL', 'Bugün sizin için güzel bir gün olacak.'),
            love=sections.get('AŞK', 'Aşk hayatınızda huzur var.'),
            career=sections.get('KARİYER', 'İşleriniz yolunda gidiyor.'),
            health=sections.get('SAĞLIK', 'Sağlığınıza dikkat edin.'),
            money=sections.get('FİNANS', 'Finansal durumunuz dengeli.'),
            mood_score=random.randint(6, 10),
            lucky_number=random.choice(lucky_numbers) if lucky_numbers else random.randint(1, 99),
            lucky_color=random.choice(lucky_colors) if lucky_colors else 'Mavi',
            ai_provider='gemini'
        )
        
        return horoscope
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"\n❌ Horoscope generation error for {zodiac_sign.name}: {e}")
        print(f"Error details: {error_details}")
        # Fallback - AI başarısız olursa
        return DailyHoroscope.objects.create(
            zodiac_sign=zodiac_sign,
            date=date,
            general=f"[FALLBACK] Bugün {zodiac_sign.name} burcu için enerjik bir gün olacak.",
            love="[FALLBACK] Aşk hayatınızda olumlu gelişmeler sizi bekliyor.",
            career="[FALLBACK] Kariyerinizde yeni fırsatlar doğabilir.",
            health="[FALLBACK] Sağlığınıza özen gösterin.",
            money="[FALLBACK] Finansal konularda dikkatli olun.",
            mood_score=7,
            lucky_number=random.randint(1, 99),
            lucky_color='Mavi',
            ai_provider='fallback'
        )


def generate_compatibility(user, sign1, sign2):
    """AI ile burç uyumu analizi oluştur"""
    try:
        ai_service = AIService()
        
        prompt = f"""Sen profesyonel bir astrolog ve ilişki danışmanısın.

{sign1.name} ve {sign2.name} burçları arasındaki uyumu analiz et.

Burç Bilgileri:
{sign1.name}: Element={sign1.get_element_display()}, Gezegen={sign1.ruling_planet}
{sign2.name}: Element={sign2.get_element_display()}, Gezegen={sign2.ruling_planet}

Aşağıdaki başlıklar altında analiz yap:

1. AŞK UYUMU: Romantik ilişki potansiyeli (3-4 cümle)
2. ARKADAŞLIK UYUMU: Dostluk ve arkadaşlık (3-4 cümle)
3. İŞ UYUMU: İş birliği ve çalışma uyumu (3-4 cümle)
4. ZORLUKLAR: Olası problemler ve dikkat edilmesi gerekenler (2-3 cümle)
5. TAVSİYELER: İlişkiyi güçlendirmek için öneriler (2-3 cümle)

Her başlığı büyük harfle yaz. Dürüst, yapıcı ve faydalı ol."""

        response = ai_service.generate_interpretation(
            question=prompt,
            cards=[],
            spread_name="Burç Uyumu"
        )
        
        sections = parse_horoscope_response(response)
        
        # Uyum skoru hesapla (basit)
        element_compatibility = {
            ('fire', 'fire'): 85, ('fire', 'air'): 90, ('fire', 'water'): 50, ('fire', 'earth'): 60,
            ('earth', 'earth'): 85, ('earth', 'water'): 90, ('earth', 'air'): 50, ('earth', 'fire'): 60,
            ('air', 'air'): 85, ('air', 'fire'): 90, ('air', 'earth'): 50, ('air', 'water'): 60,
            ('water', 'water'): 85, ('water', 'earth'): 90, ('water', 'fire'): 50, ('water', 'air'): 60,
        }
        
        score = element_compatibility.get((sign1.element, sign2.element), 70)
        
        compatibility = CompatibilityReading.objects.create(
            user=user,
            sign1=sign1,
            sign2=sign2,
            compatibility_score=score,
            love_compatibility=sections.get('AŞK UYUMU', 'Aşk uyumunuz yüksek.'),
            friendship_compatibility=sections.get('ARKADAŞLIK UYUMU', 'İyi arkadaş olabilirsiniz.'),
            work_compatibility=sections.get('İŞ UYUMU', 'İş birliğiniz verimli olabilir.'),
            challenges=sections.get('ZORLUKLAR', 'Bazı zorluklarla karşılaşabilirsiniz.'),
            advice=sections.get('TAVSİYELER', 'İletişime önem verin.'),
            ai_provider='gemini'
        )
        
        return compatibility
        
    except Exception as e:
        print(f"Compatibility generation error: {e}")
        return None


def parse_horoscope_response(response):
    """AI yanıtını bölümlere ayır"""
    sections = {}
    lines = response.split('\n')
    current_section = None
    current_content = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Başlık kontrolü (büyük harfle başlıyorsa)
        if line.isupper() or (line and line[0].isupper() and ':' in line):
            # Önceki bölümü kaydet
            if current_section and current_content:
                sections[current_section] = ' '.join(current_content).strip()
            
            # Yeni bölüm başlat
            current_section = line.replace(':', '').strip().upper()
            current_content = []
        elif current_section:
            current_content.append(line)
    
    # Son bölümü kaydet
    if current_section and current_content:
        sections[current_section] = ' '.join(current_content).strip()
    
    return sections


def generate_weekly_horoscope(zodiac_sign, week_start):
    """AI ile haftalık burç yorumu oluştur"""
    try:
        ai_service = AIService()
        week_end = week_start + timedelta(days=6)
        
        prompt = f"""Sen profesyonel bir astrolog ve burç yorumcususun.

{zodiac_sign.name} burcu için {week_start} - {week_end} tarihleri arası haftalık burç yorumu yap.

Burç Özellikleri:
- Element: {zodiac_sign.element}
- Yöneten Gezegen: {zodiac_sign.ruling_planet}
- Güçlü Yönler: {zodiac_sign.strengths[:100]}

Aşağıdaki başlıklar altında detaylı yorumla:

1. GENEL: Haftalık genel enerji ve öneriler (4-5 cümle)
2. AŞK: Aşk hayatı ve ilişkiler (4-5 cümle)
3. KARİYER: İş hayatı ve kariyer fırsatları (4-5 cümle)
4. SAĞLIK: Fiziksel ve mental sağlık (3-4 cümle)
5. FİNANS: Ekonomik durum ve yatırımlar (3-4 cümle)
6. ÖNEMLİ GÜNLER: Haftanın dikkat edilmesi gereken günleri (2-3 cümle)

Her başlığı büyük harfle yaz ve altına yorumu ekle. Pozitif, motive edici ve detaylı ol."""

        response = ai_service.generate_interpretation(
            question=prompt,
            cards=[],
            spread_name="Haftalık Burç"
        )
        
        sections = parse_horoscope_response(response)
        
        horoscope = WeeklyHoroscope.objects.create(
            zodiac_sign=zodiac_sign,
            week_start=week_start,
            general=sections.get('GENEL', 'Bu hafta sizin için önemli gelişmeler olabilir.'),
            love=sections.get('AŞK', 'Aşk hayatınızda hareketli bir hafta.'),
            career=sections.get('KARİYER', 'Kariyerinizde olumlu adımlar atabilirsiniz.'),
            health=sections.get('SAĞLIK', 'Sağlığınıza özen gösterin.'),
            money=sections.get('FİNANS', 'Finansal konularda dengeli olun.'),
            important_days=sections.get('ÖNEMLİ GÜNLER', 'Hafta ortası önemli.'),
            ai_provider='gemini'
        )
        
        return horoscope
        
    except Exception as e:
        print(f"Weekly horoscope generation error: {e}")
        return None


def generate_monthly_horoscope(zodiac_sign, year, month):
    """AI ile aylık burç yorumu oluştur"""
    try:
        ai_service = AIService()
        month_names = [
            '', 'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran',
            'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'
        ]
        
        prompt = f"""Sen profesyonel bir astrolog ve burç yorumcususun.

{zodiac_sign.name} burcu için {month_names[month]} {year} ayı burç yorumu yap.

Burç Özellikleri:
- Element: {zodiac_sign.element}
- Yöneten Gezegen: {zodiac_sign.ruling_planet}
- Karakteristik: {zodiac_sign.traits[:150]}

Aşağıdaki başlıklar altında kapsamlı yorumla:

1. GENEL: Aylık genel enerji ve trendler (5-6 cümle)
2. AŞK: Aşk hayatı, flört ve ilişkiler (5-6 cümle)
3. KARİYER: İş hayatı, projeler ve fırsatlar (5-6 cümle)
4. SAĞLIK: Fiziksel ve mental sağlık durumu (4-5 cümle)
5. FİNANS: Ekonomik durum, gelir ve giderler (4-5 cümle)
6. ÖNEMLİ TARİHLER: Ayın kritik günleri ve olayları (3-4 cümle)
7. TAVSİYELER: Ay boyunca yapılması gerekenler (3-4 cümle)

Her başlığı büyük harfle yaz. Detaylı, içgörü dolu ve faydalı ol."""

        response = ai_service.generate_interpretation(
            question=prompt,
            cards=[],
            spread_name="Aylık Burç"
        )
        
        sections = parse_horoscope_response(response)
        
        horoscope = MonthlyHoroscope.objects.create(
            zodiac_sign=zodiac_sign,
            year=year,
            month=month,
            general=sections.get('GENEL', 'Bu ay sizin için bereketli olacak.'),
            love=sections.get('AŞK', 'Aşk hayatınızda yeni başlangıçlar.'),
            career=sections.get('KARİYER', 'Kariyerinizde önemli gelişmeler yaşanabilir.'),
            health=sections.get('SAĞLIK', 'Sağlığınıza dikkat edin.'),
            money=sections.get('FİNANS', 'Finansal durumunuz dengeli seyredecek.'),
            important_dates=sections.get('ÖNEMLİ TARİHLER', 'Ay ortası önemli.'),
            advice=sections.get('TAVSİYELER', 'Sabırlı ve planlı olun.'),
            ai_provider='gemini'
        )
        
        return horoscope
        
    except Exception as e:
        print(f"Monthly horoscope generation error: {e}")
        return None
