from django.contrib import admin
from .models import Invoice, InvoiceItem, Payment

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'patient', 'date_generated', 'due_date', 'final_amount', 'status']
    list_filter = ['status', 'date_generated']
    search_fields = ['invoice_number', 'patient__user__first_name', 'patient__user__last_name']
    inlines = [InvoiceItemInline, PaymentInline]

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'invoice', 'amount', 'payment_method', 'payment_date']
    list_filter = ['payment_method', 'payment_date']
    search_fields = ['payment_id', 'invoice__invoice_number', 'transaction_id']
