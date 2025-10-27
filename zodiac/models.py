from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class ZodiacSign(models.Model):
    """Burç bilgileri"""
    name = models.CharField(max_length=50, unique=True, verbose_name="Burç Adı")
    name_en = models.CharField(max_length=50, unique=True, verbose_name="İngilizce Adı")
    slug = models.SlugField(max_length=50, unique=True, default='default', verbose_name="Slug")
    symbol = models.CharField(max_length=10, verbose_name="Sembol")
    element = models.CharField(
        max_length=20,
        choices=[
            ('fire', 'Ateş'),
            ('earth', 'Toprak'),
            ('air', 'Hava'),
            ('water', 'Su')
        ],
        verbose_name="Element"
    )
    quality = models.CharField(
        max_length=20,
        choices=[
            ('cardinal', 'Öncü'),
            ('fixed', 'Sabit'),
            ('mutable', 'Değişken')
        ],
        verbose_name="Nitelik"
    )
    ruling_planet = models.CharField(max_length=50, verbose_name="Yöneten Gezegen")
    date_range = models.CharField(max_length=50, verbose_name="Tarih Aralığı")
    start_month = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        verbose_name="Başlangıç Ayı"
    )
    start_day = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        verbose_name="Başlangıç Günü"
    )
    end_month = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        verbose_name="Bitiş Ayı"
    )
    end_day = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        verbose_name="Bitiş Günü"
    )
    description = models.TextField(verbose_name="Genel Açıklama")
    traits = models.TextField(verbose_name="Karakteristik Özellikleri")
    strengths = models.TextField(verbose_name="Güçlü Yönleri")
    weaknesses = models.TextField(verbose_name="Zayıf Yönleri")
    compatibility = models.TextField(verbose_name="Uyumlu Burçlar")
    lucky_numbers = models.CharField(max_length=100, verbose_name="Şanslı Sayılar")
    lucky_colors = models.CharField(max_length=100, verbose_name="Şanslı Renkler")
    lucky_day = models.CharField(max_length=20, verbose_name="Şanslı Gün")
    image_url = models.URLField(blank=True, verbose_name="Görsel URL")
    order = models.IntegerField(default=0, verbose_name="Sıralama")
    
    # Token maliyeti ayarları
    token_cost = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Jeton Maliyeti",
        help_text="Bu burçtan detaylı analiz almak için gereken jeton sayısı. 0 = Ücretsiz"
    )
    is_premium_only = models.BooleanField(
        default=False,
        verbose_name="Sadece Premium Üyeler",
        help_text="Bu burç analizi sadece premium üyelere açık mı?"
    )
    
    class Meta:
        verbose_name = "Burç"
        verbose_name_plural = "Burçlar"
        ordering = ['order']
    
    def __str__(self):
        return self.name
    
    @classmethod
    def get_sign_by_date(cls, month, day):
        """Doğum tarihine göre burç belirle"""
        for sign in cls.objects.all():
            if sign.start_month == sign.end_month:
                # Aynı ay içinde
                if month == sign.start_month and sign.start_day <= day <= sign.end_day:
                    return sign
            elif sign.start_month < sign.end_month:
                # Normal durum (örn: Mart 21 - Nisan 19)
                if (month == sign.start_month and day >= sign.start_day) or \
                   (month == sign.end_month and day <= sign.end_day) or \
                   (sign.start_month < month < sign.end_month):
                    return sign
            else:
                # Yıl geçişi olan burçlar (örn: Aralık 22 - Ocak 19)
                if (month == sign.start_month and day >= sign.start_day) or \
                   (month == sign.end_month and day <= sign.end_day) or \
                   (month > sign.start_month or month < sign.end_month):
                    return sign
        return None


