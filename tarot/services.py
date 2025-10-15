"""
AI Servis sınıfları - AstroTarot AI entegrasyonu
"""
import openai
import google.generativeai as genai
import logging
import traceback
from django.conf import settings
from .models import SiteSettings, AIProvider

# Logger yapılandırması
logger = logging.getLogger(__name__)


class AIService:
    """AI yorumlama servisi"""
    
    def __init__(self, provider_name=None):
        """
        AI servisini başlat
        provider_name: 'openai' veya 'gemini' (None ise site ayarlarından alınır)
        """
        self.site_settings = SiteSettings.load()
        self.provider_name = provider_name or self.site_settings.default_ai_provider
        
        logger.info(f"🤖 AI Service başlatılıyor: {self.provider_name}")
        
        # API key ve model'i site ayarlarından al
        if self.provider_name == 'openai':
            self.api_key = self.site_settings.openai_api_key
            self.model = self.site_settings.openai_model
            logger.info(f"📝 AstroTarot AI Model: {self.model}")
            logger.info(f"🔑 AstroTarot AI Key: {'✅ Mevcut' if self.api_key else '❌ Yok'}")
        else:  # gemini
            self.api_key = self.site_settings.gemini_api_key
            self.model = self.site_settings.gemini_model
            logger.info(f"📝 AstroTarot AI Model: {self.model}")
            logger.info(f"🔑 AstroTarot AI Key: {'✅ Mevcut' if self.api_key else '❌ Yok'}")
            if self.api_key:
                logger.info(f"🔑 API Key ilk 10 karakter: {self.api_key[:10]}...")
        
        if not self.api_key:
            error_msg = f"{self.provider_name} için API anahtarı bulunamadı!"
            logger.error(f"❌ {error_msg}")
            raise Exception(error_msg)
    
    def generate_interpretation(self, question, cards, spread_name, language='tr'):
        """
        Tarot yorumu üret
        
        Args:
            question: Kullanıcının sorusu
            cards: Seçilen kartlar listesi (dict: {position, card, is_reversed})
            spread_name: Yayılım adı
            language: Yorum dili ('tr', 'en', 'de', 'fr')
        
        Returns:
            str: AI tarafından üretilen yorum
        """
        logger.info(f"🎴 Yorum oluşturuluyor - Yayılım: {spread_name}, Kart sayısı: {len(cards)}")
        logger.info(f"❓ Soru: {question[:100]}...")
        
        # Prompt oluştur
        prompt = self._create_prompt(question, cards, spread_name, language)
        logger.info(f"📄 Prompt uzunluğu: {len(prompt)} karakter")
        
        # Akıllı Fallback Sistemi: İlk provider başarısız olursa diğerini dene
        providers_to_try = []
        
        if self.provider_name == 'openai':
            providers_to_try = ['openai', 'gemini']
        elif self.provider_name == 'gemini':
            providers_to_try = ['gemini', 'openai']
        else:
            logger.error(f"❌ Desteklenmeyen AI provider: {self.provider_name}")
            return self._generate_fallback_interpretation(question, cards, spread_name)
        
        # Her provider'ı sırayla dene
        for provider in providers_to_try:
            try:
                logger.info(f"🤖 {provider.upper()} ile yanıt üretiliyor...")
                
                if provider == 'openai':
                    # OpenAI için API key kontrolü
                    if not self.site_settings.openai_api_key:
                        logger.warning("⚠️ OpenAI API key yok, atlanıyor...")
                        continue
                    result = self._generate_openai(prompt)
                    logger.info(f"✅ {provider.upper()} başarılı!")
                    return result
                    
                elif provider == 'gemini':
                    # Gemini için API key kontrolü
                    if not self.site_settings.gemini_api_key:
                        logger.warning("⚠️ Gemini API key yok, atlanıyor...")
                        continue
                    result = self._generate_gemini(prompt)
                    logger.info(f"✅ {provider.upper()} başarılı!")
                    return result
                    
            except Exception as e:
                error_msg = str(e)
                logger.error(f"❌ {provider.upper()} başarısız: {error_msg}")
                
                # Kota hatası mı kontrol et
                if 'quota' in error_msg.lower() or 'rate limit' in error_msg.lower():
                    logger.warning(f"⚠️ {provider.upper()} kota sınırına ulaşıldı, sonraki provider deneniyor...")
                elif '429' in error_msg:
                    logger.warning(f"⚠️ {provider.upper()} rate limit, sonraki provider deneniyor...")
                else:
                    logger.error(f"📋 Hata detayları:\n{traceback.format_exc()}")
                
                # Son provider değilse devam et
                if provider != providers_to_try[-1]:
                    logger.info(f"🔄 Sonraki provider deneniyor...")
                    continue
        
        # Tüm provider'lar başarısız olursa fallback
        logger.warning("⚠️ Tüm AI provider'lar başarısız oldu, fallback yorumu kullanılıyor...")
        return self._generate_fallback_interpretation(question, cards, spread_name, language)
    
    def _create_prompt(self, question, cards, spread_name, language='tr'):
        """AI için prompt oluştur"""
        # Dil talimatları
        language_instructions = {
            'tr': 'Türkçe yanıt ver. ',
            'en': 'Respond in English. ',
            'de': 'Antworte auf Deutsch. ',
            'fr': 'Répondez en français. '
        }
        
        lang_instruction = language_instructions.get(language, language_instructions['tr'])
        
        prompt = f"""{lang_instruction}Sen profesyonel bir tarot yorumcususun. Aşağıdaki tarot okuma için detaylı ve içgörülü bir yorum yap.

Yayılım Türü: {spread_name}
Soru: {question}

Çekilen Kartlar:
"""
        
        for card_info in cards:
            card = card_info['card']
            position = card_info['position']
            is_reversed = card_info['is_reversed']
            
            direction = "Ters" if is_reversed else "Düz"
            meaning = card.reversed_meaning if is_reversed else card.upright_meaning
            
            prompt += f"\n{position}. Pozisyon: {card.name} ({direction})"
            prompt += f"\n   Anlam: {meaning}\n"
        
        prompt += """
Lütfen bu kartları yorumlarken:
1. Her kartın konumuyla ilişkisini açıkla
2. Kartlar arasındaki bağlantıları ve enerjiyi yorumla
3. Kullanıcının sorusuna net ve yardımcı cevap ver
4. Pozitif ama gerçekçi bir yaklaşım sergile
5. Tavsiyeler ve öneriler sun

Yorumun profesyonel, anlaşılır ve içgörülü olsun. Türkçe olarak yanıt ver.
"""
        return prompt
    
    def _generate_openai(self, prompt):
        """AstroTarot AI kullanarak yorum üret"""
        try:
            logger.info(f"🤖 AstroTarot AI başlatılıyor - Model: {self.model}")
            
            # Yeni OpenAI API (v1.0+) kullanımı
            client = openai.OpenAI(api_key=self.api_key)
            
            # o1 modelleri için özel parametreler
            is_o1_model = self.model.startswith('o1')
            
            logger.info("📤 AstroTarot AI'ya istek gönderiliyor...")
            
            if is_o1_model:
                # o1 modelleri system message desteklemiyor, temperature ve max_tokens farklı
                logger.info("🧠 AstroTarot AI Advanced Reasoning Model kullanılıyor")
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": f"Sen profesyonel bir tarot yorumcususun. Detaylı ve içgörülü yorumlar yaparsın.\n\n{prompt}"}
                    ],
                    # o1 modelleri için temperature ve max_tokens parametreleri desteklenmiyor
                )
            else:
                # Normal GPT modelleri (gpt-4o, gpt-4-turbo, vb.)
                logger.info("💬 AstroTarot AI Standard Model kullanılıyor")
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Sen profesyonel bir tarot yorumcususun. Detaylı ve içgörülü yorumlar yaparsın."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1500
                )
            
            result = response.choices[0].message.content
            if result:
                logger.info(f"✅ OpenAI yanıt alındı - Uzunluk: {len(result)} karakter")
            else:
                logger.warning("⚠️ OpenAI yanıt boş!")
            
            # Token kullanımı logla
            if hasattr(response, 'usage') and response.usage:
                logger.info(f"📊 Token kullanımı: {response.usage.total_tokens}")
            
            return result or ""
            
        except Exception as e:
            logger.error(f"❌ AstroTarot AI Hatası: {str(e)}")
            logger.error(f"📋 Traceback:\n{traceback.format_exc()}")
            raise
    
    def _generate_gemini(self, prompt):
        """AstroTarot AI kullanarak yorum üret"""
        try:
            logger.info(f"🤖 AstroTarot AI başlatılıyor - Model: {self.model}")
            logger.info(f"🔑 API Key kontrolü: {len(self.api_key) if self.api_key else 0} karakter")
            
            # API anahtarını ayarla
            logger.info("⚙️ Gemini API yapılandırılıyor...")
            genai.configure(api_key=self.api_key)
            logger.info("✅ Gemini API yapılandırıldı")
            
            # Model oluştur (site ayarlarından gelen model)
            logger.info(f"🤖 Model oluşturuluyor: {self.model}")
            model = genai.GenerativeModel(self.model)
            logger.info("✅ Model oluşturuldu")
            
            # Yorum üret
            logger.info("📤 Gemini'ye istek gönderiliyor...")
            logger.info(f"📝 Prompt başlangıcı: {prompt[:200]}...")
            
            response = model.generate_content(prompt)
            logger.info("📥 Gemini'den yanıt alındı")
            
            if not response:
                logger.error("❌ Gemini yanıtı None!")
                raise Exception("Gemini'den yanıt alınamadı (None)")
            
            logger.info(f"🔍 Response tipi: {type(response)}")
            logger.info(f"🔍 Response attributes: {dir(response)}")
            
            if hasattr(response, 'text'):
                result = response.text
                logger.info(f"✅ Gemini yanıt alındı - Uzunluk: {len(result) if result else 0} karakter")
                if result:
                    logger.info(f"📝 Yanıt başlangıcı: {result[:200]}...")
                return result
            else:
                logger.error(f"❌ Response'da 'text' attribute yok!")
                logger.error(f"📋 Response içeriği: {response}")
                raise Exception("AstroTarot AI response'unda text attribute bulunamadı")
                
        except Exception as e:
            logger.error(f"❌ AstroTarot AI Hatası: {str(e)}")
            logger.error(f"🔍 Hata tipi: {type(e).__name__}")
            logger.error(f"📋 Traceback:\n{traceback.format_exc()}")
            raise
    
    def _generate_fallback_interpretation(self, question, cards, spread_name, language='tr'):
        """API hatası durumunda basit yorum üret"""
        # Dile göre çeviriler
        translations = {
            'tr': {
                'interpretation': 'Yorumu',
                'your_question': 'Sorunuz',
                'drawn_cards': 'Çekilen Kartlar',
                'card': 'Kart',
                'upright': 'Düz',
                'reversed': 'Ters',
                'note': 'Not: Bu yorum AI servisine erişilemediği için otomatik oluşturulmuştur. Daha detaylı yorum için lütfen daha sonra tekrar deneyin.'
            },
            'en': {
                'interpretation': 'Reading',
                'your_question': 'Your Question',
                'drawn_cards': 'Drawn Cards',
                'card': 'Card',
                'upright': 'Upright',
                'reversed': 'Reversed',
                'note': 'Note: This interpretation was automatically generated because AI service is unavailable. Please try again later for a more detailed reading.'
            },
            'de': {
                'interpretation': 'Deutung',
                'your_question': 'Ihre Frage',
                'drawn_cards': 'Gezogene Karten',
                'card': 'Karte',
                'upright': 'Aufrecht',
                'reversed': 'Umgekehrt',
                'note': 'Hinweis: Diese Deutung wurde automatisch erstellt, da der KI-Dienst nicht verfügbar ist. Bitte versuchen Sie es später erneut für eine detailliertere Deutung.'
            },
            'fr': {
                'interpretation': 'Lecture',
                'your_question': 'Votre Question',
                'drawn_cards': 'Cartes Tirées',
                'card': 'Carte',
                'upright': 'Endroit',
                'reversed': 'Renversé',
                'note': 'Remarque : Cette interprétation a été générée automatiquement car le service IA est indisponible. Veuillez réessayer plus tard pour une lecture plus détaillée.'
            }
        }
        
        t = translations.get(language, translations['tr'])
        
        interpretation = f"## {spread_name} {t['interpretation']}\n\n"
        interpretation += f"**{t['your_question']}:** {question}\n\n"
        interpretation += f"### {t['drawn_cards']}:\n\n"
        
        for card_info in cards:
            card = card_info['card']
            position = card_info['position']
            is_reversed = card_info['is_reversed']
            
            direction = t['reversed'] if is_reversed else t['upright']
            meaning = card.reversed_meaning if is_reversed else card.upright_meaning
            
            interpretation += f"**{position}. {t['card']}: {card.name}** ({direction})\n"
            interpretation += f"{meaning}\n\n"
        
        interpretation += f"\n*{t['note']}*"
        
        return interpretation


