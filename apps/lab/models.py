from django.db import models
from apps.patients.models import Patient
from apps.staff.models import Staff

class TestCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    def __str__(self):
        return self.name

class LabTest(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(TestCategory, on_delete=models.CASCADE)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    preparation_instructions = models.TextField()
    report_delivery_time = models.PositiveIntegerField()  # in hours
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class TestRequest(models.Model):
    STATUS_CHOICES = [
        ('REQUESTED', 'Requested'),
        ('SAMPLE_COLLECTED', 'Sample Collected'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    request_id = models.CharField(max_length=10, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    test = models.ForeignKey(LabTest, on_delete=models.CASCADE)
    requested_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='requested_tests')
    technician = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='assigned_tests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='REQUESTED')
    requested_date = models.DateTimeField(auto_now_add=True)
    sample_collection_date = models.DateTimeField(null=True, blank=True)
    result_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.request_id} - {self.patient.user.get_full_name()} - {self.test.name}"

class TestResult(models.Model):
    test_request = models.OneToOneField(TestRequest, on_delete=models.CASCADE)
    result_value = models.TextField()
    reference_range = models.CharField(max_length=100)
    interpretation = models.TextField()
    remarks = models.TextField(blank=True)
    performed_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Result for {self.test_request.request_id}"
