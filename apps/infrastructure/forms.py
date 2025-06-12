from django import forms
from .models import Building, Ward, Bed, Equipment, MaintenanceRecord

class BuildingForm(forms.ModelForm):
    class Meta:
        model = Building
        fields = ['name', 'description', 'floors', 'address']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class WardForm(forms.ModelForm):
    class Meta:
        model = Ward
        fields = ['name', 'building', 'floor', 'ward_type', 'capacity', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        floor = cleaned_data.get('floor')
        building = cleaned_data.get('building')
        
        if floor and building and floor > building.floors:
            raise forms.ValidationError("Floor number cannot be greater than building's total floors.")
        return cleaned_data

class BedForm(forms.ModelForm):
    class Meta:
        model = Bed
        fields = ['bed_number', 'ward', 'status', 'price_per_day', 'is_active', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = [
            'name', 'equipment_type', 'serial_number', 'manufacturer',
            'purchase_date', 'warranty_expiry', 'last_maintenance',
            'next_maintenance', 'location', 'status', 'notes'
        ]
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'warranty_expiry': forms.DateInput(attrs={'type': 'date'}),
            'last_maintenance': forms.DateInput(attrs={'type': 'date'}),
            'next_maintenance': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class MaintenanceRecordForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRecord
        fields = ['equipment', 'maintenance_date', 'performed_by', 'description', 'cost', 'next_maintenance']
        widgets = {
            'maintenance_date': forms.DateInput(attrs={'type': 'date'}),
            'next_maintenance': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
