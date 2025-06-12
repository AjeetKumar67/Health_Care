from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils.crypto import get_random_string
from django.db.models import Q
from django.http import JsonResponse
from .models import Patient, MedicalRecord, PatientDocument
from apps.appointments.models import Appointment
from apps.pharmacy.models import Prescription
from apps.lab.models import TestRequest
from apps.users.decorators import doctor_required, staff_required
from .forms import PatientForm, MedicalRecordForm, PatientDocumentForm

@login_required
def patient_dashboard(request):
    """Dashboard view for patients to see their information and recent activities"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, "Patient profile not found.")
        return redirect('users:dashboard')
    
    # Get recent appointments
    recent_appointments = Appointment.objects.filter(
        patient=patient
    ).order_by('-date')[:5]
    
    # Get recent prescriptions
    recent_prescriptions = Prescription.objects.filter(
        patient=patient
    ).order_by('-prescribed_date')[:5]
    
    # Get recent medical records
    recent_medical_records = MedicalRecord.objects.filter(
        patient=patient
    ).order_by('-date')[:5]
    
    # Get recent lab tests
    recent_lab_tests = TestRequest.objects.filter(
        patient=patient
    ).order_by('-requested_date')[:5]
    
    context = {
        'patient': patient,
        'recent_appointments': recent_appointments,
        'recent_prescriptions': recent_prescriptions,
        'recent_medical_records': recent_medical_records,
        'recent_lab_tests': recent_lab_tests,
    }
    return render(request, 'patients/dashboard.html', context)

@login_required
@staff_required
def patient_list(request):
    """View for staff to see list of all patients"""
    search_query = request.GET.get('search', '')
    if search_query:
        patients = Patient.objects.filter(
            Q(patient_id__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    else:
        patients = Patient.objects.all()
    
    paginator = Paginator(patients.order_by('-created_at'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'patients/patient_list.html', {'page_obj': page_obj})

@login_required
def patient_detail(request, patient_id):
    """View patient details"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    
    # Check permissions
    if not request.user.is_staff and request.user != patient.user:
        messages.error(request, "You don't have permission to view this profile.")
        return redirect('users:dashboard')
    
    # Get patient's medical records
    medical_records = MedicalRecord.objects.filter(patient=patient).order_by('-date')
    
    # Get patient's documents
    documents = PatientDocument.objects.filter(patient=patient).order_by('-uploaded_at')
    
    # Get patient's appointments
    appointments = Appointment.objects.filter(patient=patient).order_by('-date')
    
    context = {
        'patient': patient,
        'medical_records': medical_records,
        'documents': documents,
        'appointments': appointments,
    }
    return render(request, 'patients/patient_detail.html', context)

@login_required
def patient_edit(request, patient_id):
    """Edit patient profile"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    
    # Check permissions
    if not request.user.is_staff and request.user != patient.user:
        messages.error(request, "You don't have permission to edit this profile.")
        return redirect('users:dashboard')
    
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('patients:patient_detail', patient_id=patient.patient_id)
    else:
        form = PatientForm(instance=patient)
    
    return render(request, 'patients/patient_form.html', {
        'form': form,
        'patient': patient,
        'title': 'Edit Patient Profile'
    })

@login_required
@staff_required
def patient_create(request):
    """Create new patient profile"""
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.patient_id = 'PAT' + get_random_string(7, '0123456789')
            patient.save()
            messages.success(request, 'Patient profile created successfully!')
            return redirect('patients:patient_detail', patient_id=patient.patient_id)
    else:
        form = PatientForm()
    
    return render(request, 'patients/patient_form.html', {
        'form': form,
        'title': 'Create New Patient'
    })

@login_required
@doctor_required
def medical_record_create(request, patient_id):
    """Create new medical record"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    
    if request.method == 'POST':
        form = MedicalRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.patient = patient
            record.save()
            messages.success(request, 'Medical record added successfully!')
            return redirect('patients:patient_detail', patient_id=patient.patient_id)
    else:
        form = MedicalRecordForm()
    
    return render(request, 'patients/medical_record_form.html', {
        'form': form,
        'patient': patient,
        'title': 'Add Medical Record'
    })

@login_required
def document_upload(request, patient_id):
    """Upload patient documents"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    
    # Check permissions
    if not request.user.is_staff and request.user != patient.user:
        messages.error(request, "You don't have permission to upload documents.")
        return redirect('users:dashboard')
    
    if request.method == 'POST':
        form = PatientDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.patient = patient
            document.save()
            messages.success(request, 'Document uploaded successfully!')
            return redirect('patients:patient_detail', patient_id=patient.patient_id)
    else:
        form = PatientDocumentForm()
    
    return render(request, 'patients/document_upload.html', {
        'form': form,
        'patient': patient,
        'title': 'Upload Document'
    })

@login_required
def medical_records(request, patient_id):
    """View all medical records for a patient"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    
    # Check permissions
    if not request.user.is_staff and request.user != patient.user:
        messages.error(request, "You don't have permission to view medical records.")
        return redirect('users:dashboard')
    
    records = MedicalRecord.objects.filter(patient=patient).order_by('-date')
    paginator = Paginator(records, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'patients/medical_records.html', {
        'page_obj': page_obj,
        'patient': patient
    })
