"""
Blog AI Servisleri
Gemini ve OpenAI ile blog içeriği üretimi
"""

import logging
from typing import Dict, List, Optional
from tarot.services import AIService

logger = logging.getLogger(__name__)


class BlogAIService:
    """AI destekli blog içerik üretimi"""
    
    def __init__(self):
        self.ai_service = AIService()
    
    def generate_blog_post(self, topic: str, category: str = None, 
                          keywords: List[str] = None, word_count: int = 800) -> Dict:
        """
        Belirli bir konu hakkında tam blog yazısı üret
        
        Args:
            topic: Blog konusu
            category: Kategori (Tarot, Astroloji, vs.)
            keywords: Anahtar kelimeler
            word_count: Yaklaşık kelime sayısı
        
        Returns:
            {
                'title': str,
                'excerpt': str,
                'content': str,
                'meta_title': str,
                'meta_description': str,
                'meta_keywords': str,
                'suggested_tags': List[str]
            }
        """
        try:
            # Prompt oluştur
            prompt = self._create_blog_prompt(topic, category, keywords, word_count)
            
            # AI'dan içerik al
            response = self.ai_service.generate_interpretation(
                question=f"Blog yazısı oluştur: {topic}",
                cards=[],  # Blog için kart gerekmez
                spread_name="Blog Generation"
            )
            
            # Yanıtı parse et
            return self._parse_blog_response(response, topic)
            
        except Exception as e:
            logger.error(f"❌ Blog üretimi hatası: {e}")
            return self._get_fallback_blog(topic)
    
    def generate_seo_meta(self, post) -> Dict:
        """
        Mevcut bir blog yazısı için SEO metaları üret
        
        Args:
            post: BlogPost instance
        
        Returns:
            {
                'meta_title': str,
                'meta_description': str,
                'meta_keywords': str
            }
        """
        try:
            prompt = f"""
Aşağıdaki blog yazısı için SEO optimize edilmiş metalar üret:

BAŞLIK: {post.title}
ÖZET: {post.excerpt}
KATEGORİ: {post.category.name if post.category else 'Genel'}

Lütfen şu formatta yanıt ver:

META BAŞLIK: [60 karakterden kısa, SEO optimize]
META AÇIKLAMA: [155 karakterden kısa, etkileyici, harekete geçirici]
ANAHTAR KELİMELER: [virgülle ayrılmış 5-10 anahtar kelime]

Tarot ve astroloji terimleri kullan, Türkçe olsun.
"""
            
            response = self.ai_service.generate_interpretation(
                question="SEO meta üret",
                cards=[],
                spread_name="SEO Generation"
            )
            
            return self._parse_seo_response(response, post)
            
        except Exception as e:
            logger.error(f"❌ SEO meta üretimi hatası: {e}")
            return {
                'meta_title': post.title[:60],
                'meta_description': post.excerpt[:160],
                'meta_keywords': ''
            }
    
    def suggest_related_topics(self, post) -> List[str]:
        """
        Blog yazısına benzer konu önerileri üret
        
        Args:
            post: BlogPost instance
        
        Returns:
            List of topic suggestions
        """
        try:
            prompt = f"""
Bu blog yazısıyla ilgili 5 yeni blog konusu öner:

BAŞLIK: {post.title}
KATEGORİ: {post.category.name if post.category else 'Genel'}
ÖZET: {post.excerpt}

Her satıra bir konu önerisi yaz. Tarot ve astroloji ile ilgili olsun.
"""
            
            response = self.ai_service.generate_interpretation(
                question="İlgili konular öner",
                cards=[],
                spread_name="Topic Suggestion"
            )
            
            # Her satırı bir konu olarak al
            topics = [line.strip() for line in response.split('\n') 
                     if line.strip() and not line.startswith('#')]
            
            return topics[:5]
            
        except Exception as e:
            logger.error(f"❌ Konu önerisi hatası: {e}")
            return []
    
    def generate_image_prompt(self, post) -> str:
        """
        Blog görseli için AI image generation prompt'u oluştur
        
        Args:
            post: BlogPost instance
        
        Returns:
            Image generation prompt (DALL-E, Midjourney, vs. için)
        """
        try:
            prompt = f"""
Bu blog yazısı için görsel üretim prompt'u oluştur:

BAŞLIK: {post.title}
KATEGORİ: {post.category.name if post.category else 'Genel'}

Mystical, tarot, astrology temalı bir görsel olsun.
DALL-E veya Midjourney için uygun İngilizce prompt ver.
Sadece prompt'u yaz, açıklama yapma.
"""
            
            response = self.ai_service.generate_interpretation(
                question="Görsel prompt oluştur",
                cards=[],
                spread_name="Image Prompt Generation"
            )
            
            # İlk satırı al (genellikle prompt burada)
            lines = [l.strip() for l in response.split('\n') if l.strip()]
            return lines[0] if lines else "mystical tarot card scene, magical atmosphere"
            
        except Exception as e:
            logger.error(f"❌ Görsel prompt hatası: {e}")
            return "mystical tarot and astrology themed image, magical atmosphere, detailed illustration"
    
    # Private methods
    
    def _create_blog_prompt(self, topic: str, category: str = None, 
                           keywords: List[str] = None, word_count: int = 800) -> str:
        """Blog üretim prompt'u oluştur"""
        
        keywords_str = ', '.join(keywords) if keywords else ''
        category_str = f" ({category} kategorisinde)" if category else ""
        
        prompt = f"""
Sen bir tarot ve astroloji uzmanısın. Aşağıdaki konu hakkında detaylı bir blog yazısı yaz:

KONU: {topic}{category_str}
KELİME SAYISI: Yaklaşık {word_count} kelime
{f'ANAHTAR KELİMELER: {keywords_str}' if keywords_str else ''}

Blog yazısını şu formatta oluştur:

# BAŞLIK
[Etkileyici, SEO uyumlu başlık]

## ÖZET
[2-3 cümlelik özet]

## GİRİŞ
[Konuya giriş, okuyucunun ilgisini çekmeli]

## ANA İÇERİK
[Detaylı açıklama, örnekler, tarot/astroloji terimleri]
[Alt başlıklar kullan]
[Madde işaretleri ve numaralandırma kullan]

## SONUÇ
[Özet ve harekete geçirici sonuç]

## ETİKETLER
[virgülle ayrılmış 5-8 etiket]

Türkçe yaz, profesyonel ama samimi bir dil kullan.
Tarot ve astroloji terimleri kullan.
Okuyucu için değerli bilgiler ver.
"""
        return prompt
    
    def _parse_blog_response(self, response: str, topic: str) -> Dict:
        """AI yanıtını blog yapısına parse et"""
        
        try:
            lines = response.split('\n')
            
            # Başlık bul (# ile başlayan ilk satır)
            title = topic  # Varsayılan
            for line in lines:
                if line.startswith('# ') and not line.startswith('## '):
                    title = line.replace('# ', '').strip()
                    break
            
            # Özet bul (## ÖZET veya ## SUMMARY)
            excerpt = ""
            in_excerpt = False
            for line in lines:
                if '## ÖZET' in line.upper() or '## SUMMARY' in line.upper():
                    in_excerpt = True
                    continue
                elif in_excerpt and line.startswith('##'):
                    break
                elif in_excerpt and line.strip():
                    excerpt += line.strip() + " "
            
            excerpt = excerpt.strip()[:300] if excerpt else f"{topic} hakkında detaylı bilgiler."
            
            # İçerik (tüm yanıt)
            content = response
            
            # Etiketler bul
            tags = []
            for line in lines:
                if '## ETİKET' in line.upper() or '## TAG' in line.upper():
                    tag_line = lines[lines.index(line) + 1] if lines.index(line) + 1 < len(lines) else ""
                    tags = [t.strip() for t in tag_line.split(',') if t.strip()]
                    break
            
            # SEO metaları üret
            meta_title = title[:60]
            meta_description = excerpt[:160]
            meta_keywords = ', '.join(tags) if tags else topic
            
            return {
                'title': title,
                'excerpt': excerpt,
                'content': content,
                'meta_title': meta_title,
                'meta_description': meta_description,
                'meta_keywords': meta_keywords,
                'suggested_tags': tags[:8]
            }
            
        except Exception as e:
            logger.error(f"❌ Blog parse hatası: {e}")
            return self._get_fallback_blog(topic)
    
    def _parse_seo_response(self, response: str, post) -> Dict:
        """SEO yanıtını parse et"""
        
        try:
            meta_title = post.title[:60]
            meta_description = post.excerpt[:160]
            meta_keywords = ""
            
            lines = response.split('\n')
            
            for line in lines:
                line_upper = line.upper()
                
                if 'META BAŞLIK:' in line_upper or 'META TITLE:' in line_upper:
                    meta_title = line.split(':', 1)[1].strip()[:60]
                
                elif 'META AÇIKLAMA:' in line_upper or 'META DESCRIPTION:' in line_upper:
                    meta_description = line.split(':', 1)[1].strip()[:160]
                
                elif 'ANAHTAR KELİME' in line_upper or 'KEYWORD' in line_upper:
                    meta_keywords = line.split(':', 1)[1].strip()[:200]
            
            return {
                'meta_title': meta_title,
                'meta_description': meta_description,
                'meta_keywords': meta_keywords
            }
            
        except Exception as e:
            logger.error(f"❌ SEO parse hatası: {e}")
            return {
                'meta_title': post.title[:60],
                'meta_description': post.excerpt[:160],
                'meta_keywords': ''
            }
    
    def _get_fallback_blog(self, topic: str) -> Dict:
        """AI başarısız olursa fallback blog"""
        
        return {
            'title': topic,
            'excerpt': f"{topic} hakkında detaylı bilgiler ve yorumlar.",
            'content': f"# {topic}\n\n{topic} hakkında içerik üretilemiyor. Lütfen manuel olarak yazın.",
            'meta_title': topic[:60],
            'meta_description': f"{topic} hakkında detaylı bilgiler.",
            'meta_keywords': topic,
            'suggested_tags': ['tarot', 'astroloji', 'falcılık']
        }
