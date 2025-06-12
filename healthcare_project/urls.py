"""
URL configuration for healthcare_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

def home(request):
    return redirect('users:dashboard')

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('', include('apps.users.urls')),
    path('appointments/', include('apps.appointments.urls')),
    path('pharmacy/', include('apps.pharmacy.urls')),
    path('staff/', include('apps.staff.urls')),
    path('lab/', include('apps.lab.urls')),
    path('inventory/', include('apps.inventory.urls')),
    path('infrastructure/', include('apps.infrastructure.urls')),
    path('billing/', include('apps.billing.urls')),
    path('support/', include('apps.support.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
