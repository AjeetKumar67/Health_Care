from django.db import models
from apps.patients.models import Patient
from apps.appointments.models import Appointment
from apps.lab.models import TestRequest
from apps.pharmacy.models import Prescription

class Invoice(models.Model):
    PAYMENT_STATUS = [
        ('PENDING', 'Pending'),
        ('PARTIAL', 'Partially Paid'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    invoice_number = models.CharField(max_length=10, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date_generated = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='PENDING')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.patient.user.get_full_name()}"

class InvoiceItem(models.Model):
    ITEM_TYPES = [
        ('APPOINTMENT', 'Doctor Appointment'),
        ('LAB_TEST', 'Laboratory Test'),
        ('MEDICINE', 'Medicine'),
        ('OTHER', 'Other Services'),
    ]
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES)
    description = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    test_request = models.ForeignKey(TestRequest, on_delete=models.SET_NULL, null=True, blank=True)
    prescription = models.ForeignKey(Prescription, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.description} - {self.total_price}"

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('CASH', 'Cash'),
        ('CARD', 'Credit/Debit Card'),
        ('UPI', 'UPI'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('INSURANCE', 'Insurance'),
    ]
    
    payment_id = models.CharField(max_length=10, unique=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Payment {self.payment_id} for Invoice {self.invoice.invoice_number}"
