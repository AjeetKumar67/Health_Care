from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import uuid
from datetime import timedelta

from .serializers import (
    UserSerializer,
    UpdateUserSerializer,
    ChangePasswordSerializer,
    ResetPasswordSerializer,
    ResetPasswordConfirmSerializer,
    CustomTokenObtainPairSerializer
)
from .models import TokenBlacklist

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class ChangePasswordView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def update(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            if not user.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, 
                             status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(serializer.data.get("new_password"))
            user.save()
            return Response({"message": "Password updated successfully"}, 
                          status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateProfileView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UpdateUserSerializer

    def get_object(self):
        return self.request.user

class RequestPasswordResetView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data["email"]
            try:
                user = User.objects.get(email=email)
                token = str(uuid.uuid4())
                user.reset_password_token = token
                user.reset_password_expires = timezone.now() + timedelta(hours=1)
                user.save()

                reset_url = f"http://your-frontend-url/reset-password?token={token}"
                send_mail(
                    'Password Reset Request',
                    f'Click this link to reset your password: {reset_url}',
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )
                return Response({"message": "Password reset email has been sent."}, 
                              status=status.HTTP_200_OK)
            except User.DoesNotExist:
                pass
            
            return Response({"message": "If the email exists, a reset link has been sent."}, 
                          status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordConfirmView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ResetPasswordConfirmSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            token = serializer.data["token"]
            try:
                user = User.objects.get(
                    reset_password_token=token,
                    reset_password_expires__gt=timezone.now()
                )
                user.set_password(serializer.data["new_password"])
                user.reset_password_token = ""
                user.reset_password_expires = None
                user.save()
                return Response({"message": "Password has been reset."}, 
                              status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "Invalid or expired token."}, 
                              status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            TokenBlacklist.objects.create(token=str(token))
            token.blacklist()
            return Response({"message": "Successfully logged out."}, 
                          status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Invalid token."}, 
                          status=status.HTTP_400_BAD_REQUEST)
