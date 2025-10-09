import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class SiteSettings(models.Model):
    """Site ayarları modeli - Singleton pattern"""
    # Genel Ayarlar
    site_title = models.CharField(max_length=200, default="Tarot Yorum", verbose_name="Site Başlığı")
    site_description = models.TextField(default="AI destekli tarot falı platformu", verbose_name="Site Açıklaması")
    site_keywords = models.CharField(max_length=500, default="tarot, fal, astroloji, ai", verbose_name="SEO Anahtar Kelimeleri")
    
    # AI Servis Ayarları
    default_ai_provider = models.CharField(
        max_length=20,
        choices=[('openai', 'AstroTarot AI (Primary)'), ('gemini', 'AstroTarot AI (Alternative)')],
        default='gemini',
        verbose_name="Varsayılan AI Motoru"
    )
    
    # OpenAI Ayarları (Primary Engine)
    openai_api_key = models.CharField(max_length=200, blank=True, verbose_name="AstroTarot AI API Anahtarı (Primary)")
    openai_model = models.CharField(
        max_length=50,
        choices=[
            ('o1', 'Expert Model (En Akıllı)'),
            ('o1-mini', 'Expert Mini (Hızlı Reasoning)'),
            ('gpt-4o', 'Advanced Model (Güçlü - Multimodal)'),
            ('gpt-4o-mini', 'Standard Model (Hızlı ve Uygun) ✅'),
            ('gpt-4-turbo', 'Advanced Turbo (Güçlü)'),
            ('gpt-4', 'Advanced (Standart)'),
            ('gpt-3.5-turbo', 'Basic (Ekonomik)'),
        ],
        default='gpt-4o-mini',
        verbose_name="AstroTarot AI Model (Primary)"
    )
    
    # Gemini Ayarları (Alternative Engine)
    gemini_api_key = models.CharField(max_length=200, blank=True, verbose_name="AstroTarot AI API Anahtarı (Alternative)")
    gemini_model = models.CharField(
        max_length=50,
        choices=[
            ('gemini-2.0-flash-exp', 'Alternative v2.0 Flash (Deneysel - En Hızlı)'),
            ('gemini-1.5-pro-latest', 'Alternative v1.5 Pro (En Güçlü)'),
            ('gemini-1.5-flash-latest', 'Alternative v1.5 Flash (Hızlı ve Dengeli)'),
            ('gemini-pro', 'Alternative Pro (Standart)'),
        ],
        default='gemini-1.5-flash-latest',
        verbose_name="AstroTarot AI Model (Alternative)"
    )
    ai_response_max_length = models.IntegerField(
        default=1000, 
        validators=[MinValueValidator(100), MaxValueValidator(5000)],
        verbose_name="AI Yanıt Maksimum Uzunluk"
    )
    
    # Kullanıcı Limitleri
    daily_reading_limit = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(50)],
        verbose_name="Günlük Okuma Limiti"
    )
    max_question_length = models.IntegerField(
        default=500,
        validators=[MinValueValidator(50), MaxValueValidator(2000)],
        verbose_name="Maksimum Soru Uzunluğu"
    )
    
    # Site Durumu
    maintenance_mode = models.BooleanField(default=False, verbose_name="Bakım Modu")
    maintenance_message = models.TextField(
        default="Site bakımda, lütfen daha sonra tekrar deneyin.",
        verbose_name="Bakım Mesajı"
    )
    allow_registration = models.BooleanField(default=True, verbose_name="Kayıt Olma İzni")
    allow_guest_reading = models.BooleanField(default=False, verbose_name="Misafir Okuma İzni")
    
    # İletişim Bilgileri
    contact_email = models.EmailField(blank=True, verbose_name="İletişim E-postası")
    support_phone = models.CharField(max_length=20, blank=True, verbose_name="Destek Telefonu")
    
    # Sosyal Medya
    facebook_url = models.URLField(blank=True, verbose_name="Facebook URL")
    twitter_url = models.URLField(blank=True, verbose_name="Twitter URL")
    instagram_url = models.URLField(blank=True, verbose_name="Instagram URL")
    
    # Cache Ayarları
    cache_timeout = models.IntegerField(
        default=3600,
        validators=[MinValueValidator(60), MaxValueValidator(86400)],
        verbose_name="Cache Süresi (saniye)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Site Ayarları"
        verbose_name_plural = "Site Ayarları"
    
    def __str__(self):
        return "Site Ayarları"
    
    def save(self, *args, **kwargs):
        # Singleton pattern - sadece bir ayar kaydı olabilir
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Singleton - silinmesine izin verme
        pass
    
    @classmethod
    def load(cls):
        """Site ayarlarını yükle, yoksa varsayılan oluştur"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class AIProvider(models.Model):
    """AI Sağlayıcı ayarları"""
    name = models.CharField(max_length=50, unique=True, verbose_name="Sağlayıcı Adı")
    display_name = models.CharField(max_length=100, verbose_name="Görünen Adı")
    api_key = models.CharField(max_length=200, blank=True, verbose_name="API Anahtarı")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    max_tokens = models.IntegerField(default=1000, verbose_name="Maksimum Token")
    temperature = models.FloatField(
        default=0.7,
        validators=[MinValueValidator(0.0), MaxValueValidator(2.0)],
        verbose_name="Yaratıcılık Seviyesi"
    )
    system_prompt = models.TextField(
        default="Sen uzman bir tarot yorumcususun. Kartların anlamlarını detaylı ve anlayışlı bir şekilde açıkla.",
        verbose_name="Sistem Mesajı"
    )
    
    class Meta:
        verbose_name = "AI Sağlayıcı"
        verbose_name_plural = "AI Sağlayıcıları"
    
    def __str__(self):
        return self.display_name

class TarotCard(models.Model):
    """Tarot kartı modeli"""
    name = models.CharField(max_length=100, verbose_name="Kart Adı")
    name_en = models.CharField(max_length=100, verbose_name="İngilizce Adı")
    suit = models.CharField(
        max_length=20,
        choices=[
            ('major', 'Major Arcana'),
            ('cups', 'Cups (Kupa)'), 
            ('pentacles', 'Pentacles (Tılsım)'),
            ('swords', 'Swords (Kılıç)'),
            ('wands', 'Wands (Değnek)')
        ],
        verbose_name="Takım"
    )
    number = models.IntegerField(null=True, blank=True, verbose_name="Numara")
    upright_meaning = models.TextField(verbose_name="Düz Anlam")
    reversed_meaning = models.TextField(verbose_name="Ters Anlam")
    description = models.TextField(verbose_name="Açıklama")
    image_url = models.URLField(blank=True, verbose_name="Görsel URL")
    
    class Meta:
        verbose_name = "Tarot Kartı"
        verbose_name_plural = "Tarot Kartları"
        unique_together = ['suit', 'number']
        
    def __str__(self):
        return self.name


class TarotSpread(models.Model):
    """Tarot yayılım modeli"""
    name = models.CharField(max_length=100, verbose_name="Yayılım Adı")
    slug = models.SlugField(unique=True, verbose_name="URL")
    description = models.TextField(verbose_name="Açıklama")
    card_count = models.IntegerField(verbose_name="Kart Sayısı")
    positions = models.JSONField(
        verbose_name="Pozisyon Anlamları",
        help_text="Her pozisyonun anlamını içeren JSON"
    )
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Başlangıç'),
            ('intermediate', 'Orta'),
            ('advanced', 'İleri')
        ],
        default='beginner',
        verbose_name="Zorluk Seviyesi"
    )
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Tarot Yayılımı"
        verbose_name_plural = "Tarot Yayılımları"
        
    def __str__(self):
        return self.name


class TarotReading(models.Model):
    """Tarot okuma modeli"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Kullanıcı")
    spread = models.ForeignKey(TarotSpread, on_delete=models.CASCADE, verbose_name="Yayılım")
    question = models.TextField(verbose_name="Soru")
    cards = models.JSONField(verbose_name="Çekilen Kartlar")
    interpretation = models.TextField(verbose_name="Yorum")
    ai_provider = models.CharField(
        max_length=20,
        choices=[('openai', 'OpenAI'), ('gemini', 'Google Gemini')],
        verbose_name="AI Sağlayıcı"
    )
    is_public = models.BooleanField(default=False, verbose_name="Herkese Açık")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Tarot Okuma"
        verbose_name_plural = "Tarot Okumaları"
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.username} - {self.spread.name} - {self.created_at.strftime('%d/%m/%Y')}"


class DailyCard(models.Model):
    """Günlük kart modeli"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Kullanıcı")
    card = models.ForeignKey(TarotCard, on_delete=models.CASCADE, verbose_name="Kart")
    date = models.DateField(verbose_name="Tarih")
    is_reversed = models.BooleanField(default=False, verbose_name="Ters Çekildi")
    interpretation = models.TextField(verbose_name="Günlük Yorum")
    ai_provider = models.CharField(
        max_length=20,
        choices=[('openai', 'OpenAI'), ('gemini', 'Google Gemini')],
        verbose_name="AI Sağlayıcı"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Günlük Kart"
        verbose_name_plural = "Günlük Kartlar"
        unique_together = ['user', 'date']
        
    def __str__(self):
        return f"{self.user.username} - {self.card.name} - {self.date}"
