from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.conf.urls.static import static
from django.utils import translation

translation.activate('fa')

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # language switching
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
)

urlpatterns += [
    path('api/v1/auth/', include('authentication.urls')),
    path('api/v1/profiles/', include('profiles.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