class DailyCardService:
    """Günlük kart servisi"""
    
    def __init__(self):
        self.ai_service = AIService()
    
    def generate_daily_interpretation(self, card, is_reversed=False, language='tr'):
        """Günlük kart için özel yorum üret"""
        meaning = card.reversed_meaning if is_reversed else card.upright_meaning
        
        # Dil talimatları ve çeviriler
        language_map = {
            'tr': {
                'instruction': 'Türkçe yanıt ver. ',
                'direction_upright': 'Düz',
                'direction_reversed': 'Ters'
            },
            'en': {
                'instruction': 'Respond in English. ',
                'direction_upright': 'Upright',
                'direction_reversed': 'Reversed'
            },
            'de': {
                'instruction': 'Antworte auf Deutsch. ',
                'direction_upright': 'Aufrecht',
                'direction_reversed': 'Umgekehrt'
            },
            'fr': {
                'instruction': 'Répondez en français. ',
                'direction_upright': 'Endroit',
                'direction_reversed': 'Renversé'
            }
        }
        
        lang = language_map.get(language, language_map['tr'])
        direction = lang['direction_reversed'] if is_reversed else lang['direction_upright']
        
        prompt = f"""{lang['instruction']}Sen profesyonel bir tarot yorumcususun. Günün kartı için ilham verici bir yorum yap.

Günün Kartı: {card.name} ({direction})
Temel Anlam: {meaning}

Lütfen bu kart için:
1. Güne dair genel bir enerji değerlendirmesi yap
2. Kişisel gelişim ve fırsatlar hakkında ipuçları ver
3. Dikkat edilmesi gereken noktaları belirt
4. Pozitif ve motive edici bir dil kullan
5. Kısa ve öz tut (3-4 paragraf)
"""
        
        try:
            if self.ai_service.provider_name == 'openai':
                return self.ai_service._generate_openai(prompt)
            elif self.ai_service.provider_name == 'gemini':
                return self.ai_service._generate_gemini(prompt)
        except Exception as e:
            print(f"Daily card AI error: {str(e)}")
            # Fallback with language support
            fallback_translations = {
                'tr': {
                    'title': 'Günün Kartı',
                    'position': 'Pozisyon',
                    'message': 'Bu kart bugün için size önemli bir mesaj taşıyor. Kartın enerjisini kullanarak gününüzü daha bilinçli yaşayabilirsiniz.'
                },
                'en': {
                    'title': "Today's Card",
                    'position': 'Position',
                    'message': 'This card carries an important message for you today. Use the card\'s energy to live your day more consciously.'
                },
                'de': {
                    'title': 'Karte des Tages',
                    'position': 'Position',
                    'message': 'Diese Karte trägt heute eine wichtige Botschaft für Sie. Nutzen Sie die Energie der Karte, um Ihren Tag bewusster zu leben.'
                },
                'fr': {
                    'title': 'Carte du Jour',
                    'position': 'Position',
                    'message': 'Cette carte porte un message important pour vous aujourd\'hui. Utilisez l\'énergie de la carte pour vivre votre journée plus consciemment.'
                }
            }
            
            fb = fallback_translations.get(language, fallback_translations['tr'])
            interpretation = f"## {fb['title']}: {card.name}\n\n"
            interpretation += f"**{direction} {fb['position']}**\n\n"
            interpretation += f"{meaning}\n\n"
            interpretation += fb['message']
            return interpretation


