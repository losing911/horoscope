from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.safestring import mark_safe
from .models import User


class CustomUserCreationForm(UserCreationForm):
    """Custom User modeli için kayıt formu"""
    email = forms.EmailField(
        required=True,
        help_text='Gerekli. Geçerli bir e-posta adresi girin.',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    birth_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text='Burç hesaplaması için doğum tarihinizi girebilirsiniz (opsiyonel).'
    )
    
    # KVKK Onayları - Linkli
    terms_accepted = forms.BooleanField(
        required=True,
        label=mark_safe('<a href="/kullanim-kosullari/" target="_blank" class="text-primary">Kullanım Koşulları</a>nı okudum ve kabul ediyorum'),
        error_messages={'required': 'Kullanım koşullarını kabul etmelisiniz.'}
    )
    privacy_accepted = forms.BooleanField(
        required=True,
        label=mark_safe('<a href="/gizlilik-politikasi/" target="_blank" class="text-primary">Gizlilik Politikası</a> ve <a href="/kvkk/" target="_blank" class="text-primary">KVKK Aydınlatma Metni</a>ni okudum ve kabul ediyorum'),
        error_messages={'required': 'Gizlilik politikasını kabul etmelisiniz.'}
    )
    marketing_consent = forms.BooleanField(
        required=False,
        label='E-posta ile bilgilendirme ve kampanya almak istiyorum (opsiyonel)'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'birth_date', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True, request=None):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if self.cleaned_data.get('birth_date'):
            user.birth_date = self.cleaned_data['birth_date']
            # Burcu otomatik hesapla
            from zodiac.models import ZodiacSign
            if user.birth_date:
                zodiac_sign = ZodiacSign.get_sign_by_date(
                    user.birth_date.month, 
                    user.birth_date.day
                )
                if zodiac_sign:
                    user.zodiac_sign = zodiac_sign
        if commit:
            user.save()
            
            # KVKK onaylarını kaydet
            from .legal_models import LegalDocument, UserConsent
            
            # IP ve User-Agent bilgisi
            ip_address = None
            user_agent = None
            if request:
                # IP adresini al (proxy arkasındaysa X-Forwarded-For'dan)
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip_address = x_forwarded_for.split(',')[0].strip()
                else:
                    ip_address = request.META.get('REMOTE_ADDR')
                user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Kullanım Koşulları onayı
            if self.cleaned_data.get('terms_accepted'):
                try:
                    terms_doc = LegalDocument.objects.filter(
                        document_type='terms',
                        is_active=True
                    ).first()
                    if terms_doc:
                        UserConsent.objects.create(
                            user=user,
                            document=terms_doc,
                            document_version=terms_doc.version,
                            consent_given=True,
                            ip_address=ip_address,
                            user_agent=user_agent
                        )
                except Exception:
                    pass
            
            # Gizlilik Politikası onayı
            if self.cleaned_data.get('privacy_accepted'):
                try:
                    privacy_doc = LegalDocument.objects.filter(
                        document_type='privacy',
                        is_active=True
                    ).first()
                    if privacy_doc:
                        UserConsent.objects.create(
                            user=user,
                            document=privacy_doc,
                            document_version=privacy_doc.version,
                            consent_given=True,
                            ip_address=ip_address,
                            user_agent=user_agent
                        )
                    
                    # KVKK belgesi de privacy ile birlikte
                    kvkk_doc = LegalDocument.objects.filter(
                        document_type='kvkk',
                        is_active=True
                    ).first()
                    if kvkk_doc:
                        UserConsent.objects.create(
                            user=user,
                            document=kvkk_doc,
                            document_version=kvkk_doc.version,
                            consent_given=True,
                            ip_address=ip_address,
                            user_agent=user_agent
                        )
                except Exception:
                    pass
            
            # Pazarlama onayı (çerez politikası)
            if self.cleaned_data.get('marketing_consent'):
                try:
                    cookie_doc = LegalDocument.objects.filter(
                        document_type='cookies',
                        is_active=True
                    ).first()
                    if cookie_doc:
                        UserConsent.objects.create(
                            user=user,
                            document=cookie_doc,
                            document_version=cookie_doc.version,
                            consent_given=True,
                            ip_address=ip_address,
                            user_agent=user_agent
                        )
                except Exception:
                    pass
        
        return user


class CustomUserChangeForm(UserChangeForm):
    """Custom User modeli için güncelleme formu"""
    
    class Meta:
        model = User
        fields = ('username', 'email', 'birth_date', 'zodiac_sign', 'preferred_ai_provider')


class UserProfileForm(forms.ModelForm):
    """Kullanıcı profil güncelleme formu"""
    
    class Meta:
        model = User
        fields = ('email', 'birth_date', 'zodiac_sign', 'preferred_ai_provider', 'daily_reading_limit')
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }
