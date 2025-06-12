from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.support_dashboard, name='dashboard'),
    
    # Support Tickets
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/create/', views.ticket_create, name='ticket_create'),
    path('tickets/<str:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('tickets/<str:ticket_id>/edit/', views.ticket_edit, name='ticket_edit'),
    path('tickets/<str:ticket_id>/respond/', views.ticket_respond, name='ticket_respond'),
    
    # Feedback
    path('feedback/', views.feedback_list, name='feedback_list'),
    path('feedback/create/', views.feedback_create, name='feedback_create'),
    path('feedback/<int:pk>/', views.feedback_detail, name='feedback_detail'),
    path('feedback/<int:pk>/resolve/', views.feedback_resolve, name='feedback_resolve'),
    
    # FAQ
    path('faq/', views.faq_list, name='faq_list'),
    path('faq/create/', views.faq_create, name='faq_create'),
    path('faq/<int:pk>/edit/', views.faq_edit, name='faq_edit'),
    path('faq/<int:pk>/toggle/', views.faq_toggle_publish, name='faq_toggle_publish'),
    
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
]
