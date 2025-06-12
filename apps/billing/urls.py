from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.billing_dashboard, name='dashboard'),
    
    # Invoices
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/create/', views.invoice_create, name='invoice_create'),
    path('invoices/<str:invoice_number>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<str:invoice_number>/add-items/', views.invoice_add_items, name='invoice_add_items'),
    
    # Payments
    path('invoices/<str:invoice_number>/payment/create/', views.payment_create, name='payment_create'),
]
