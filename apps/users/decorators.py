from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.user_type == 'ADMIN':
            return view_func(request, *args, **kwargs)
        messages.error(request, 'You must be logged in as an administrator to access this page.')
        return redirect('users:login')
    return _wrapped_view

def pharmacy_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.user_type == 'PHARMACY_STAFF':
            return view_func(request, *args, **kwargs)
        messages.error(request, 'You must be logged in as pharmacy staff to access this page.')
        return redirect('users:login')
    return _wrapped_view

def doctor_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.user_type == 'DOCTOR':
            return view_func(request, *args, **kwargs)
        messages.error(request, 'You must be logged in as a doctor to access this page.')
        return redirect('users:login')
    return _wrapped_view

def staff_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return view_func(request, *args, **kwargs)
        messages.error(request, 'You must be logged in as staff to access this page.')
        return redirect('users:login')
    return _wrapped_view

def lab_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.user_type == 'LAB_STAFF':
            return view_func(request, *args, **kwargs)
        messages.error(request, 'You must be logged in as laboratory staff to access this page.')
        return redirect('users:login')
    return _wrapped_view

def inventory_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.user_type == 'STAFF':
            return view_func(request, *args, **kwargs)
        messages.error(request, 'You must be logged in as inventory staff to access this page.')
        return redirect('users:login')
    return _wrapped_view
