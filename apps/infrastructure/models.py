from django.db import models

class Building(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    floors = models.PositiveIntegerField()
    address = models.TextField()
    
    def __str__(self):
        return self.name

class Ward(models.Model):
    WARD_TYPES = [
        ('GENERAL', 'General Ward'),
        ('PRIVATE', 'Private Room'),
        ('ICU', 'Intensive Care Unit'),
        ('CCU', 'Critical Care Unit'),
        ('EMERGENCY', 'Emergency Ward'),
        ('OT', 'Operation Theater'),
    ]
    
    name = models.CharField(max_length=100)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    floor = models.PositiveIntegerField()
    ward_type = models.CharField(max_length=20, choices=WARD_TYPES)
    capacity = models.PositiveIntegerField()
    description = models.TextField()
    
    def __str__(self):
        return f"{self.name} - {self.ward_type}"

class Bed(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('OCCUPIED', 'Occupied'),
        ('MAINTENANCE', 'Under Maintenance'),
        ('RESERVED', 'Reserved'),
    ]
    
    bed_number = models.CharField(max_length=10)
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Bed {self.bed_number} - {self.ward.name}"

class Equipment(models.Model):
    EQUIPMENT_TYPES = [
        ('MEDICAL', 'Medical Equipment'),
        ('LAB', 'Laboratory Equipment'),
        ('IT', 'IT Equipment'),
        ('FURNITURE', 'Furniture'),
        ('OTHER', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    equipment_type = models.CharField(max_length=20, choices=EQUIPMENT_TYPES)
    serial_number = models.CharField(max_length=100, unique=True)
    manufacturer = models.CharField(max_length=200)
    purchase_date = models.DateField()
    warranty_expiry = models.DateField()
    last_maintenance = models.DateField()
    next_maintenance = models.DateField()
    location = models.ForeignKey(Ward, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.serial_number}"

class MaintenanceRecord(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    maintenance_date = models.DateField()
    performed_by = models.CharField(max_length=100)
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    next_maintenance = models.DateField()
    
    def __str__(self):
        return f"{self.equipment.name} - {self.maintenance_date}"
