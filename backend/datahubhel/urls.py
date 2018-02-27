from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('service.urls')),
    path('api/', include('gatekeeper.urls')),
    path('mqttauth/', include('mqttauth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
