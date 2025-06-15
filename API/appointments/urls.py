from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'doctors', views.DoctorViewSet)
router.register(r'doctor-availability', views.DoctorAvailabilityViewSet)
router.register(r'appointments', views.AppointmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
