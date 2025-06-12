from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime, timedelta
from django.utils import timezone
from .models import (
    EmergencyCase, EmergencyContact, EmergencyTreatment,
    Ambulance, AmbulanceCall
)
from .forms import (
    EmergencyContactForm, EmergencyRegistrationForm,
    EmergencyTreatmentForm, AmbulanceForm, AmbulanceCallForm
)
from apps.users.decorators import staff_required

@login_required
@staff_required
def emergency_dashboard(request):
    """Emergency department dashboard view"""
    # Get current cases
    active_cases = EmergencyCase.objects.filter(
        status__in=['REGISTERED', 'TRIAGE', 'TREATMENT', 'ADMITTED']
    ).select_related('patient', 'attending_doctor', 'assigned_bed')
    
    # Get available ambulances
    available_ambulances = Ambulance.objects.filter(status='AVAILABLE').count()
    total_ambulances = Ambulance.objects.count()
    
    # Get active ambulance calls
    active_calls = AmbulanceCall.objects.filter(
        return_time__isnull=True
    ).select_related('ambulance', 'emergency_case')
    
    # Get statistics
    today = timezone.now().date()
    today_cases = EmergencyCase.objects.filter(
        arrival_time__date=today
    ).count()
    
    critical_cases = EmergencyCase.objects.filter(
        status__in=['REGISTERED', 'TRIAGE', 'TREATMENT'],
        severity='CRITICAL'
    ).count()
    
    # Calculate bed occupancy
    total_er_beds = 50  # This should come from settings or ward configuration
    occupied_beds = EmergencyCase.objects.filter(
        status__in=['TREATMENT', 'ADMITTED'],
        assigned_bed__isnull=False
    ).count()
    
    context = {
        'active_cases': active_cases,
        'available_ambulances': available_ambulances,
        'total_ambulances': total_ambulances,
        'active_calls': active_calls,
        'today_cases': today_cases,
        'critical_cases': critical_cases,
        'occupied_beds': occupied_beds,
        'total_er_beds': total_er_beds,
        'bed_occupancy': (occupied_beds / total_er_beds * 100) if total_er_beds > 0 else 0,
    }
    return render(request, 'emergency/dashboard.html', context)

@login_required
@staff_required
def case_list(request):
    """View list of emergency cases"""
    status_filter = request.GET.get('status', '')
    severity_filter = request.GET.get('severity', '')
    search_query = request.GET.get('search', '')
    
    cases = EmergencyCase.objects.select_related(
        'patient', 'attending_doctor', 'assigned_bed'
    )
    
    if status_filter:
        cases = cases.filter(status=status_filter)
    
    if severity_filter:
        cases = cases.filter(severity=severity_filter)
    
    if search_query:
        cases = cases.filter(
            Q(case_id__icontains=search_query) |
            Q(patient__full_name__icontains=search_query) |
            Q(chief_complaint__icontains=search_query)
        )
    
    cases = cases.order_by('-arrival_time')
    
    paginator = Paginator(cases, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'severity_filter': severity_filter,
        'search_query': search_query,
        'status_choices': EmergencyCase.STATUS_CHOICES,
        'severity_levels': EmergencyCase.SEVERITY_LEVELS,
    }
    return render(request, 'emergency/case_list.html', context)

@login_required
@staff_required
def case_create(request):
    """Register new emergency case"""
    if request.method == 'POST':
        contact_form = EmergencyContactForm(request.POST)
        case_form = EmergencyRegistrationForm(request.POST)
        
        if contact_form.is_valid() and case_form.is_valid():
            emergency_contact = contact_form.save()
            emergency_case = case_form.save(commit=False)
            
            # Generate case ID
            today = datetime.now().strftime('%Y%m%d')
            count = EmergencyCase.objects.filter(
                case_id__startswith=f'ER{today}'
            ).count()
            emergency_case.case_id = f'ER{today}{count+1:03d}'
            
            emergency_case.emergency_contact = emergency_contact
            emergency_case.save()
            
            messages.success(request, 'Emergency case registered successfully.')
            return redirect('emergency:case_detail', pk=emergency_case.pk)
    else:
        contact_form = EmergencyContactForm()
        case_form = EmergencyRegistrationForm()
    
    return render(request, 'emergency/case_form.html', {
        'contact_form': contact_form,
        'case_form': case_form,
        'title': 'Register Emergency Case'
    })

@login_required
@staff_required
def case_detail(request, pk):
    """View emergency case details"""
    case = get_object_or_404(EmergencyCase, pk=pk)
    treatments = EmergencyTreatment.objects.filter(
        emergency_case=case
    ).select_related('performed_by')
    
    if request.method == 'POST':
        treatment_form = EmergencyTreatmentForm(request.POST)
        if treatment_form.is_valid():
            treatment = treatment_form.save(commit=False)
            treatment.emergency_case = case
            treatment.save()
            messages.success(request, 'Treatment record added successfully.')
            return redirect('emergency:case_detail', pk=pk)
    else:
        treatment_form = EmergencyTreatmentForm()
    
    context = {
        'case': case,
        'treatments': treatments,
        'treatment_form': treatment_form,
    }
    return render(request, 'emergency/case_detail.html', context)

