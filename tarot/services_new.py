"""
AI Servis sınıfları - OpenRouter.ai entegrasyonu
Tek bir API ile tüm AI modellerine erişim
"""
import logging
from django.core.cache import cache
from .openrouter_service import OpenRouterService, DEFAULT_TAROT_PROMPT, DEFAULT_ZODIAC_PROMPT

# Logger yapılandırması
logger = logging.getLogger(__name__)


class AIService:
    """AI yorumlama servisi - OpenRouter.ai kullanır"""
    
    def __init__(self, provider_name=None, model=None):
        """
        AI servisini başlat
        provider_name: Geriye uyumluluk için (kullanılmıyor)
        model: OpenRouter model adı (örn: 'anthropic/claude-3.5-sonnet')
        """
        try:
            self.openrouter = OpenRouterService(model=model)
            self.provider_name = self.openrouter.provider_name
            logger.info(f"✅ AI Service başlatıldı: {self.openrouter.model}")
        except Exception as e:
            logger.error(f"❌ AI Service başlatılamadı: {str(e)}")
            raise
    
    def generate_interpretation(self, question, cards, spread_name, language='tr'):
        """Tarot yorumu üret"""
        logger.info(f"🎴 Yorum oluşturuluyor - Yayılım: {spread_name}")
        
        # Cache kontrolü
        cache_key = f"tarot_{hash(question)}_{hash(str(cards))}_{spread_name}_{language}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Prompt oluştur
        prompt = self._create_prompt(question, cards, spread_name, language)
        
        try:
            result = self.openrouter.generate_response(
                prompt=prompt,
                system_prompt=DEFAULT_TAROT_PROMPT,
                max_tokens=1000,
                temperature=0.8
            )
            cache.set(cache_key, result, 3600)
            return result
        except Exception as e:
            logger.error(f"❌ AI hatası: {str(e)}")
            return self._generate_fallback_interpretation(question, cards, spread_name, language)
    
    def _create_prompt(self, question, cards, spread_name, language='tr'):
        """Prompt oluştur"""
        prompt = f"Tarot okuma yapıyoruz. Yayılım: {spread_name}\n\n"
        prompt += f"Soru: {question}\n\nÇekilen Kartlar:\n"
        
        for card_data in cards:
            position = card_data.get('position', '')
            card_obj = card_data.get('card', {})
            card_name = card_obj.get('name', 'Bilinmeyen') if isinstance(card_obj, dict) else getattr(card_obj, 'name', 'Bilinmeyen')
            is_reversed = card_data.get('is_reversed', False)
            
            prompt += f"- Pozisyon: {position}\n  Kart: {card_name}"
            if is_reversed:
                prompt += " (Ters)"
            prompt += "\n"
        
        prompt += "\nLütfen detaylı, anlayışlı ve içgörü dolu bir yorum yaz."
        return prompt
    
    def _generate_fallback_interpretation(self, question, cards, spread_name, language='tr'):
        """Fallback yorum"""
        card_names = []
        for c in cards:
            card_obj = c.get('card', {})
            name = card_obj.get('name', '') if isinstance(card_obj, dict) else getattr(card_obj, 'name', '')
            card_names.append(name)
        
        return f"""
Şu anda AI servisi geçici olarak kullanılamıyor.

Çekilen kartlarınız: {', '.join(card_names)}

Lütfen daha sonra tekrar deneyin.
"""


class DailyCardService:
    """Günlük kart servisi"""
    
    def __init__(self, provider_name=None, model=None):
        self.ai_service = AIService(provider_name=provider_name, model=model)
    
    def generate_daily_interpretation(self, card, is_reversed=False, language='tr'):
        """Günlük kart yorumu üret"""
        meaning = card.reversed_meaning if is_reversed else card.upright_meaning
        
        prompt = f"""Sen profesyonel bir tarot yorumcususun. Günün kartı için ilham verici bir yorum yap.

Günün Kartı: {card.name} ({'Ters' if is_reversed else 'Düz'})
Temel Anlam: {meaning}

Lütfen bu kart için:
1. Güne dair genel bir enerji değerlendirmesi yap
2. Kişisel gelişim ve fırsatlar hakkında ipuçları ver
3. Pozitif ve motive edici bir dil kullan
4. Kısa ve öz tut (3-4 paragraf)
"""
        
        try:
            result = self.ai_service.openrouter.generate_response(
                prompt=prompt,
                system_prompt=DEFAULT_TAROT_PROMPT,
                max_tokens=800,
                temperature=0.8
            )
            return result
        except Exception as e:
            logger.error(f"❌ Daily card AI error: {str(e)}")
            return f"## Günün Kartı: {card.name}\n\n{'Ters' if is_reversed else 'Düz'} Pozisyon\n\n{meaning}"


class ImageGenerationService:
    """Görsel üretme servisi (Placeholder)"""
    
    def __init__(self):
        logger.info("🎨 ImageGenerationService başlatıldı (Placeholder)")
    
    def generate_tarot_card_image(self, card_name, description):
        """Görsel üret (henüz desteklenmiyor)"""
        logger.warning("⚠️ Görsel üretme henüz desteklenmiyor")
        return None
    
    def generate_zodiac_background(self, zodiac_sign, theme='mystical'):
        """Burç görseli üret (henüz desteklenmiyor)"""
        logger.warning("⚠️ Görsel üretme henüz desteklenmiyor")
        return None
    
    def generate_zodiac_symbol_image(self, zodiac_name, element, traits):
        """Burç sembolü üret (henüz desteklenmiyor)"""
        logger.warning("⚠️ Görsel üretme henüz desteklenmiyor")
        return None
    
    def generate_reading_background_image(self, theme="mystical night"):
        """Arka plan görseli üret (henüz desteklenmiyor)"""
        logger.warning("⚠️ Görsel üretme henüz desteklenmiyor")
        return None
