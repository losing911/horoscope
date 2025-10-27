import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class HeroSection(models.Model):
    """Ana sayfa hero bölümü içerikleri"""
    # Ana Başlık
    title_line1 = models.CharField(max_length=100, default="İçsel Farkındalığınızı", verbose_name="Başlık Satır 1")
    title_line2 = models.CharField(max_length=100, default="Keşfedin", verbose_name="Başlık Satır 2 (Vurgulu)")
    
    # Alt Başlık
    subtitle = models.TextField(
        default="Yapay zeka destekli kişisel gelişim platformu. Duygusal denge, motivasyon ve içsel rehberlik için algoritmalarla desteklenen özel yöntemler.",
        verbose_name="Alt Başlık"
    )
    
    # Duyuru/Bildirim
    show_announcement = models.BooleanField(default=False, verbose_name="Duyuru Göster")
    announcement_text = models.CharField(
        max_length=200, 
        default="Yeni Video Yayınlandı!",
        verbose_name="Duyuru Metni"
    )
    announcement_icon = models.CharField(
        max_length=50,
        default="fas fa-video",
        verbose_name="Duyuru İkonu (Font Awesome)"
    )
    announcement_link = models.URLField(blank=True, verbose_name="Duyuru Linki")
    announcement_color = models.CharField(
        max_length=20,
        default="#FF0000",
        verbose_name="Duyuru Rengi"
    )
    
    # Butonlar
    primary_button_text = models.CharField(max_length=50, default="Rehberliğe Başla", verbose_name="Ana Buton Metni")
    primary_button_url = models.CharField(max_length=200, default="/spreads/", verbose_name="Ana Buton URL")
    
    secondary_button_text = models.CharField(max_length=50, default="Günlük İlham", verbose_name="İkinci Buton Metni")
    secondary_button_url = models.CharField(max_length=200, default="/daily-card/", verbose_name="İkinci Buton URL")
    
    # Görsel Ayarları
    background_gradient_start = models.CharField(max_length=20, default="#6B1B3D", verbose_name="Arka Plan Başlangıç Rengi")
    background_gradient_end = models.CharField(max_length=20, default="#4A0E2A", verbose_name="Arka Plan Bitiş Rengi")
    
    # YouTube Video
    show_video = models.BooleanField(default=False, verbose_name="Video Göster")
    video_url = models.URLField(
        blank=True, 
        verbose_name="YouTube Video URL",
        help_text="Örnek: https://www.youtube.com/watch?v=VIDEO_ID veya https://youtu.be/VIDEO_ID"
    )
    video_title = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name="Video Başlığı",
        help_text="Video için özel başlık (opsiyonel)"
    )
    
    # Aktiflik
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Hero Bölümü"
        verbose_name_plural = "Hero Bölümü"
        ordering = ['-is_active', '-updated_at']
    
    def __str__(self):
        return f"Hero Section - {self.title_line1}"
    
    def get_video_id(self):
        """YouTube URL'den video ID'sini çıkar"""
        if not self.video_url:
            return None
        
        import re
        # YouTube URL formatları:
        # https://www.youtube.com/watch?v=VIDEO_ID
        # https://youtu.be/VIDEO_ID
        # https://www.youtube.com/embed/VIDEO_ID
        # https://www.youtube.com/shorts/VIDEO_ID
        # https://m.youtube.com/watch?v=VIDEO_ID
        
        patterns = [
            r'(?:youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})',
            r'(?:youtu\.be\/)([a-zA-Z0-9_-]{11})',
            r'(?:youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'(?:youtube\.com\/shorts\/)([a-zA-Z0-9_-]{11})',
            r'(?:m\.youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})',
            # Video ID'yi direkt algıla (11 karakter)
            r'^([a-zA-Z0-9_-]{11})$',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.video_url)
            if match:
                video_id = match.group(1)
                # Video ID'nin 11 karakter olduğunu doğrula
                if len(video_id) == 11:
                    return video_id
        
        return None
    
    @classmethod
    def get_active(cls):
        """Aktif hero section'ı getir"""
        try:
            return cls.objects.filter(is_active=True).first()
        except cls.DoesNotExist:
            # Yoksa varsayılan oluştur
            return cls.objects.create()


class SiteSettings(models.Model):
    """Site ayarları modeli - Singleton pattern"""
    # Genel Ayarlar
    site_title = models.CharField(max_length=200, default="Tarot Yorum", verbose_name="Site Başlığı")
    site_description = models.TextField(default="AI destekli tarot falı platformu", verbose_name="Site Açıklaması")
    site_keywords = models.CharField(max_length=500, default="tarot, fal, astroloji, ai", verbose_name="SEO Anahtar Kelimeleri")
    
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
        max_length=100,
        default='openrouter',
        verbose_name="AI Sağlayıcı",
        help_text="Artık OpenRouter kullanılıyor"
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
        max_length=100,
        default='openrouter',
        verbose_name="AI Sağlayıcı",
        help_text="Artık OpenRouter kullanılıyor"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Günlük Kart"
        verbose_name_plural = "Günlük Kartlar"
        unique_together = ['user', 'date']
        
    def __str__(self):
        return f"{self.user.username} - {self.card.name} - {self.date}"