class DailyHoroscope(models.Model):
    """Günlük burç yorumu"""
    zodiac_sign = models.ForeignKey(ZodiacSign, on_delete=models.CASCADE, verbose_name="Burç")
    date = models.DateField(verbose_name="Tarih")
    general = models.TextField(verbose_name="Genel Yorum")
    love = models.TextField(verbose_name="Aşk Hayatı")
    career = models.TextField(verbose_name="Kariyer")
    health = models.TextField(verbose_name="Sağlık")
    money = models.TextField(verbose_name="Finans")
    mood_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        default=5,
        verbose_name="Ruh Hali Skoru"
    )
    lucky_number = models.IntegerField(verbose_name="Günün Şanslı Sayısı")
    lucky_color = models.CharField(max_length=50, verbose_name="Günün Şanslı Rengi")
    ai_provider = models.CharField(
        max_length=20,
        choices=[('openai', 'OpenAI'), ('gemini', 'Google Gemini')],
        default='gemini',
        verbose_name="AI Sağlayıcı"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Günlük Burç Yorumu"
        verbose_name_plural = "Günlük Burç Yorumları"
        unique_together = ['zodiac_sign', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.zodiac_sign.name} - {self.date}"


class WeeklyHoroscope(models.Model):
    """Haftalık burç yorumu"""
    zodiac_sign = models.ForeignKey(ZodiacSign, on_delete=models.CASCADE, verbose_name="Burç")
    week_start = models.DateField(verbose_name="Hafta Başlangıcı")
    week_end = models.DateField(verbose_name="Hafta Bitişi")
    general = models.TextField(verbose_name="Genel Yorum")
    love = models.TextField(verbose_name="Aşk Hayatı")
    career = models.TextField(verbose_name="Kariyer")
    health = models.TextField(verbose_name="Sağlık")
    money = models.TextField(verbose_name="Finans")
    advice = models.TextField(verbose_name="Haftalık Tavsiye")
    ai_provider = models.CharField(
        max_length=20,
        choices=[('openai', 'OpenAI'), ('gemini', 'Google Gemini')],
        default='gemini',
        verbose_name="AI Sağlayıcı"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Haftalık Burç Yorumu"
        verbose_name_plural = "Haftalık Burç Yorumları"
        unique_together = ['zodiac_sign', 'week_start']
        ordering = ['-week_start']
    
    def __str__(self):
        return f"{self.zodiac_sign.name} - {self.week_start} / {self.week_end}"


class MonthlyHoroscope(models.Model):
    """Aylık burç yorumu"""
    zodiac_sign = models.ForeignKey(ZodiacSign, on_delete=models.CASCADE, verbose_name="Burç")
    month = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        verbose_name="Ay"
    )
    year = models.IntegerField(verbose_name="Yıl")
    general = models.TextField(verbose_name="Genel Yorum")
    love = models.TextField(verbose_name="Aşk Hayatı")
    career = models.TextField(verbose_name="Kariyer")
    health = models.TextField(verbose_name="Sağlık")
    money = models.TextField(verbose_name="Finans")
    opportunities = models.TextField(verbose_name="Fırsatlar")
    challenges = models.TextField(verbose_name="Zorluklar")
    ai_provider = models.CharField(
        max_length=20,
        choices=[('openai', 'OpenAI'), ('gemini', 'Google Gemini')],
        default='gemini',
        verbose_name="AI Sağlayıcı"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Aylık Burç Yorumu"
        verbose_name_plural = "Aylık Burç Yorumları"
        unique_together = ['zodiac_sign', 'month', 'year']
        ordering = ['-year', '-month']
    
    def __str__(self):
        return f"{self.zodiac_sign.name} - {self.month}/{self.year}"


class CompatibilityReading(models.Model):
    """Burç uyumu analizi"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Kullanıcı")
    sign1 = models.ForeignKey(
        ZodiacSign, 
        on_delete=models.CASCADE, 
        related_name='compatibility_sign1',
        verbose_name="İlk Burç"
    )
    sign2 = models.ForeignKey(
        ZodiacSign, 
        on_delete=models.CASCADE, 
        related_name='compatibility_sign2',
        verbose_name="İkinci Burç"
    )
    compatibility_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Uyum Skoru"
    )
    love_compatibility = models.TextField(verbose_name="Aşk Uyumu")
    friendship_compatibility = models.TextField(verbose_name="Arkadaşlık Uyumu")
    work_compatibility = models.TextField(verbose_name="İş Uyumu")
    challenges = models.TextField(verbose_name="Olası Zorluklar")
    advice = models.TextField(verbose_name="Tavsiyeler")
    ai_provider = models.CharField(
        max_length=20,
        choices=[('openai', 'OpenAI'), ('gemini', 'Google Gemini')],
        default='gemini',
        verbose_name="AI Sağlayıcı"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Burç Uyumu Analizi"
        verbose_name_plural = "Burç Uyumu Analizleri"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sign1.name} - {self.sign2.name} Uyumu"


class BirthChart(models.Model):
    """Doğum haritası"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Kullanıcı")
    name = models.CharField(max_length=100, verbose_name="İsim")
    birth_date = models.DateField(verbose_name="Doğum Tarihi")
    birth_time = models.TimeField(verbose_name="Doğum Saati")
    birth_place = models.CharField(max_length=200, verbose_name="Doğum Yeri")
    latitude = models.FloatField(verbose_name="Enlem")
    longitude = models.FloatField(verbose_name="Boylam")
    
    # Ana Burç Bilgileri
    sun_sign = models.ForeignKey(
        ZodiacSign, 
        on_delete=models.CASCADE,
        related_name='birth_chart_sun',
        verbose_name="Güneş Burcu"
    )
    moon_sign = models.ForeignKey(
        ZodiacSign, 
        on_delete=models.CASCADE,
        related_name='birth_chart_moon',
        verbose_name="Ay Burcu"
    )
    rising_sign = models.ForeignKey(
        ZodiacSign, 
        on_delete=models.CASCADE,
        related_name='birth_chart_rising',
        verbose_name="Yükselen Burç"
    )
    
    # Detaylı Analiz
    personality_analysis = models.TextField(verbose_name="Kişilik Analizi")
    emotional_analysis = models.TextField(verbose_name="Duygusal Analiz")
    career_analysis = models.TextField(verbose_name="Kariyer Analizi")
    relationship_analysis = models.TextField(verbose_name="İlişki Analizi")
    life_path_analysis = models.TextField(verbose_name="Yaşam Yolu Analizi")
    
    # Gezegen Pozisyonları (JSON olarak saklayabiliriz)
    planet_positions = models.JSONField(default=dict, verbose_name="Gezegen Pozisyonları")
    house_positions = models.JSONField(default=dict, verbose_name="Ev Pozisyonları")
    aspects = models.JSONField(default=dict, verbose_name="Açılar (Aspects)")
    
    ai_provider = models.CharField(
        max_length=20,
        choices=[('openai', 'OpenAI'), ('gemini', 'Google Gemini')],
        default='gemini',
        verbose_name="AI Sağlayıcı"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Doğum Haritası"
        verbose_name_plural = "Doğum Haritaları"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.birth_date}"


class MoonSign(models.Model):
    """Ay Burcu Hesaplaması"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Kullanıcı")
    birth_date = models.DateField(verbose_name="Doğum Tarihi")
    birth_time = models.TimeField(verbose_name="Doğum Saati")
    birth_place = models.CharField(max_length=200, verbose_name="Doğum Yeri")
    latitude = models.FloatField(verbose_name="Enlem")
    longitude = models.FloatField(verbose_name="Boylam")
    moon_sign = models.ForeignKey(ZodiacSign, on_delete=models.CASCADE, related_name='moon_signs', verbose_name="Ay Burcu")
    interpretation = models.TextField(verbose_name="Yorum")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma")
    
    class Meta:
        verbose_name = "Ay Burcu"
        verbose_name_plural = "Ay Burçları"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - Ay Burcu: {self.moon_sign.name}"


class Ascendant(models.Model):
    """Yükselen Burç Hesaplaması"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Kullanıcı")
    birth_date = models.DateField(verbose_name="Doğum Tarihi")
    birth_time = models.TimeField(verbose_name="Doğum Saati")
    birth_place = models.CharField(max_length=200, verbose_name="Doğum Yeri")
    latitude = models.FloatField(verbose_name="Enlem")
    longitude = models.FloatField(verbose_name="Boylam")
    ascendant_sign = models.ForeignKey(ZodiacSign, on_delete=models.CASCADE, related_name='ascendants', verbose_name="Yükselen Burç")
    interpretation = models.TextField(verbose_name="Yorum")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma")
    
    class Meta:
        verbose_name = "Yükselen Burç"
        verbose_name_plural = "Yükselen Burçlar"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - Yükselen: {self.ascendant_sign.name}"


