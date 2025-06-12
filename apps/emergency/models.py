from django.db import models
from apps.patients.models import Patient
from apps.staff.models import Staff
from apps.infrastructure.models import Bed

class EmergencyContact(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    relationship = models.CharField(max_length=50)
    address = models.TextField()
    
    def __str__(self):
        return f"{self.name} - {self.relationship}"

class EmergencyCase(models.Model):
    SEVERITY_LEVELS = [
        ('CRITICAL', 'Critical'),
        ('SEVERE', 'Severe'),
        ('MODERATE', 'Moderate'),
        ('MILD', 'Mild'),
    ]
    
    STATUS_CHOICES = [
        ('REGISTERED', 'Registered'),
        ('TRIAGE', 'In Triage'),
        ('TREATMENT', 'Under Treatment'),
        ('ADMITTED', 'Admitted'),
        ('DISCHARGED', 'Discharged'),
        ('TRANSFERRED', 'Transferred'),
        ('DECEASED', 'Deceased'),
    ]
    
    case_id = models.CharField(max_length=10, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    emergency_contact = models.ForeignKey(EmergencyContact, on_delete=models.SET_NULL, null=True)
    arrival_time = models.DateTimeField(auto_now_add=True)
    chief_complaint = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='REGISTERED')
    attending_doctor = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='emergency_cases')
    assigned_bed = models.ForeignKey(Bed, on_delete=models.SET_NULL, null=True)
    vital_signs = models.TextField()
    initial_diagnosis = models.TextField()
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Emergency Case {self.case_id}"

class EmergencyTreatment(models.Model):
    emergency_case = models.ForeignKey(EmergencyCase, on_delete=models.CASCADE)
    treatment_time = models.DateTimeField(auto_now_add=True)
    procedure = models.TextField()
    medications = models.TextField()
    performed_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True)
    notes = models.TextField()
    
    def __str__(self):
        return f"Treatment for Case {self.emergency_case.case_id}"

class Ambulance(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('ON_CALL', 'On Call'),
        ('MAINTENANCE', 'Under Maintenance'),
    ]
    
    vehicle_number = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    driver_name = models.CharField(max_length=100)
    driver_phone = models.CharField(max_length=15)
    last_maintenance = models.DateField()
    
    def __str__(self):
        return f"Ambulance {self.vehicle_number}"

class AmbulanceCall(models.Model):
    call_id = models.CharField(max_length=10, unique=True)
    ambulance = models.ForeignKey(Ambulance, on_delete=models.CASCADE)
    emergency_case = models.ForeignKey(EmergencyCase, on_delete=models.CASCADE)
    pickup_location = models.TextField()
    dispatch_time = models.DateTimeField()
    arrival_time = models.DateTimeField(null=True, blank=True)
    return_time = models.DateTimeField(null=True, blank=True)
    distance_covered = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Ambulance Call {self.call_id}"
