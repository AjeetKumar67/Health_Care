from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('book/', views.book_appointment, name='book_appointment'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('doctor-appointments/', views.doctor_appointments, name='doctor_appointments'),
    path('appointment/<str:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('get-schedule/', views.get_doctor_schedule, name='get_doctor_schedule'),
]