@login_required
@staff_required
def case_edit(request, pk):
    """Edit emergency case"""
    case = get_object_or_404(EmergencyCase, pk=pk)
    
    if request.method == 'POST':
        case_form = EmergencyRegistrationForm(request.POST, instance=case)
        contact_form = EmergencyContactForm(
            request.POST,
            instance=case.emergency_contact
        )
        
        if case_form.is_valid() and contact_form.is_valid():
            contact_form.save()
            case_form.save()
            messages.success(request, 'Emergency case updated successfully.')
            return redirect('emergency:case_detail', pk=pk)
    else:
        case_form = EmergencyRegistrationForm(instance=case)
        contact_form = EmergencyContactForm(instance=case.emergency_contact)
    
    return render(request, 'emergency/case_form.html', {
        'case_form': case_form,
        'contact_form': contact_form,
        'title': 'Edit Emergency Case',
        'case': case
    })

@login_required
@staff_required
def ambulance_list(request):
    """View list of ambulances"""
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    ambulances = Ambulance.objects.all()
    
    if status_filter:
        ambulances = ambulances.filter(status=status_filter)
    
    if search_query:
        ambulances = ambulances.filter(
            Q(vehicle_number__icontains=search_query) |
            Q(driver_name__icontains=search_query)
        )
    
    ambulances = ambulances.order_by('vehicle_number')
    
    context = {
        'ambulances': ambulances,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': Ambulance.STATUS_CHOICES,
    }
    return render(request, 'emergency/ambulance_list.html', context)

@login_required
@staff_required
def ambulance_create(request):
    """Add new ambulance"""
    if request.method == 'POST':
        form = AmbulanceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ambulance added successfully.')
            return redirect('emergency:ambulance_list')
    else:
        form = AmbulanceForm()
    
    return render(request, 'emergency/ambulance_form.html', {
        'form': form,
        'title': 'Add New Ambulance'
    })

@login_required
@staff_required
def ambulance_edit(request, pk):
    """Edit ambulance details"""
    ambulance = get_object_or_404(Ambulance, pk=pk)
    
    if request.method == 'POST':
        form = AmbulanceForm(request.POST, instance=ambulance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ambulance updated successfully.')
            return redirect('emergency:ambulance_list')
    else:
        form = AmbulanceForm(instance=ambulance)
    
    return render(request, 'emergency/ambulance_form.html', {
        'form': form,
        'title': 'Edit Ambulance',
        'ambulance': ambulance
    })

@login_required
@staff_required
def ambulance_call_list(request):
    """View list of ambulance calls"""
    status_filter = request.GET.get('status', '')  # active/completed
    search_query = request.GET.get('search', '')
    
    calls = AmbulanceCall.objects.select_related(
        'ambulance', 'emergency_case'
    )
    
    if status_filter == 'active':
        calls = calls.filter(return_time__isnull=True)
    elif status_filter == 'completed':
        calls = calls.filter(return_time__isnull=False)
    
    if search_query:
        calls = calls.filter(
            Q(call_id__icontains=search_query) |
            Q(pickup_location__icontains=search_query) |
            Q(ambulance__vehicle_number__icontains=search_query)
        )
    
    calls = calls.order_by('-dispatch_time')
    
    paginator = Paginator(calls, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    return render(request, 'emergency/ambulance_call_list.html', context)

@login_required
@staff_required
def ambulance_call_create(request):
    """Create new ambulance call"""
    if request.method == 'POST':
        form = AmbulanceCallForm(request.POST)
        if form.is_valid():
            call = form.save(commit=False)
            
            # Generate call ID
            today = datetime.now().strftime('%Y%m%d')
            count = AmbulanceCall.objects.filter(
                call_id__startswith=f'AMB{today}'
            ).count()
            call.call_id = f'AMB{today}{count+1:03d}'
            
            # Update ambulance status
            ambulance = call.ambulance
            ambulance.status = 'ON_CALL'
            ambulance.save()
            
            call.save()
            messages.success(request, 'Ambulance call created successfully.')
            return redirect('emergency:ambulance_call_list')
    else:
        form = AmbulanceCallForm()
    
    return render(request, 'emergency/ambulance_call_form.html', {
        'form': form,
        'title': 'Create Ambulance Call'
    })

@login_required
@staff_required
def ambulance_call_edit(request, pk):
    """Edit ambulance call"""
    call = get_object_or_404(AmbulanceCall, pk=pk)
    
    if request.method == 'POST':
        form = AmbulanceCallForm(request.POST, instance=call)
        if form.is_valid():
            call = form.save()
            
            # Update ambulance status if call is complete
            if call.return_time:
                ambulance = call.ambulance
                ambulance.status = 'AVAILABLE'
                ambulance.save()
            
            messages.success(request, 'Ambulance call updated successfully.')
            return redirect('emergency:ambulance_call_list')
    else:
        form = AmbulanceCallForm(instance=call)
    
    return render(request, 'emergency/ambulance_call_form.html', {
        'form': form,
        'title': 'Edit Ambulance Call',
        'call': call
    })