class ImageGenerationService:
    """Gemini 2.5 Flash ile görsel üretimi"""
    
    def __init__(self):
        """Gemini 2.5 Flash için servis başlat"""
        self.site_settings = SiteSettings.load()
        self.api_key = self.site_settings.gemini_api_key
        
        if not self.api_key:
            raise Exception("Gemini API anahtarı bulunamadı!")
        
        # Gemini'yi yapılandır
        genai.configure(api_key=self.api_key)
        
        # Imagen 3 modeli için
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        logger.info("🎨 Image Generation Service başlatıldı (Gemini 2.5 Flash)")
    
    def generate_tarot_card_image(self, card_name, card_meaning, style="mystical"):
        """
        Tarot kartı için görsel üret
        
        Args:
            card_name: Kart adı
            card_meaning: Kartın anlamı
            style: Görsel stili (mystical, modern, classic, etc.)
        
        Returns:
            str: Üretilen görselin URL'i veya base64 string
        """
        logger.info(f"🎨 Tarot kartı görseli üretiliyor: {card_name}")
        
        prompt = f"""Create a beautiful tarot card image for '{card_name}'.
        
Style: {style}, mystical, spiritual, detailed artwork
Meaning: {card_meaning[:200]}

The image should be:
- High quality artistic tarot card design
- Rich in symbolism and mystical elements
- Professional tarot card aesthetics
- Vibrant colors with spiritual atmosphere
- Traditional tarot card composition

Do not include any text or numbers in the image.
"""
        
        try:
            response = self.model.generate_content(prompt)
            
            if response.parts:
                # Görsel verisi varsa al
                for part in response.parts:
                    if hasattr(part, 'inline_data'):
                        image_data = part.inline_data.data
                        logger.info("✅ Tarot kartı görseli oluşturuldu")
                        return image_data
            
            logger.warning("⚠️ Görsel üretilemedi")
            return None
            
        except Exception as e:
            logger.error(f"❌ Görsel üretim hatası: {str(e)}")
            logger.error(f"📋 Traceback:\n{traceback.format_exc()}")
            return None
    
    def generate_zodiac_symbol_image(self, zodiac_name, element, traits):
        """
        Burç sembolü için görsel üret
        
        Args:
            zodiac_name: Burç adı
            element: Element (Ateş, Su, Toprak, Hava)
            traits: Karakter özellikleri
        
        Returns:
            str: Üretilen görselin URL'i veya base64 string
        """
        logger.info(f"🌟 Burç sembolü görseli üretiliyor: {zodiac_name}")
        
        element_colors = {
            'fire': 'red, orange, warm fiery colors',
            'earth': 'brown, green, earthy tones',
            'air': 'light blue, white, airy colors',
            'water': 'blue, turquoise, flowing colors'
        }
        
        color_scheme = element_colors.get(element, 'cosmic colors')
        
        prompt = f"""Create a beautiful zodiac sign symbol image for '{zodiac_name}'.

Element: {element}
Colors: {color_scheme}
Traits: {traits[:200]}

The image should be:
- Artistic zodiac constellation design
- Mystical and celestial atmosphere
- Stars, cosmos, and astrological elements
- Rich symbolic representation
- Professional astrology artwork
- Vibrant cosmic colors

Do not include any text in the image.
"""
        
        try:
            response = self.model.generate_content(prompt)
            
            if response.parts:
                for part in response.parts:
                    if hasattr(part, 'inline_data'):
                        image_data = part.inline_data.data
                        logger.info("✅ Burç sembolü görseli oluşturuldu")
                        return image_data
            
            logger.warning("⚠️ Görsel üretilemedi")
            return None
            
        except Exception as e:
            logger.error(f"❌ Görsel üretim hatası: {str(e)}")
            logger.error(f"📋 Traceback:\n{traceback.format_exc()}")
            return None
    
    def generate_reading_background_image(self, theme="mystical night"):
        """
        Okuma arka plan görseli üret
        
        Args:
            theme: Tema (mystical night, cosmic space, ancient temple, etc.)
        
        Returns:
            str: Üretilen görselin URL'i veya base64 string
        """
        logger.info(f"🖼️ Arka plan görseli üretiliyor: {theme}")
        
        prompt = f"""Create a beautiful background image for tarot reading.

Theme: {theme}

The image should be:
- Mystical and atmospheric
- Perfect for tarot card reading backdrop
- Rich in spiritual and magical elements
- Deep, rich colors
- Professional artistic quality
- Suitable as a website background

Do not include any text or specific symbols, just the atmospheric background.
"""
        
        try:
            response = self.model.generate_content(prompt)
            
            if response.parts:
                for part in response.parts:
                    if hasattr(part, 'inline_data'):
                        image_data = part.inline_data.data
                        logger.info("✅ Arka plan görseli oluşturuldu")
                        return image_data
            
            logger.warning("⚠️ Görsel üretilemedi")
            return None
            
        except Exception as e:
            logger.error(f"❌ Görsel üretim hatası: {str(e)}")
            logger.error(f"📋 Traceback:\n{traceback.format_exc()}")
            return None
