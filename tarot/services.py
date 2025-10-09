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
    
    def generate_interpretation(self, question, cards, spread_name):
        """
        Tarot yorumu üret
        
        Args:
            question: Kullanıcının sorusu
            cards: Seçilen kartlar listesi (dict: {position, card, is_reversed})
            spread_name: Yayılım adı
        
        Returns:
            str: AI tarafından üretilen yorum
        """
        logger.info(f"🎴 Yorum oluşturuluyor - Yayılım: {spread_name}, Kart sayısı: {len(cards)}")
        logger.info(f"❓ Soru: {question[:100]}...")
        
        # Prompt oluştur
        prompt = self._create_prompt(question, cards, spread_name)
        logger.info(f"📄 Prompt uzunluğu: {len(prompt)} karakter")
        
        try:
            if self.provider_name == 'openai':
                logger.info("🤖 AstroTarot AI yanıt üretiyor...")
                return self._generate_openai(prompt)
            elif self.provider_name == 'gemini':
                logger.info("🤖 AstroTarot AI yanıt üretiyor...")
                return self._generate_gemini(prompt)
            else:
                error_msg = f"Desteklenmeyen AI provider: {self.provider_name}"
                logger.error(f"❌ {error_msg}")
                raise Exception(error_msg)
        except Exception as e:
            logger.error(f"❌ AI Service Error: {str(e)}")
            logger.error(f"📋 Traceback:\n{traceback.format_exc()}")
            # Hata durumunda basit bir yorum döndür
            return self._generate_fallback_interpretation(question, cards, spread_name)
    
    def _create_prompt(self, question, cards, spread_name):
        """AI için prompt oluştur"""
        prompt = f"""Sen profesyonel bir tarot yorumcususun. Aşağıdaki tarot okuma için detaylı ve içgörülü bir yorum yap.

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
    
    def _generate_fallback_interpretation(self, question, cards, spread_name):
        """API hatası durumunda basit yorum üret"""
        interpretation = f"## {spread_name} Yorumu\n\n"
        interpretation += f"**Sorunuz:** {question}\n\n"
        interpretation += "### Çekilen Kartlar:\n\n"
        
        for card_info in cards:
            card = card_info['card']
            position = card_info['position']
            is_reversed = card_info['is_reversed']
            
            direction = "Ters" if is_reversed else "Düz"
            meaning = card.reversed_meaning if is_reversed else card.upright_meaning
            
            interpretation += f"**{position}. Kart: {card.name}** ({direction})\n"
            interpretation += f"{meaning}\n\n"
        
        interpretation += "\n*Not: Bu yorum AI servisine erişilemediği için otomatik oluşturulmuştur. "
        interpretation += "Daha detaylı yorum için lütfen daha sonra tekrar deneyin.*"
        
        return interpretation


class DailyCardService:
    """Günlük kart servisi"""
    
    def __init__(self):
        self.ai_service = AIService()
    
    def generate_daily_interpretation(self, card, is_reversed=False):
        """Günlük kart için özel yorum üret"""
        meaning = card.reversed_meaning if is_reversed else card.upright_meaning
        direction = "Ters" if is_reversed else "Düz"
        
        prompt = f"""Sen profesyonel bir tarot yorumcususun. Günün kartı için ilham verici bir yorum yap.

Günün Kartı: {card.name} ({direction})
Temel Anlam: {meaning}

Lütfen bu kart için:
1. Güne dair genel bir enerji değerlendirmesi yap
2. Kişisel gelişim ve fırsatlar hakkında ipuçları ver
3. Dikkat edilmesi gereken noktaları belirt
4. Pozitif ve motive edici bir dil kullan
5. Kısa ve öz tut (3-4 paragraf)

Türkçe olarak yanıt ver.
"""
        
        try:
            if self.ai_service.provider_name == 'openai':
                return self.ai_service._generate_openai(prompt)
            elif self.ai_service.provider_name == 'gemini':
                return self.ai_service._generate_gemini(prompt)
        except Exception as e:
            print(f"Daily card AI error: {str(e)}")
            # Fallback
            interpretation = f"## Günün Kartı: {card.name}\n\n"
            interpretation += f"**{direction} Pozisyon**\n\n"
            interpretation += f"{meaning}\n\n"
            interpretation += "Bu kart bugün için size önemli bir mesaj taşıyor. "
            interpretation += "Kartın enerjisini kullanarak gününüzü daha bilinçli yaşayabilirsiniz."
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
