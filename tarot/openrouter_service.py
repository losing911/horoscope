"""
OpenRouter.ai API Servisi
Tek API key ile tüm AI modellere erişim
"""

import os
import requests
from decouple import config
from django.core.cache import cache


class OpenRouterService:
    """OpenRouter.ai entegrasyon servisi"""
    
    def __init__(self, model=None):
        """
        Args:
            model: Kullanılacak model adı (örn: "anthropic/claude-3.5-sonnet")
                  Belirtilmezse environment'tan alınır
        """
        self.api_key = config('OPENROUTER_API_KEY', default='')
        self.model = model or config('OPENROUTER_MODEL', default='anthropic/claude-3.5-sonnet')
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable gerekli!")
    
    def generate_response(self, prompt, system_prompt=None, max_tokens=1000, temperature=0.7):
        """
        OpenRouter API kullanarak AI yanıtı üret
        
        Args:
            prompt: Kullanıcı mesajı
            system_prompt: Sistem mesajı (opsiyonel)
            max_tokens: Maksimum token sayısı
            temperature: Yaratıcılık seviyesi (0.0-2.0)
            
        Returns:
            str: AI yanıtı
        """
        # Cache kontrolü
        cache_key = f"openrouter_{hash(prompt)}_{self.model}"
        cached_response = cache.get(cache_key)
        if cached_response:
            return cached_response
        
        # Mesajları hazırla
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # API isteği
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": config('SITE_URL', default='https://tarot-yorum.fun'),
            "X-Title": "AstroTarot",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            
            # Cache'e kaydet (1 saat)
            cache.set(cache_key, ai_response, 3600)
            
            return ai_response
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"OpenRouter API hatası: {str(e)}")
        except (KeyError, IndexError) as e:
            raise Exception(f"OpenRouter yanıt formatı hatası: {str(e)}")
    
    def get_available_models(self):
        """Kullanılabilir modelleri listele"""
        try:
            response = requests.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10
            )
            response.raise_for_status()
            return response.json()['data']
        except Exception as e:
            print(f"Model listesi alınamadı: {e}")
            return []
    
    @property
    def provider_name(self):
        """Kullanılan provider adı"""
        return f"openrouter:{self.model}"


# Varsayılan sistem promptları
DEFAULT_TAROT_PROMPT = """Sen uzman bir tarot yorumcususun. Kartların anlamlarını detaylı, anlayışlı 
ve empatik bir şekilde açıkla. Yorumların pozitif ama gerçekçi olsun. Türkçe yaz."""

DEFAULT_ZODIAC_PROMPT = """Sen uzman bir astrologsun. Burç yorumlarını detaylı, pozitif ve 
motive edici bir şekilde yaz. Günlük hayata uygulanabilir tavsiyeler ver. Türkçe yaz."""
