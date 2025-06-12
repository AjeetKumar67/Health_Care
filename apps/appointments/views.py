from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.http import JsonResponse
from datetime import datetime, timedelta
from .models import Appointment, DoctorSchedule
from apps.patients.models import Patient
from apps.staff.models import Doctor
from .forms import AppointmentBookingForm

@login_required
def book_appointment(request):
    if request.user.user_type != 'PATIENT':
        messages.error(request, "Only patients can book appointments.")
        return redirect('users:dashboard')

    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, "Patient profile not found. Please complete your profile first.")
        return redirect('users:dashboard')

    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST)
        if form.is_valid():
            try:
                appointment = form.save(commit=False)
                appointment.patient = patient
                appointment.appointment_id = 'APT' + get_random_string(7, '0123456789')
                appointment.status = 'SCHEDULED'
                appointment.save()
                
                messages.success(request, 'Appointment booked successfully!')
                return redirect('appointments:appointment_detail', appointment_id=appointment.appointment_id)
            except Exception as e:
                messages.error(request, f"Error booking appointment: {str(e)}")
    else:
        form = AppointmentBookingForm()

    return render(request, 'appointments/book_appointment.html', {
        'form': form
    })

@login_required
def appointment_detail(request, appointment_id):
    appointment = get_object_or_404(Appointment, appointment_id=appointment_id)
    if request.user != appointment.patient.user and request.user != appointment.doctor.user:
        messages.error(request, "You don't have permission to view this appointment.")
        return redirect('users:dashboard')
        
    return render(request, 'appointments/appointment_detail.html', {
        'appointment': appointment
    })

@login_required
def get_doctor_schedule(request):
    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')
    
    if not doctor_id or not date_str:
        return JsonResponse({'error': 'Missing parameters'}, status=400)
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        day_of_week = date.weekday()
        
        schedule = DoctorSchedule.objects.filter(
            doctor_id=doctor_id,
            day_of_week=day_of_week,
            is_available=True
        ).first()
        
        if not schedule:
            return JsonResponse({'error': 'No schedule found'}, status=404)
        
        # Get already booked appointments
        booked_slots = Appointment.objects.filter(
            doctor_id=doctor_id,
            date=date_str
        ).values_list('time_slot', flat=True)
        
        # Generate available time slots
        available_slots = []
        current_time = schedule.start_time
        while current_time < schedule.end_time:
            slot = current_time.strftime('%H:%M')
            if slot not in booked_slots:
                available_slots.append(slot)
            current_time = (datetime.combine(date.today(), current_time) + timedelta(minutes=30)).time()
        
        return JsonResponse({'slots': available_slots})
        
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid parameters'}, status=400)

@login_required
def my_appointments(request):
    if request.user.user_type == 'PATIENT':
        try:
            patient = Patient.objects.get(user=request.user)
            appointments = Appointment.objects.filter(patient=patient).order_by('-date')
        except Patient.DoesNotExist:
            appointments = []
    else:
        appointments = []
    
    return render(request, 'appointments/my_appointments.html', {
        'appointments': appointments
    })

@login_required
def doctor_appointments(request):
    """View for doctors to see their appointments"""
    if request.user.user_type != 'DOCTOR':
        messages.error(request, "Only doctors can access this page.")
        return redirect('users:dashboard')

    try:
        doctor = Doctor.objects.get(user=request.user)
        appointments = Appointment.objects.filter(doctor=doctor).order_by('-date')
    except Doctor.DoesNotExist:
        appointments = []
        messages.error(request, "Doctor profile not found.")
        return redirect('users:dashboard')

    return render(request, 'appointments/doctor_appointments.html', {
        'appointments': appointments
    })
