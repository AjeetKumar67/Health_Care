from django import forms
from django.contrib.auth import get_user_model
from .models import Patient, MedicalRecord, PatientDocument

User = get_user_model()

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'date_of_birth', 'blood_group', 'gender', 'phone', 'address',
            'emergency_contact_name', 'emergency_contact_phone',
            'medical_history', 'allergies'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'medical_history': forms.Textarea(attrs={'rows': 3}),
            'allergies': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['diagnosis', 'prescription', 'notes']
        widgets = {
            'diagnosis': forms.Textarea(attrs={'rows': 3}),
            'prescription': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class PatientDocumentForm(forms.ModelForm):
    class Meta:
        model = PatientDocument
        fields = ['title', 'document', 'document_type', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
