"""
Zodiac AI Service - Burç yorumları için AI entegrasyonu
OpenRouter AI ile günlük, haftalık, aylık burç yorumları oluşturur
"""
import logging
import random
from datetime import timedelta
from django.utils import timezone
from tarot.openrouter_service import OpenRouterService

logger = logging.getLogger(__name__)


class ZodiacAIService:
    """
    Burç yorumları için AI servisi
    OpenRouter AI servisini kullanarak burç yorumları oluşturur
    """
    
    def __init__(self, model=None):
        """
        AI servisi başlat
        model: Kullanılacak AI model (None ise varsayılan: anthropic/claude-3.5-sonnet)
        """
        self.openrouter = OpenRouterService(model)
    
    def generate_daily_horoscope(self, zodiac_sign, date, language='tr'):
        """
        Belirli bir burç için günlük yorum oluştur
        
        Args:
            zodiac_sign: ZodiacSign model instance
            date: datetime.date object
            language: Yorum dili ('tr', 'en', 'de', 'fr')
            
        Returns:
            dict: Yorumların bulunduğu dictionary
        """
        try:
            logger.info(f"🌟 Günlük yorum oluşturuluyor: {zodiac_sign.name} - {date} ({language}) - Model: {self.openrouter.model}")
            
            # Dil talimatı
            language_instructions = {
                'tr': 'Türkçe yanıt ver. ',
                'en': 'Respond in English. ',
                'de': 'Antworte auf Deutsch. ',
                'fr': 'Répondez en français. '
            }
            lang_instruction = language_instructions.get(language, language_instructions['tr'])
            
            element_display = self._get_element_display(zodiac_sign.element)
            
            system_prompt = f"""{lang_instruction}Sen uzman bir astrolog ve burç yorumcususun. Pozitif, motive edici ve yapıcı yorumlar yaparsın."""
            
            prompt = f"""{zodiac_sign.name} burcu için {date} tarihli günlük burç yorumu yap.

Burç Özellikleri:
- Element: {element_display}
- Yöneten Gezegen: {zodiac_sign.ruling_planet}
- Güçlü Yönler: {zodiac_sign.strengths[:100]}
- Karakteristik: {zodiac_sign.traits[:100]}

Aşağıdaki başlıklar altında yorumla:

1. GENEL: Günün genel enerjisi ve öneriler (2-3 cümle)
2. AŞK: Aşk hayatı ve ilişkiler (2-3 cümle)
3. KARİYER: İş hayatı ve fırsatlar (2-3 cümle)
4. SAĞLIK: Fiziksel ve mental sağlık (2-3 cümle)
5. FİNANS: Ekonomik durum ve harcamalar (2-3 cümle)

Her başlığı büyük harfle yaz ve altına yorumu ekle."""

            response = self.openrouter.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=800,
                temperature=0.7
            )
            
            logger.info(f"🤖 AI Yanıtı alındı ({len(response)} karakter)")
            
            sections = self._parse_horoscope_response(response)
            logger.info(f"📊 Parse edilen sections: {list(sections.keys())}")
            
            # Şanslı sayı ve renk
            lucky_numbers = self._parse_lucky_numbers(zodiac_sign.lucky_numbers)
            lucky_colors = self._parse_lucky_colors(zodiac_sign.lucky_colors)
            
            result = {
                'general': sections.get('GENEL', 'Bugün sizin için güzel bir gün olacak.'),
                'love': sections.get('AŞK', 'Aşk hayatınızda huzur var.'),
                'career': sections.get('KARİYER', 'İşleriniz yolunda gidiyor.'),
                'health': sections.get('SAĞLIK', 'Sağlığınıza dikkat edin.'),
                'money': sections.get('FİNANS', 'Finansal durumunuz dengeli.'),
                'mood_score': random.randint(6, 10),
                'lucky_number': random.choice(lucky_numbers) if lucky_numbers else random.randint(1, 99),
                'lucky_color': random.choice(lucky_colors) if lucky_colors else 'Mavi',
                'ai_provider': 'openrouter'
            }
            
            logger.info(f"✅ Günlük yorum oluşturuldu: {zodiac_sign.name} - Model: {self.openrouter.model}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Günlük yorum hatası: {zodiac_sign.name} - {e}")
            return self._get_fallback_daily_horoscope(zodiac_sign)
    
    def generate_weekly_horoscope(self, zodiac_sign, week_start, language='tr'):
        """
        Haftalık burç yorumu oluştur
        
        Args:
            zodiac_sign: ZodiacSign model instance
            week_start: Haftanın başlangıç tarihi
            language: Yorum dili ('tr', 'en', 'de', 'fr')
            
        Returns:
            dict: Yorumların bulunduğu dictionary
        """
        try:
            week_end = week_start + timedelta(days=6)
            logger.info(f"📅 Haftalık yorum oluşturuluyor: {zodiac_sign.name} - {week_start} to {week_end} ({language})")
            
            # Dil talimatı
            language_instructions = {
                'tr': 'Türkçe yanıt ver. ',
                'en': 'Respond in English. ',
                'de': 'Antworte auf Deutsch. ',
                'fr': 'Répondez en français. '
            }
            lang_instruction = language_instructions.get(language, language_instructions['tr'])
            
            element_display = self._get_element_display(zodiac_sign.element)
            
            prompt = f"""{lang_instruction}Sen profesyonel bir astrolog ve burç yorumcususun.

{zodiac_sign.name} burcu için {week_start.strftime('%d.%m.%Y')} - {week_end.strftime('%d.%m.%Y')} tarihleri arası haftalık burç yorumu yap.

Burç Özellikleri:
- Element: {element_display}
- Yöneten Gezegen: {zodiac_sign.ruling_planet}
- Güçlü Yönler: {zodiac_sign.strengths[:100]}
- Zayıf Yönler: {zodiac_sign.weaknesses[:100]}

Aşağıdaki başlıklar altında detaylı yorumla:

1. GENEL: Haftalık genel enerji ve öneriler (4-5 cümle)
2. AŞK: Aşk hayatı ve ilişkiler (4-5 cümle)
3. KARİYER: İş hayatı ve kariyer fırsatları (4-5 cümle)
4. SAĞLIK: Fiziksel ve mental sağlık (3-4 cümle)
5. FİNANS: Ekonomik durum ve yatırımlar (3-4 cümle)
6. ÖNEMLİ GÜNLER: Haftanın dikkat edilmesi gereken günleri (2-3 cümle)

Her başlığı büyük harfle yaz ve altına yorumu ekle. Pozitif, motive edici ve detaylı ol."""

            system_prompt = f"""{lang_instruction}Sen profesyonel bir astrolog ve burç yorumcususun. Detaylı, içgörü dolu ve motive edici haftalık burç yorumları yazıyorsun."""

            response = self.openrouter.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=1000,
                temperature=0.7
            )
            
            sections = self._parse_horoscope_response(response)
            
            result = {
                'general': sections.get('GENEL', 'Bu hafta sizin için önemli gelişmeler olabilir.'),
                'love': sections.get('AŞK', 'Aşk hayatınızda hareketli bir hafta.'),
                'career': sections.get('KARİYER', 'Kariyerinizde olumlu adımlar atabilirsiniz.'),
                'health': sections.get('SAĞLIK', 'Sağlığınıza özen gösterin.'),
                'money': sections.get('FİNANS', 'Finansal konularda dengeli olun.'),
                'advice': sections.get('ÖNEMLİ GÜNLER', 'Hafta ortası önemli olabilir.'),
                'ai_provider': 'openrouter'
            }
            
            logger.info(f"✅ Haftalık yorum oluşturuldu: {zodiac_sign.name} - Provider: openrouter")
            return result
            
        except Exception as e:
            logger.error(f"❌ Haftalık yorum hatası: {zodiac_sign.name} - {e}")
            return self._get_fallback_weekly_horoscope(zodiac_sign)
    
    def generate_monthly_horoscope(self, zodiac_sign, year, month, language='tr'):
        """
        Aylık burç yorumu oluştur
        
        Args:
            zodiac_sign: ZodiacSign model instance
            year: Yıl
            month: Ay (1-12)
            language: Yorum dili ('tr', 'en', 'de', 'fr')
            
        Returns:
            dict: Yorumların bulunduğu dictionary
        """
        try:
            month_names = [
                '', 'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran',
                'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'
            ]
            
            logger.info(f"📆 Aylık yorum oluşturuluyor: {zodiac_sign.name} - {month_names[month]} {year} ({language})")
            
            # Dil talimatı
            language_instructions = {
                'tr': 'Türkçe yanıt ver. ',
                'en': 'Respond in English. ',
                'de': 'Antworte auf Deutsch. ',
                'fr': 'Répondez en français. '
            }
            lang_instruction = language_instructions.get(language, language_instructions['tr'])
            
            element_display = self._get_element_display(zodiac_sign.element)
            
            prompt = f"""{lang_instruction}Sen profesyonel bir astrolog ve burç yorumcususun.

{zodiac_sign.name} burcu için {month_names[month]} {year} ayı burç yorumu yap.

Burç Özellikleri:
- Element: {element_display}
- Yöneten Gezegen: {zodiac_sign.ruling_planet}
- Karakteristik: {zodiac_sign.traits[:150]}
- Güçlü Yönler: {zodiac_sign.strengths[:100]}

Aşağıdaki başlıklar altında kapsamlı yorumla:

1. GENEL: Aylık genel enerji ve trendler (5-6 cümle)
2. AŞK: Aşk hayatı, flört ve ilişkiler (5-6 cümle)
3. KARİYER: İş hayatı, projeler ve fırsatlar (5-6 cümle)
4. SAĞLIK: Fiziksel ve mental sağlık durumu (4-5 cümle)
5. FİNANS: Ekonomik durum, gelir ve giderler (4-5 cümle)
6. FIRSATLAR: Ay boyunca karşılaşabileceğiniz fırsatlar (3-4 cümle)
7. ZORLUKLAR: Dikkat edilmesi gereken zorluklar (3-4 cümle)
8. TAVSİYELER: Ay boyunca yapılması gerekenler (3-4 cümle)

Her başlığı büyük harfle yaz. Detaylı, içgörü dolu ve faydalı ol."""

            system_prompt = f"""{lang_instruction}Sen profesyonel bir astrolog ve burç yorumcususun. Kapsamlı, içgörü dolu ve faydalı aylık burç yorumları yazıyorsun."""

            response = self.openrouter.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=1200,
                temperature=0.7
            )
            
            sections = self._parse_horoscope_response(response)
            
            result = {
                'general': sections.get('GENEL', 'Bu ay sizin için bereketli olacak.'),
                'love': sections.get('AŞK', 'Aşk hayatınızda yeni başlangıçlar.'),
                'career': sections.get('KARİYER', 'Kariyerinizde önemli gelişmeler yaşanabilir.'),
                'health': sections.get('SAĞLIK', 'Sağlığınıza dikkat edin.'),
                'money': sections.get('FİNANS', 'Finansal durumunuz dengeli seyredecek.'),
                'opportunities': sections.get('FIRSATLAR', 'Yeni fırsatlar kapınızı çalabilir.'),
                'challenges': sections.get('ZORLUKLAR', 'Bazı zorluklarla karşılaşabilirsiniz.'),
                'ai_provider': 'openrouter'
            }
            
            logger.info(f"✅ Aylık yorum oluşturuldu: {zodiac_sign.name} - Provider: openrouter")
            return result
            
        except Exception as e:
            logger.error(f"❌ Aylık yorum hatası: {zodiac_sign.name} - {e}")
            return self._get_fallback_monthly_horoscope(zodiac_sign)
    
    def generate_compatibility_analysis(self, sign1, sign2, language='tr'):
        """
        İki burç arasında uyumluluk analizi oluştur
        
        Args:
            sign1: İlk ZodiacSign instance
            sign2: İkinci ZodiacSign instance
            language: Yorum dili ('tr', 'en', 'de', 'fr')
            
        Returns:
            dict: Uyumluluk analizi
        """
        try:
            logger.info(f"💕 Uyumluluk analizi: {sign1.name} & {sign2.name} ({language})")
            
            # Dil talimatı
            language_instructions = {
                'tr': 'Türkçe yanıt ver. ',
                'en': 'Respond in English. ',
                'de': 'Antworte auf Deutsch. ',
                'fr': 'Répondez en français. '
            }
            lang_instruction = language_instructions.get(language, language_instructions['tr'])
            
            element1 = self._get_element_display(sign1.element)
            element2 = self._get_element_display(sign2.element)
            
            prompt = f"""{lang_instruction}Sen profesyonel bir astrolog ve ilişki danışmanısın.

{sign1.name} ve {sign2.name} burçları arasındaki uyumu analiz et.

Burç Bilgileri:
{sign1.name}: Element={element1}, Gezegen={sign1.ruling_planet}, Kalite={sign1.get_quality_display()}
{sign2.name}: Element={element2}, Gezegen={sign2.ruling_planet}, Kalite={sign2.get_quality_display()}

Aşağıdaki başlıklar altında analiz yap:

1. AŞK UYUMU: Romantik ilişki potansiyeli (4-5 cümle)
2. ARKADAŞLIK UYUMU: Dostluk ve arkadaşlık (4-5 cümle)
3. İŞ UYUMU: İş birliği ve çalışma uyumu (4-5 cümle)
4. ZORLUKLAR: Olası problemler ve dikkat edilmesi gerekenler (3-4 cümle)
5. TAVSİYELER: İlişkiyi güçlendirmek için öneriler (3-4 cümle)

Her başlığı büyük harfle yaz. Dürüst, yapıcı ve faydalı ol."""

            system_prompt = f"""{lang_instruction}Sen profesyonel bir astrolog ve ilişki danışmanısın. Burç uyumları hakkında detaylı, yapıcı ve faydalı analizler yapıyorsun."""

            response = self.openrouter.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=1000,
                temperature=0.7
            )
            
            sections = self._parse_horoscope_response(response)
            
            # Uyum skoru hesapla (element uyumuna göre)
            compatibility_score = self._calculate_compatibility_score(sign1, sign2)
            
            result = {
                'compatibility_score': compatibility_score,
                'love_compatibility': sections.get('AŞK UYUMU', 'Aşk uyumunuz yüksek.'),
                'friendship_compatibility': sections.get('ARKADAŞLIK UYUMU', 'İyi arkadaş olabilirsiniz.'),
                'work_compatibility': sections.get('İŞ UYUMU', 'İş birliğiniz verimli olabilir.'),
                'challenges': sections.get('ZORLUKLAR', 'Bazı zorluklarla karşılaşabilirsiniz.'),
                'advice': sections.get('TAVSİYELER', 'İletişime önem verin.'),
                'ai_provider': 'openrouter'
            }
            
            logger.info(f"✅ Uyumluluk analizi oluşturuldu: {sign1.name} & {sign2.name} - Provider: openrouter")
            return result
            
        except Exception as e:
            logger.error(f"❌ Uyumluluk analizi hatası: {sign1.name} & {sign2.name} - {e}")
            return self._get_fallback_compatibility(sign1, sign2)
    
    # Helper Methods
    
    def _parse_horoscope_response(self, response):
        """AI yanıtını bölümlere ayır"""
        sections = {}
        lines = response.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Başlık kontrolü - "1. GENEL" veya "GENEL" gibi başlıkları yakala
            # Sayı ile başlayan başlıklar için
            if line and (line.isupper() or (':' in line and line.split(':')[0].isupper())):
                # Önceki bölümü kaydet
                if current_section and current_content:
                    sections[current_section] = ' '.join(current_content).strip()
                
                # Yeni bölüm başlat - sayıları ve noktalama işaretlerini kaldır
                section_name = line.replace(':', '').strip().upper()
                # "1. GENEL" -> "GENEL", "2. AŞK" -> "AŞK"
                section_name = section_name.split('. ', 1)[-1] if '. ' in section_name else section_name
                section_name = section_name.split(')', 1)[-1].strip() if ')' in section_name else section_name
                current_section = section_name
                current_content = []
            elif current_section:
                current_content.append(line)
        
        # Son bölümü kaydet
        if current_section and current_content:
            sections[current_section] = ' '.join(current_content).strip()
        
        return sections
    
    def _get_element_display(self, element):
        """Element kodunu Türkçe'ye çevir"""
        element_map = {
            'fire': 'Ateş',
            'earth': 'Toprak',
            'air': 'Hava',
            'water': 'Su'
        }
        return element_map.get(element, element)
    
    def _parse_lucky_numbers(self, lucky_numbers_str):
        """Şanslı sayıları parse et"""
        try:
            return [int(n.strip()) for n in lucky_numbers_str.split(',') if n.strip().isdigit()]
        except:
            return [7, 13, 21]
    
    def _parse_lucky_colors(self, lucky_colors_str):
        """Şanslı renkleri parse et"""
        try:
            return [c.strip() for c in lucky_colors_str.split(',') if c.strip()]
        except:
            return ['Mavi', 'Yeşil']
    
    def _calculate_compatibility_score(self, sign1, sign2):
        """Element ve kaliteye göre uyum skoru hesapla"""
        # Element uyumu
        element_compatibility = {
            ('fire', 'fire'): 85, ('fire', 'air'): 90, ('fire', 'water'): 50, ('fire', 'earth'): 60,
            ('earth', 'earth'): 85, ('earth', 'water'): 90, ('earth', 'air'): 50, ('earth', 'fire'): 60,
            ('air', 'air'): 85, ('air', 'fire'): 90, ('air', 'earth'): 50, ('air', 'water'): 60,
            ('water', 'water'): 85, ('water', 'earth'): 90, ('water', 'fire'): 50, ('water', 'air'): 60,
        }
        
        base_score = element_compatibility.get((sign1.element, sign2.element), 70)
        
        # Aynı kalitede olanlar biraz daha uyumlu
        if sign1.quality == sign2.quality:
            base_score += 5
        
        return min(base_score, 100)
    
    # Fallback Methods
    
    def _get_fallback_daily_horoscope(self, zodiac_sign):
        """AI başarısız olursa fallback günlük yorum"""
        return {
            'general': f"Bugün {zodiac_sign.name} burcu için enerjik bir gün olacak. Pozitif düşünün.",
            'love': "Aşk hayatınızda olumlu gelişmeler sizi bekliyor.",
            'career': "Kariyerinizde yeni fırsatlar doğabilir. Dikkatli olun.",
            'health': "Sağlığınıza özen gösterin. Dengeli beslenin.",
            'money': "Finansal konularda dikkatli olun. Gereksiz harcamalardan kaçının.",
            'mood_score': 7,
            'lucky_number': random.randint(1, 99),
            'lucky_color': 'Mavi',
            'ai_provider': 'fallback'
        }
    
    def _get_fallback_weekly_horoscope(self, zodiac_sign):
        """AI başarısız olursa fallback haftalık yorum"""
        return {
            'general': f"Bu hafta {zodiac_sign.name} burcu için önemli gelişmeler olabilir.",
            'love': "Aşk hayatınızda hareketli bir hafta sizi bekliyor.",
            'career': "Kariyerinizde olumlu adımlar atabilirsiniz.",
            'health': "Sağlığınıza özen gösterin. Düzenli uyuyun.",
            'money': "Finansal konularda dengeli olun. Planlı harcayın.",
            'advice': "Hafta ortası önemli olabilir. Dikkatli olun ve fırsatları değerlendirin.",
            'ai_provider': 'fallback'
        }
    
    def _get_fallback_monthly_horoscope(self, zodiac_sign):
        """AI başarısız olursa fallback aylık yorum"""
        return {
            'general': f"Bu ay {zodiac_sign.name} burcu için bereketli olacak.",
            'love': "Aşk hayatınızda yeni başlangıçlar sizi bekliyor.",
            'career': "Kariyerinizde önemli gelişmeler yaşanabilir.",
            'health': "Sağlığınıza dikkat edin. Spor yapın.",
            'money': "Finansal durumunuz dengeli seyredecek.",
            'opportunities': "Yeni fırsatlar kapınızı çalabilir.",
            'challenges': "Bazı zorluklarla karşılaşabilirsiniz ama üstesinden gelirsiniz.",
            'ai_provider': 'fallback'
        }
    
    def _get_fallback_compatibility(self, sign1, sign2):
        """AI başarısız olursa fallback uyumluluk"""
        score = self._calculate_compatibility_score(sign1, sign2)
        return {
            'compatibility_score': score,
            'love_compatibility': f"{sign1.name} ve {sign2.name} arasında orta düzeyde aşk uyumu var.",
            'friendship_compatibility': "İyi arkadaş olabilirsiniz. Birbirinizi anlayabilirsiniz.",
            'work_compatibility': "İş birliğiniz verimli olabilir. İletişime önem verin.",
            'challenges': "Bazı zorluklarla karşılaşabilirsiniz ama üstesinden gelebilirsiniz.",
            'advice': "İletişime önem verin. Birbirinizi anlamaya çalışın.",
            'ai_provider': 'fallback'
        }
