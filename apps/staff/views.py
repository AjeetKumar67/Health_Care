from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.db.models import Count
from django.core.paginator import Paginator
from datetime import datetime
from .models import Staff, Department, Doctor, Schedule
from .forms import StaffForm, DoctorForm, DepartmentForm, ScheduleForm
from apps.users.decorators import admin_required

@login_required
@admin_required
def staff_dashboard(request):
    # Get summary statistics
    total_staff = Staff.objects.count()
    total_doctors = Doctor.objects.count()
    total_departments = Department.objects.count()
    active_staff = Staff.objects.filter(is_active=True).count()
    
    # Get staff by department
    dept_stats = Department.objects.annotate(
        staff_count=Count('staff')
    ).values('name', 'staff_count')
    
    # Get recent staff additions
    recent_staff = Staff.objects.select_related('user', 'department').order_by('-created_at')[:5]
    
    context = {
        'total_staff': total_staff,
        'total_doctors': total_doctors,
        'total_departments': total_departments,
        'active_staff': active_staff,
        'dept_stats': dept_stats,
        'recent_staff': recent_staff,
    }
    return render(request, 'staff/dashboard.html', context)

@login_required
@admin_required
def staff_list(request):
    staff_members = Staff.objects.select_related('user', 'department').all()
    paginator = Paginator(staff_members, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'staff/staff_list.html', {'page_obj': page_obj})

@login_required
@admin_required
def staff_create(request):
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            staff = form.save(commit=False)
            staff.staff_id = 'STF' + get_random_string(7, '0123456789')
            staff.save()
            messages.success(request, 'Staff member added successfully!')
            return redirect('staff:staff_detail', pk=staff.pk)
    else:
        form = StaffForm()
    return render(request, 'staff/staff_form.html', {
        'form': form,
        'title': 'Add New Staff Member'
    })

@login_required
@admin_required
def staff_detail(request, pk):
    staff = get_object_or_404(Staff.objects.select_related('user', 'department'), pk=pk)
    schedule = Schedule.objects.filter(staff=staff)
    return render(request, 'staff/staff_detail.html', {
        'staff': staff,
        'schedule': schedule
    })

@login_required
@admin_required
def staff_edit(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    if request.method == 'POST':
        form = StaffForm(request.POST, instance=staff)
        if form.is_valid():
            form.save()
            messages.success(request, 'Staff details updated successfully!')
            return redirect('staff:staff_detail', pk=pk)
    else:
        form = StaffForm(instance=staff)
    return render(request, 'staff/staff_form.html', {
        'form': form,
        'title': 'Edit Staff Member',
        'staff': staff
    })

@login_required
@admin_required
def department_list(request):
    departments = Department.objects.annotate(staff_count=Count('staff'))
    return render(request, 'staff/department_list.html', {'departments': departments})

@login_required
@admin_required
def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department created successfully!')
            return redirect('staff:department_list')
    else:
        form = DepartmentForm()
    return render(request, 'staff/department_form.html', {
        'form': form,
        'title': 'Create New Department'
    })

@login_required
@admin_required
def department_edit(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department updated successfully!')
            return redirect('staff:department_list')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'staff/department_form.html', {
        'form': form,
        'title': 'Edit Department',
        'department': department
    })

@login_required
@admin_required
def doctor_list(request):
    doctors = Doctor.objects.select_related('user', 'department').all()
    paginator = Paginator(doctors, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'staff/doctor_list.html', {'page_obj': page_obj})

@login_required
@admin_required
def doctor_create(request):
    if request.method == 'POST':
        form = DoctorForm(request.POST)
        if form.is_valid():
            doctor = form.save(commit=False)
            doctor.staff_id = 'DOC' + get_random_string(7, '0123456789')
            doctor.staff_type = 'DOCTOR'
            doctor.save()
            messages.success(request, 'Doctor added successfully!')
            return redirect('staff:doctor_detail', pk=doctor.pk)
    else:
        form = DoctorForm()
    return render(request, 'staff/doctor_form.html', {
        'form': form,
        'title': 'Add New Doctor'
    })

@login_required
@admin_required
def doctor_detail(request, pk):
    doctor = get_object_or_404(Doctor.objects.select_related('user', 'department'), pk=pk)
    schedule = Schedule.objects.filter(staff=doctor)
    return render(request, 'staff/doctor_detail.html', {
        'doctor': doctor,
        'schedule': schedule
    })

@login_required
def schedule_create(request, staff_id):
    staff = get_object_or_404(Staff, pk=staff_id)
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.staff = staff
            schedule.save()
            messages.success(request, 'Schedule created successfully!')
            return redirect('staff:staff_detail', pk=staff_id)
    else:
        form = ScheduleForm()
    return render(request, 'staff/schedule_form.html', {
        'form': form,
        'staff': staff,
        'title': 'Create Schedule'
    })
