from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('Auth.urls')),
    path('api/', include('patients.urls')),
    path('api/', include('appointments.urls')),
    path('api/', include('HMS.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
