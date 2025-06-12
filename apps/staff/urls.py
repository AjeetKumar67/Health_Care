from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.staff_dashboard, name='dashboard'),
    
    # Staff Management
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/add/', views.staff_create, name='staff_create'),
    path('staff/<int:pk>/', views.staff_detail, name='staff_detail'),
    path('staff/<int:pk>/edit/', views.staff_edit, name='staff_edit'),
    
    # Doctor Management
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('doctors/add/', views.doctor_create, name='doctor_create'),
    path('doctors/<int:pk>/', views.doctor_detail, name='doctor_detail'),
    
    # Department Management
    path('departments/', views.department_list, name='department_list'),
    path('departments/add/', views.department_create, name='department_create'),
    path('departments/<int:pk>/edit/', views.department_edit, name='department_edit'),
    
    # Schedule Management
    path('staff/<int:staff_id>/schedule/add/', views.schedule_create, name='schedule_create'),
]
