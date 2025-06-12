from django.urls import path
from . import views

app_name = 'infrastructure'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.infrastructure_dashboard, name='dashboard'),
    
    # Buildings
    path('buildings/', views.building_list, name='building_list'),
    path('buildings/add/', views.building_create, name='building_create'),
    path('buildings/<int:pk>/', views.building_detail, name='building_detail'),
    path('buildings/<int:pk>/edit/', views.building_edit, name='building_edit'),
    
    # Wards
    path('wards/', views.ward_list, name='ward_list'),
    path('wards/add/', views.ward_create, name='ward_create'),
    path('wards/<int:pk>/', views.ward_detail, name='ward_detail'),
    path('wards/<int:pk>/edit/', views.ward_edit, name='ward_edit'),
    
    # Beds
    path('beds/', views.bed_list, name='bed_list'),
    path('beds/add/', views.bed_create, name='bed_create'),
    path('beds/<int:pk>/edit/', views.bed_edit, name='bed_edit'),
    
    # Equipment
    path('equipment/', views.equipment_list, name='equipment_list'),
    path('equipment/add/', views.equipment_create, name='equipment_create'),
    path('equipment/<int:pk>/', views.equipment_detail, name='equipment_detail'),
    path('equipment/<int:pk>/edit/', views.equipment_edit, name='equipment_edit'),
    
    # Maintenance Records
    path('maintenance/', views.maintenance_list, name='maintenance_list'),
    path('maintenance/add/', views.maintenance_create, name='maintenance_create'),
]
