from django.db import models
from django.utils import timezone


class LegalDocument(models.Model):
    """Yasal Belgeler (Kullanım Koşulları, Gizlilik Politikası vb.)"""
    DOCUMENT_TYPES = [
        ('terms', 'Kullanım Koşulları'),
        ('privacy', 'Gizlilik Politikası'),
        ('cookies', 'Çerez Politikası'),
        ('kvkk', 'KVKK Aydınlatma Metni'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Başlık")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL Slug")
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPES,
        unique=True,
        verbose_name="Belge Tipi"
    )
    content = models.TextField(verbose_name="İçerik")
    version = models.CharField(max_length=20, default="1.0", verbose_name="Versiyon")
    effective_date = models.DateField(default=timezone.now, verbose_name="Yürürlük Tarihi")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Son Güncelleme")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    
    class Meta:
        verbose_name = "Yasal Belge"
        verbose_name_plural = "Yasal Belgeler"
        ordering = ['-last_updated']
    
    def __str__(self):
        return f"{self.get_document_type_display()} (v{self.version})"


class UserConsent(models.Model):
    """Kullanıcı Onayları (KVKK uyumluluğu için)"""
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, verbose_name="Kullanıcı")
    document = models.ForeignKey(LegalDocument, on_delete=models.CASCADE, verbose_name="Belge")
    document_version = models.CharField(max_length=20, verbose_name="Belge Versiyonu")
    consent_given = models.BooleanField(default=True, verbose_name="Onay Verildi")
    consent_date = models.DateTimeField(auto_now_add=True, verbose_name="Onay Tarihi")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP Adresi")
    user_agent = models.CharField(max_length=500, blank=True, verbose_name="User Agent")
    
    class Meta:
        verbose_name = "Kullanıcı Onayı"
        verbose_name_plural = "Kullanıcı Onayları"
        ordering = ['-consent_date']
        unique_together = ['user', 'document']
    
    def __str__(self):
        return f"{self.user.username} - {self.document.get_document_type_display()} - {self.consent_date.date()}"


class DataDeletionRequest(models.Model):
    """Veri Silme Talepleri (KVKK Madde 7)"""
    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('processing', 'İşleniyor'),
        ('completed', 'Tamamlandı'),
        ('rejected', 'Reddedildi'),
    ]
    
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, verbose_name="Kullanıcı")
    request_date = models.DateTimeField(auto_now_add=True, verbose_name="Talep Tarihi")
    reason = models.TextField(blank=True, verbose_name="Sebep")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Durum"
    )
    processed_date = models.DateTimeField(null=True, blank=True, verbose_name="İşlenme Tarihi")
    processed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_deletions',
        verbose_name="İşleyen Yetkili"
    )
    admin_notes = models.TextField(blank=True, verbose_name="Yönetici Notları")
    
    class Meta:
        verbose_name = "Veri Silme Talebi"
        verbose_name_plural = "Veri Silme Talepleri"
        ordering = ['-request_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_status_display()} - {self.request_date.date()}"


class ContactMessage(models.Model):
    """İletişim Mesajları"""
    name = models.CharField(max_length=100, verbose_name="Ad Soyad")
    email = models.EmailField(verbose_name="E-posta")
    subject = models.CharField(max_length=200, verbose_name="Konu")
    message = models.TextField(verbose_name="Mesaj")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Gönderim Tarihi")
    is_read = models.BooleanField(default=False, verbose_name="Okundu")
    is_replied = models.BooleanField(default=False, verbose_name="Yanıtlandı")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP Adresi")
    
    class Meta:
        verbose_name = "İletişim Mesajı"
        verbose_name_plural = "İletişim Mesajları"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject} ({self.created_at.date()})"
