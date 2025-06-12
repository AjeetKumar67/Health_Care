from django.db import models
from apps.users.models import User

# Create your models here.
class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    def __str__(self):
        return self.name

class Staff(models.Model):
    STAFF_TYPES = [
        ('DOCTOR', 'Doctor'),
        ('NURSE', 'Nurse'),
        ('ADMIN', 'Administrative Staff'),
        ('LAB', 'Laboratory Staff'),
        ('PHARMACY', 'Pharmacy Staff'),
    ]
    
    staff_id = models.CharField(max_length=10, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    staff_type = models.CharField(max_length=20, choices=STAFF_TYPES)
    specialization = models.CharField(max_length=100, blank=True)
    qualification = models.CharField(max_length=200)
    experience_years = models.PositiveIntegerField()
    joining_date = models.DateField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.staff_id} - {self.user.get_full_name()}"

class Doctor(Staff):
    license_number = models.CharField(max_length=50, unique=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    available_days = models.CharField(max_length=100)  # Store as comma-separated days
    available_times = models.CharField(max_length=100)  # Store as comma-separated time slots

    def save(self, *args, **kwargs):
        if not self.pk:
            self.staff_type = 'DOCTOR'
        super().save(*args, **kwargs)

class Schedule(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    day = models.CharField(max_length=10)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.staff.user.get_full_name()} - {self.day}"
