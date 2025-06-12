from django import forms
from .models import TestCategory, LabTest, TestRequest, TestResult

class TestCategoryForm(forms.ModelForm):
    class Meta:
        model = TestCategory
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class LabTestForm(forms.ModelForm):
    class Meta:
        model = LabTest
        fields = ['name', 'category', 'description', 'price', 
                 'preparation_instructions', 'report_delivery_time']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'preparation_instructions': forms.Textarea(attrs={'rows': 3}),
        }

class TestRequestForm(forms.ModelForm):
    class Meta:
        model = TestRequest
        fields = ['patient', 'test', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class TestResultForm(forms.ModelForm):
    class Meta:
        model = TestResult
        fields = ['result_value', 'reference_range', 'interpretation', 'remarks']
        widgets = {
            'result_value': forms.Textarea(attrs={'rows': 3}),
            'interpretation': forms.Textarea(attrs={'rows': 3}),
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }

class SampleCollectionForm(forms.ModelForm):
    class Meta:
        model = TestRequest
        fields = ['sample_collection_date', 'notes']
        widgets = {
            'sample_collection_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
