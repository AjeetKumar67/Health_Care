from django.urls import path
from . import views

app_name = 'lab'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.lab_dashboard, name='dashboard'),
    
    # Test Requests
    path('requests/', views.test_request_list, name='test_request_list'),
    path('requests/create/', views.test_request_create, name='test_request_create'),
    path('requests/<str:request_id>/', views.test_request_detail, name='test_request_detail'),
    path('requests/<str:request_id>/collect-sample/', views.collect_sample, name='collect_sample'),
    path('requests/<str:request_id>/enter-result/', views.enter_test_result, name='enter_test_result'),
    path('requests/<str:request_id>/update-status/', views.update_test_status, name='update_test_status'),
    
    # Lab Tests
    path('tests/', views.lab_test_list, name='lab_test_list'),
    path('tests/create/', views.lab_test_create, name='lab_test_create'),
    path('tests/<int:pk>/edit/', views.lab_test_edit, name='lab_test_edit'),
    
    # Test Categories
    path('categories/', views.test_category_list, name='test_category_list'),
    path('categories/create/', views.test_category_create, name='test_category_create'),
    path('categories/<int:pk>/edit/', views.test_category_edit, name='test_category_edit'),
]
