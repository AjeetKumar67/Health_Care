from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Staff, Doctor, Department, Schedule
from apps.users.models import User

class StaffForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput(), required=False)
    
    class Meta:
        model = Staff
        fields = ['staff_type', 'department', 'specialization', 'qualification',
                 'experience_years', 'joining_date', 'phone', 'address']
        widgets = {
            'joining_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['password'].required = False
        else:
            self.fields['password'].required = True

    def save(self, commit=True):
        staff = super().save(commit=False)
        if not self.instance.pk:
            # Creating new user
            user = User.objects.create_user(
                username=self.cleaned_data['email'],
                email=self.cleaned_data['email'],
                password=self.cleaned_data['password'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                user_type=self.cleaned_data['staff_type']
            )
            staff.user = user
        else:
            # Updating existing user
            user = staff.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            if self.cleaned_data['password']:
                user.set_password(self.cleaned_data['password'])
            user.save()
        
        if commit:
            staff.save()
        return staff

class DoctorForm(StaffForm):
    class Meta(StaffForm.Meta):
        model = Doctor
        fields = StaffForm.Meta.fields + ['license_number', 'consultation_fee', 
                                        'available_days', 'available_times']

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['day', 'start_time', 'end_time', 'is_available']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }
