from django import forms
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Appointment
from apps.staff.models import Doctor

from django import forms
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Appointment
from apps.staff.models import Doctor

class AppointmentBookingForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        })
    )
    time_slot = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        }),
        help_text='Select your preferred appointment time'
    )
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select Doctor"
    )
    symptoms = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Please describe your symptoms'
        }),
        required=True
    )
    
    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time_slot', 'symptoms']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = Doctor.objects.filter(is_active=True)
        
    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date < timezone.now().date():
            raise forms.ValidationError("Appointment date cannot be in the past.")
        return date
