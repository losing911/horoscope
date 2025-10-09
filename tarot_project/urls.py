from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Custom admin dashboard URL'leri önce gelmeli
    path('', include('tarot.urls')),
    path('zodiac/', include('zodiac.urls')),
    path('blog/', include('blog.urls')),
    # Django admin paneli
    path('admin/', admin.site.urls),
]

# Static files for development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
