from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from zodiac.admin_views import (
    horoscope_images_view,
    generate_horoscope_image,
    generate_all_horoscope_images,
    download_horoscope_image
)
from accounts.legal_views import (
    legal_document,
    terms_of_service,
    privacy_policy,
    cookie_policy,
    kvkk_clarification,
    contact,
    request_data_deletion,
    record_consent
)

# Dil değiştirme URL'i (dil seçimi için) - i18n_patterns DIŞINDA olmali
urlpatterns = [
    path('i18n/setlang/', set_language, name='set_language'),
    path('rosetta/', include('rosetta.urls')),  # Translation interface (admin only)
    # Admin horoscope images
    path('admin/horoscope-images/', horoscope_images_view, name='admin_horoscope_images'),
    path('admin/horoscope-images/generate/<slug:sign_slug>/<str:date_str>/', generate_horoscope_image, name='admin_generate_horoscope_image'),
    path('admin/horoscope-images/generate-all/<str:date_str>/', generate_all_horoscope_images, name='admin_generate_all_horoscope_images'),
    path('admin/horoscope-images/download/<slug:sign_slug>/<str:date_str>/', download_horoscope_image, name='admin:download_horoscope_image'),
    # Legal pages (outside i18n for consistency)
    path('kullanim-kosullari/', terms_of_service, name='terms_of_service'),
    path('gizlilik-politikasi/', privacy_policy, name='privacy_policy'),
    path('cerez-politikasi/', cookie_policy, name='cookie_policy'),
    path('kvkk/', kvkk_clarification, name='kvkk_clarification'),
    path('iletisim/', contact, name='contact'),
    path('legal/<slug:slug>/', legal_document, name='legal_document'),
    # KVKK API endpoints
    path('api/request-deletion/', request_data_deletion, name='request_data_deletion'),
    path('api/record-consent/<str:document_type>/', record_consent, name='record_consent'),
]

# Dil prefix'li URL'ler (tr/, en/, de/, fr/)
urlpatterns += i18n_patterns(
    # Custom admin dashboard URL'leri önce gelmeli
    path('', include('tarot.urls')),
    path('zodiac/', include('zodiac.urls')),
    path('blog/', include('blog.urls')),
    path('shop/', include('shop.urls')),
    path('accounts/', include('accounts.urls')),
    # Django admin paneli
    path('admin/', admin.site.urls),
    prefix_default_language=False,  # /tr/ yerine / kullan (Türkçe için)
)

# Static files for development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
