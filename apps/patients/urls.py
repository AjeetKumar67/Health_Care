from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    # Patient views
    path('dashboard/', views.patient_dashboard, name='dashboard'),
    path('list/', views.patient_list, name='patient_list'),
    path('create/', views.patient_create, name='patient_create'),
    path('<str:patient_id>/', views.patient_detail, name='patient_detail'),
    path('<str:patient_id>/edit/', views.patient_edit, name='patient_edit'),
    
    # Medical records
    path('<str:patient_id>/medical-records/', views.medical_records, name='medical_records'),
    path('<str:patient_id>/medical-record/create/', views.medical_record_create, name='medical_record_create'),
    
    # Documents
    path('<str:patient_id>/document/upload/', views.document_upload, name='document_upload'),
]
