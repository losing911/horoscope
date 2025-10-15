from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

# Dil değiştirme URL'i (dil seçimi için)
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
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
