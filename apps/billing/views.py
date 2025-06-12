from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.db.models import Sum, F, Count, Q
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Invoice, InvoiceItem, Payment
from .forms import InvoiceForm, InvoiceItemForm, PaymentForm
from apps.patients.models import Patient
from apps.users.decorators import staff_required

@login_required
@staff_required
def billing_dashboard(request):
    """Dashboard view for billing management"""
    total_invoices = Invoice.objects.count()
    pending_invoices = Invoice.objects.filter(status='PENDING').count()
    total_revenue = Payment.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    recent_invoices = Invoice.objects.order_by('-date_generated')[:5]
    recent_payments = Payment.objects.order_by('-payment_date')[:5]
    
    # Payment statistics
    payment_stats = Payment.objects.values('payment_method')\
        .annotate(total=Sum('amount'))\
        .order_by('-total')
    
    # Status statistics
    status_stats = Invoice.objects.values('status')\
        .annotate(count=Count('id'))\
        .order_by('-count')
    
    context = {
        'total_invoices': total_invoices,
        'pending_invoices': pending_invoices,
        'total_revenue': total_revenue,
        'recent_invoices': recent_invoices,
        'recent_payments': recent_payments,
        'payment_stats': payment_stats,
        'status_stats': status_stats,
    }
    
    return render(request, 'billing/dashboard.html', context)

@login_required
@staff_required
def invoice_list(request):
    """View list of invoices"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    invoices = Invoice.objects.select_related('patient__user').order_by('-date_generated')
    
    if search_query:
        invoices = invoices.filter(
            Q(invoice_number__icontains=search_query) |
            Q(patient__user__first_name__icontains=search_query) |
            Q(patient__user__last_name__icontains=search_query)
        )
    
    if status_filter:
        invoices = invoices.filter(status=status_filter)
    
    paginator = Paginator(invoices, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'billing/invoice_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': Invoice.PAYMENT_STATUS,
    })

@login_required
@staff_required
def invoice_create(request):
    """Create new invoice"""
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.invoice_number = 'INV' + get_random_string(7, '0123456789')
            invoice.date_generated = timezone.now()
            
            # Calculate final amount
            total = invoice.total_amount or 0
            discount = invoice.discount or 0
            tax = invoice.tax or 0
            invoice.final_amount = total - discount + tax
            
            invoice.save()
            messages.success(request, 'Invoice created successfully!')
            return redirect('billing:invoice_add_items', invoice_number=invoice.invoice_number)
    else:
        form = InvoiceForm()
    
    return render(request, 'billing/invoice_form.html', {
        'form': form,
        'title': 'Create New Invoice'
    })

@login_required
@staff_required
def invoice_detail(request, invoice_number):
    """View invoice details"""
    invoice = get_object_or_404(Invoice, invoice_number=invoice_number)
    items = invoice.items.all()
    payments = invoice.payments.all().order_by('-payment_date')
    
    # Calculate total paid amount
    total_paid = payments.aggregate(Sum('amount'))['amount__sum'] or 0
    remaining_amount = invoice.final_amount - total_paid
    
    # Show payment form if invoice is not fully paid
    payment_form = None
    if invoice.status in ['PENDING', 'PARTIAL'] and remaining_amount > 0:
        payment_form = PaymentForm(invoice=invoice)
    
    context = {
        'invoice': invoice,
        'items': items,
        'payments': payments,
        'total_paid': total_paid,
        'remaining_amount': remaining_amount,
        'payment_form': payment_form,
    }
    
    return render(request, 'billing/invoice_detail.html', context)

@login_required
@staff_required
def invoice_add_items(request, invoice_number):
    """Add items to invoice"""
    invoice = get_object_or_404(Invoice, invoice_number=invoice_number)
    
    if request.method == 'POST':
        form = InvoiceItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.invoice = invoice
            item.save()
            
            # Update invoice total
            total_amount = invoice.items.aggregate(
                total=Sum(F('quantity') * F('unit_price')))['total'] or 0
            invoice.total_amount = total_amount
            invoice.final_amount = total_amount - invoice.discount + invoice.tax
            invoice.save()
            
            messages.success(request, 'Item added successfully!')
            return redirect('billing:invoice_add_items', invoice_number=invoice_number)
    else:
        form = InvoiceItemForm()
    
    items = invoice.items.all()
    return render(request, 'billing/invoice_add_items.html', {
        'form': form,
        'invoice': invoice,
        'items': items,
    })

@login_required
@staff_required
def payment_create(request, invoice_number):
    """Record payment for invoice"""
    invoice = get_object_or_404(Invoice, invoice_number=invoice_number)
    
    if invoice.status == 'PAID':
        messages.error(request, 'This invoice is already paid.')
        return redirect('billing:invoice_detail', invoice_number=invoice_number)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, invoice=invoice)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.invoice = invoice
            payment.payment_id = 'PAY' + get_random_string(7, '0123456789')
            payment.save()
            
            # Update invoice status
            total_paid = invoice.payments.aggregate(Sum('amount'))['amount__sum'] or 0
            if total_paid >= invoice.final_amount:
                invoice.status = 'PAID'
            elif total_paid > 0:
                invoice.status = 'PARTIAL'
            invoice.save()
            
            messages.success(request, 'Payment recorded successfully!')
            return redirect('billing:invoice_detail', invoice_number=invoice_number)
    else:
        form = PaymentForm(invoice=invoice)
    
    return render(request, 'billing/payment_form.html', {
        'form': form,
        'invoice': invoice,
        'title': 'Record Payment'
    })
