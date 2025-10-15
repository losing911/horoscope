from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import datetime

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
    daily_reading_limit = models.IntegerField(default=3, verbose_name="Günlük Okuma Limiti")
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
        return self.get_daily_readings_count() < self.daily_reading_limit