class PersonalHoroscope(models.Model):
    """Kişisel Burç Profili (Güneş + Ay + Yükselen)"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Kullanıcı")
    sun_sign = models.ForeignKey(ZodiacSign, on_delete=models.CASCADE, related_name='sun_signs', verbose_name="Güneş Burcu")
    moon_sign = models.ForeignKey(ZodiacSign, on_delete=models.CASCADE, related_name='personal_moon_signs', null=True, blank=True, verbose_name="Ay Burcu")
    ascendant_sign = models.ForeignKey(ZodiacSign, on_delete=models.CASCADE, related_name='personal_ascendants', null=True, blank=True, verbose_name="Yükselen Burç")
    birth_date = models.DateField(verbose_name="Doğum Tarihi")
    birth_time = models.TimeField(null=True, blank=True, verbose_name="Doğum Saati")
    birth_place = models.CharField(max_length=200, blank=True, verbose_name="Doğum Yeri")
    interpretation = models.TextField(blank=True, verbose_name="Genel Yorum")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme")
    
    class Meta:
        verbose_name = "Kişisel Burç Profili"
        verbose_name_plural = "Kişisel Burç Profilleri"
    
    def __str__(self):
        result = f"{self.user.username} - {self.sun_sign.name}"
        if self.moon_sign:
            result += f" / Ay: {self.moon_sign.name}"
        if self.ascendant_sign:
            result += f" / Yükselen: {self.ascendant_sign.name}"
        return result


class UserDailyHoroscope(models.Model):
    """Kullanıcıya Özel Günlük Burç Yorumu"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Kullanıcı")
    zodiac_sign = models.ForeignKey(ZodiacSign, on_delete=models.CASCADE, verbose_name="Burç")
    date = models.DateField(verbose_name="Tarih")
    general = models.TextField(verbose_name="Genel Yorum")
    love = models.TextField(verbose_name="Aşk Hayatı")
    career = models.TextField(verbose_name="Kariyer")
    health = models.TextField(verbose_name="Sağlık")
    money = models.TextField(verbose_name="Finans")
    mood_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        default=5,
        verbose_name="Ruh Hali Skoru"
    )
    lucky_number = models.IntegerField(verbose_name="Günün Şanslı Sayısı")
    lucky_color = models.CharField(max_length=50, verbose_name="Günün Şanslı Rengi")
    ai_provider = models.CharField(
        max_length=20,
        choices=[('openai', 'OpenAI'), ('gemini', 'Google Gemini')],
        default='openai',
        verbose_name="AI Sağlayıcı"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Kullanıcı Günlük Burç Yorumu"
        verbose_name_plural = "Kullanıcı Günlük Burç Yorumları"
        unique_together = ['user', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.username} - {self.zodiac_sign.name} - {self.date}"


class UserWeeklyHoroscope(models.Model):
    """Kullanıcıya Özel Haftalık Burç Yorumu"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Kullanıcı")
    zodiac_sign = models.ForeignKey(ZodiacSign, on_delete=models.CASCADE, verbose_name="Burç")
    week_start = models.DateField(verbose_name="Hafta Başlangıcı")
    week_end = models.DateField(verbose_name="Hafta Bitişi")
    general = models.TextField(verbose_name="Genel Yorum")
    love = models.TextField(verbose_name="Aşk Hayatı")
    career = models.TextField(verbose_name="Kariyer")
    health = models.TextField(verbose_name="Sağlık")
    money = models.TextField(verbose_name="Finans")
    advice = models.TextField(verbose_name="Haftalık Tavsiye")
    ai_provider = models.CharField(
        max_length=20,
        choices=[('openai', 'OpenAI'), ('gemini', 'Google Gemini')],
        default='openai',
        verbose_name="AI Sağlayıcı"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Kullanıcı Haftalık Burç Yorumu"
        verbose_name_plural = "Kullanıcı Haftalık Burç Yorumları"
        unique_together = ['user', 'week_start']
        ordering = ['-week_start']
    
    def __str__(self):
        return f"{self.user.username} - {self.zodiac_sign.name} - {self.week_start}"


class UserMonthlyHoroscope(models.Model):
    """Kullanıcıya Özel Aylık Burç Yorumu"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Kullanıcı")
    zodiac_sign = models.ForeignKey(ZodiacSign, on_delete=models.CASCADE, verbose_name="Burç")
    month = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        verbose_name="Ay"
    )
    year = models.IntegerField(verbose_name="Yıl")
    general = models.TextField(verbose_name="Genel Yorum")
    love = models.TextField(verbose_name="Aşk Hayatı")
    career = models.TextField(verbose_name="Kariyer")
    health = models.TextField(verbose_name="Sağlık")
    money = models.TextField(verbose_name="Finans")
    opportunities = models.TextField(verbose_name="Fırsatlar")
    challenges = models.TextField(verbose_name="Zorluklar")
    ai_provider = models.CharField(
        max_length=20,
        choices=[('openai', 'OpenAI'), ('gemini', 'Google Gemini')],
        default='openai',
        verbose_name="AI Sağlayıcı"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Kullanıcı Aylık Burç Yorumu"
        verbose_name_plural = "Kullanıcı Aylık Burç Yorumları"
        unique_together = ['user', 'year', 'month']
        ordering = ['-year', '-month']
    
    def __str__(self):
        return f"{self.user.username} - {self.zodiac_sign.name} - {self.month}/{self.year}"
