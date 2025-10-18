from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .legal_models import LegalDocument, UserConsent, DataDeletionRequest, ContactMessage
from .forms import CustomUserCreationForm, UserProfileForm


def legal_document(request, slug):
    """Yasal belge görüntüleme"""
    document = get_object_or_404(LegalDocument, slug=slug, is_active=True)
    return render(request, 'accounts/legal_document.html', {
        'document': document
    })


def terms_of_service(request):
    """Kullanım Koşulları"""
    return legal_document(request, 'kullanim-kosullari')


def privacy_policy(request):
    """Gizlilik Politikası"""
    return legal_document(request, 'gizlilik-politikasi')


def cookie_policy(request):
    """Çerez Politikası"""
    return legal_document(request, 'cerez-politikasi')


def kvkk_clarification(request):
    """KVKK Aydınlatma Metni"""
    return legal_document(request, 'kvkk-aydinlatma')


@login_required
@require_http_methods(["POST"])
def request_data_deletion(request):
    """Veri silme talebi oluşturma (KVKK Madde 7)"""
    reason = request.POST.get('reason', '')
    
    # Mevcut bekleyen talep var mı kontrol et
    existing = DataDeletionRequest.objects.filter(
        user=request.user,
        status__in=['pending', 'processing']
    ).first()
    
    if existing:
        messages.warning(request, 'Zaten bekleyen bir veri silme talebiniz var.')
        return redirect('accounts:profile')
    
    # Yeni talep oluştur
    DataDeletionRequest.objects.create(
        user=request.user,
        reason=reason
    )
    
    messages.success(request, 
        'Veri silme talebiniz alındı. 30 gün içinde işleme alınacaktır. '
        'Talep durumunu profilinizden takip edebilirsiniz.'
    )
    return redirect('accounts:profile')


@login_required
@require_http_methods(["POST"])
def record_consent(request, document_type):
    """Kullanıcı onayını kaydet"""
    try:
        document = LegalDocument.objects.get(
            document_type=document_type,
            is_active=True
        )
        
        # Mevcut onayı güncelle veya yeni oluştur
        consent, created = UserConsent.objects.update_or_create(
            user=request.user,
            document=document,
            defaults={
                'document_version': document.version,
                'consent_given': True,
                'ip_address': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500]
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Onayınız kaydedildi.'
        })
    except LegalDocument.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Belge bulunamadı.'
        }, status=404)


def contact(request):
    """İletişim formu"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, 
            'Mesajınız başarıyla gönderildi. En kısa sürede size dönüş yapacağız.'
        )
        return redirect('accounts:contact')
    
    return render(request, 'accounts/contact.html')
