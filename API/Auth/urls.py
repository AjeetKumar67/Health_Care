from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    ChangePasswordView,
    UpdateProfileView,
    RequestPasswordResetView,
    ResetPasswordConfirmView,
    LogoutView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('update-profile/', UpdateProfileView.as_view(), name='update_profile'),
    path('request-reset-password/', RequestPasswordResetView.as_view(), name='request_reset_password'),
    path('reset-password/', ResetPasswordConfirmView.as_view(), name='reset_password_confirm'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
