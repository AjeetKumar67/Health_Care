from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.template.exceptions import TemplateDoesNotExist
from .forms import (
    CustomUserCreationForm, CustomAuthenticationForm,
    CustomPasswordChangeForm, UserProfileForm
)
from .models import User, UserLog


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'users/login.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        UserLog.objects.create(
            user=self.request.user,
            action='Login',
            ip_address=self.request.META.get('REMOTE_ADDR', ''),
            details='User logged in successfully'
        )
        
        # Role-based redirection
        if self.request.user.user_type == 'PHARMACY_STAFF':
            return redirect('pharmacy:dashboard')
        elif self.request.user.user_type == 'DOCTOR':
            return redirect('appointments:doctor_appointments')
        elif self.request.user.user_type == 'PATIENT':
            return redirect('appointments:my_appointments')
        elif self.request.user.user_type == 'LAB_STAFF':
            return redirect('lab:dashboard')
        return response

    def get_success_url(self):
        if self.request.user.user_type == 'PHARMACY_STAFF':
            return reverse_lazy('pharmacy:dashboard')
        return reverse_lazy('users:dashboard')
        

class CustomLogoutView(LogoutView):
    next_page = 'users:login'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            UserLog.objects.create(
                user=request.user,
                action='Logout',
                ip_address=request.META.get('REMOTE_ADDR', ''),
                details='User logged out successfully'
            )
        return super().dispatch(request, *args, **kwargs)


class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Account created successfully. Please login.')
        return response


@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')
    
    def get_object(self):
        return self.request.user


@method_decorator(login_required, name='dispatch')
class PasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'users/password_change.html'
    success_url = reverse_lazy('users:profile')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Password changed successfully.')
        return response


@login_required
def dashboard(request):
    user_type = request.user.user_type.upper()
    template_name = f'users/dashboard_{user_type.lower()}.html'
    
    context = {
        'user': request.user,
    }
    
    # Add role-specific context data
    if user_type == 'DOCTOR':
        from apps.appointments.models import Appointment
        from apps.staff.models import Doctor
        try:
            doctor = Doctor.objects.get(user=request.user)
            context['upcoming_appointments'] = Appointment.objects.filter(
                doctor=doctor,
                status='SCHEDULED'
            ).order_by('date')[:5]
        except Doctor.DoesNotExist:
            context['upcoming_appointments'] = []
        
    elif user_type == 'PATIENT':
        from apps.appointments.models import Appointment
        from apps.patients.models import Patient
        try:
            patient = Patient.objects.get(user=request.user)
            context['appointments'] = Appointment.objects.filter(
                patient=patient
            ).order_by('-date')[:5]
        except Patient.DoesNotExist:
            context['appointments'] = []
        
    elif user_type == 'ADMIN':
        context['recent_users'] = User.objects.order_by('-date_joined')[:5]
        context['recent_activities'] = UserLog.objects.order_by('-timestamp')[:10]
    
    try:
        return render(request, template_name, context)
    except TemplateDoesNotExist:
        return render(request, 'users/dashboard.html', context)
