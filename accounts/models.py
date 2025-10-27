from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import datetime

# Legal models import
from .legal_models import LegalDocument, UserConsent, DataDeletionRequest, ContactMessage
from decimal import Decimal

class User(AbstractUser):
    """Genişletilmiş kullanıcı modeli"""
    birth_date = models.DateField(null=True, blank=True, verbose_name="Doğum Tarihi")
    zodiac_sign = models.ForeignKey(
        'zodiac.ZodiacSign',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Burç"
    )
    preferred_ai_provider = models.CharField(
        max_length=20, 
        choices=[('openai', 'OpenAI'), ('gemini', 'Google Gemini')],
        default='gemini',
        verbose_name="Tercih Edilen AI Sağlayıcı"
    )
    # Jeton Sistemi
    tokens = models.IntegerField(default=10, verbose_name="Jeton Sayısı", help_text="Premium hizmetler için kullanılır")
    is_premium = models.BooleanField(default=False, verbose_name="Premium Üye")
    premium_until = models.DateTimeField(null=True, blank=True, verbose_name="Premium Bitiş Tarihi")
    
    # Limitleme
    daily_reading_limit = models.IntegerField(default=1, verbose_name="Günlük Ücretsiz Okuma Limiti")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Kullanıcı"
        verbose_name_plural = "Kullanıcılar"

    def __str__(self):
        return self.username

    def get_zodiac_sign(self):
        """Doğum tarihine göre burç hesapla"""
        if not self.birth_date:
            return None
            
        month = self.birth_date.month
        day = self.birth_date.day
        
        if (month == 3 and day >= 21) or (month == 4 and day <= 19):
            return "aries"
        elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
            return "taurus"
        elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
            return "gemini"
        elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
            return "cancer"
        elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
            return "leo"
        elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
            return "virgo"
        elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
            return "libra"
        elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
            return "scorpio"
        elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
            return "sagittarius"
        elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
            return "capricorn"
        elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
            return "aquarius"
        elif (month == 2 and day >= 19) or (month == 3 and day <= 20):
            return "pisces"
        
        return None

    def get_daily_readings_count(self):
        """Bugünkü okuma sayısını döndür"""
        from tarot.models import TarotReading
        today = timezone.now().date()
        return TarotReading.objects.filter(
            user=self, 
            created_at__date=today
        ).count()

    def can_read_today(self):
        """Bugün okuma yapabilir mi?"""
        # Premium üyeler sınırsız
        if self.is_premium_active():
            return True
        # Jeton varsa kullanabilir
        if self.tokens > 0:
            return True
        # Ücretsiz limiti kontrol et
        return self.get_daily_readings_count() < self.daily_reading_limit
    
    def is_premium_active(self):
        """Premium üyelik aktif mi?"""
        if not self.is_premium:
            return False
        if not self.premium_until:
            return True  # Sınırsız premium
        return timezone.now() < self.premium_until
    
    def use_token(self, amount=1):
        """Jeton kullan"""
        if self.tokens >= amount:
            self.tokens -= amount
            self.save()
            return True
        return False
    
    def add_tokens(self, amount):
        """Jeton ekle"""
        self.tokens += amount
        self.save()


class TokenPackage(models.Model):
    """Jeton paketleri"""
    name = models.CharField(max_length=100, verbose_name="Paket Adı")
    token_amount = models.IntegerField(verbose_name="Jeton Sayısı")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Fiyat (TL)")
    price_usd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Fiyat (USD)")
    bonus_tokens = models.IntegerField(default=0, verbose_name="Bonus Jeton", help_text="Ekstra verilen jeton")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    display_order = models.IntegerField(default=0, verbose_name="Sıralama")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Jeton Paketi"
        verbose_name_plural = "Jeton Paketleri"
        ordering = ['display_order', 'price']
    
    def __str__(self):
        return f"{self.name} - {self.total_tokens} Jeton"
    
    @property
    def total_tokens(self):
        """Toplam jeton (normal + bonus)"""
        return self.token_amount + self.bonus_tokens
    
    @property
    def per_token_price(self):
        """Jeton başına fiyat"""
        if self.total_tokens > 0:
            return self.price / self.total_tokens
        return Decimal('0')


class TokenTransaction(models.Model):
    """Jeton işlem geçmişi"""
    TRANSACTION_TYPES = [
        ('purchase', 'Satın Alma'),
        ('usage', 'Kullanım'),
        ('bonus', 'Bonus'),
        ('refund', 'İade'),
        ('admin', 'Admin İşlemi'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='token_transactions', verbose_name="Kullanıcı")
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name="İşlem Tipi")
    amount = models.IntegerField(verbose_name="Jeton Miktarı", help_text="Pozitif: ekleme, Negatif: kullanım")
    balance_before = models.IntegerField(verbose_name="Önceki Bakiye")
    balance_after = models.IntegerField(verbose_name="Sonraki Bakiye")
    description = models.TextField(blank=True, verbose_name="Açıklama")
    related_reading = models.ForeignKey(
        'tarot.TarotReading',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="İlgili Okuma"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Jeton İşlemi"
        verbose_name_plural = "Jeton İşlemleri"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_transaction_type_display()} - {self.amount} jeton"
