from django.urls import path
from . import views

app_name = 'emergency'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.emergency_dashboard, name='dashboard'),
    
    # Emergency Cases
    path('cases/', views.case_list, name='case_list'),
    path('cases/create/', views.case_create, name='case_create'),
    path('cases/<int:pk>/', views.case_detail, name='case_detail'),
    path('cases/<int:pk>/edit/', views.case_edit, name='case_edit'),
    
    # Ambulances
    path('ambulances/', views.ambulance_list, name='ambulance_list'),
    path('ambulances/create/', views.ambulance_create, name='ambulance_create'),
    path('ambulances/<int:pk>/edit/', views.ambulance_edit, name='ambulance_edit'),
    
    # Ambulance Calls
    path('ambulance-calls/', views.ambulance_call_list, name='ambulance_call_list'),
    path('ambulance-calls/create/', views.ambulance_call_create, name='ambulance_call_create'),
    path('ambulance-calls/<int:pk>/edit/', views.ambulance_call_edit, name='ambulance_call_edit'),
]
