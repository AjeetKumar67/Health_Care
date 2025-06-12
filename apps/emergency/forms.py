from django import forms
from .models import EmergencyCase, EmergencyContact, EmergencyTreatment, Ambulance, AmbulanceCall
from apps.staff.models import Staff
from apps.infrastructure.models import Bed

class EmergencyContactForm(forms.ModelForm):
    class Meta:
        model = EmergencyContact
        fields = ['name', 'phone', 'relationship', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class EmergencyRegistrationForm(forms.ModelForm):
    class Meta:
        model = EmergencyCase
        fields = [
            'chief_complaint', 'severity', 'vital_signs',
            'initial_diagnosis', 'notes', 'attending_doctor', 'assigned_bed'
        ]
        widgets = {
            'chief_complaint': forms.Textarea(attrs={'rows': 3}),
            'vital_signs': forms.Textarea(attrs={'rows': 3}),
            'initial_diagnosis': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter only doctors and available beds
        self.fields['attending_doctor'].queryset = Staff.objects.filter(role='DOCTOR')
        self.fields['assigned_bed'].queryset = Bed.objects.filter(status='AVAILABLE')

class EmergencyTreatmentForm(forms.ModelForm):
    class Meta:
        model = EmergencyTreatment
        fields = ['procedure', 'medications', 'performed_by', 'notes']
        widgets = {
            'procedure': forms.Textarea(attrs={'rows': 3}),
            'medications': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter only medical staff
        self.fields['performed_by'].queryset = Staff.objects.filter(
            role__in=['DOCTOR', 'NURSE']
        )

class AmbulanceForm(forms.ModelForm):
    class Meta:
        model = Ambulance
        fields = [
            'vehicle_number', 'vehicle_type', 'status',
            'driver_name', 'driver_phone', 'last_maintenance'
        ]
        widgets = {
            'last_maintenance': forms.DateInput(attrs={'type': 'date'}),
        }

class AmbulanceCallForm(forms.ModelForm):
    class Meta:
        model = AmbulanceCall
        fields = [
            'ambulance', 'emergency_case', 'pickup_location',
            'dispatch_time', 'arrival_time', 'return_time',
            'distance_covered', 'notes'
        ]
        widgets = {
            'pickup_location': forms.Textarea(attrs={'rows': 3}),
            'dispatch_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'arrival_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'return_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter only available ambulances
        self.fields['ambulance'].queryset = Ambulance.objects.filter(
            status='AVAILABLE'
        )
