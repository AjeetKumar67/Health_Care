from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.db.models import F, Sum
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Medicine, MedicineStock, Prescription, PrescriptionItem
from .forms import MedicineForm, MedicineStockForm, PrescriptionForm, PrescriptionItemForm
from apps.users.decorators import pharmacy_required

@login_required
@pharmacy_required
def pharmacy_dashboard(request):
    # Get today's date for filtering
    today = timezone.now().date()
    
    # Get summary statistics
    total_medicines = Medicine.objects.count()
    low_stock_medicines = Medicine.objects.filter(stock_quantity__lte=F('reorder_level')).count()
    pending_prescriptions = Prescription.objects.filter(status='PENDING').count()
    today_completed = Prescription.objects.filter(
        status='COMPLETED',
        prescribed_date__date=today
    ).count()
    
    # Get recent prescriptions
    recent_prescriptions = Prescription.objects.order_by('-prescribed_date')[:5]
    
    context = {
        'total_medicines': total_medicines,
        'low_stock_medicines': low_stock_medicines,
        'pending_prescriptions': pending_prescriptions,
        'today_completed': today_completed,
        'recent_prescriptions': recent_prescriptions,
    }
    return render(request, 'pharmacy/dashboard.html', context)

@login_required
@pharmacy_required
def medicine_list(request):
    medicines = Medicine.objects.all().order_by('name')
    paginator = Paginator(medicines, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'pharmacy/medicine_list.html', {'page_obj': page_obj})

@login_required
@pharmacy_required
def medicine_create(request):
    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medicine added successfully!')
            return redirect('pharmacy:medicine_list')
    else:
        form = MedicineForm()
    return render(request, 'pharmacy/medicine_form.html', {'form': form, 'title': 'Add New Medicine'})

@login_required
@pharmacy_required
def medicine_edit(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        form = MedicineForm(request.POST, instance=medicine)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medicine updated successfully!')
            return redirect('pharmacy:medicine_list')
    else:
        form = MedicineForm(instance=medicine)
    return render(request, 'pharmacy/medicine_form.html', {'form': form, 'title': 'Edit Medicine'})

@login_required
@pharmacy_required
def stock_list(request):
    stocks = MedicineStock.objects.all().order_by('-date_added')
    paginator = Paginator(stocks, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Add date context for expiry checking
    today = datetime.now().date()
    next_month = today + timedelta(days=30)
    
    context = {
        'page_obj': page_obj,
        'today': today,
        'next_month': next_month,
    }
    return render(request, 'pharmacy/stock_list.html', context)

@login_required
@pharmacy_required
def stock_add(request):
    if request.method == 'POST':
        form = MedicineStockForm(request.POST)
        if form.is_valid():
            stock = form.save()
            # Update medicine stock quantity
            medicine = stock.medicine
            medicine.stock_quantity += stock.quantity
            medicine.save()
            messages.success(request, 'Stock added successfully!')
            return redirect('pharmacy:stock_list')
    else:
        form = MedicineStockForm()
    return render(request, 'pharmacy/stock_form.html', {'form': form, 'title': 'Add Stock'})

@login_required
@pharmacy_required
def prescription_list(request):
    prescriptions = Prescription.objects.all().order_by('-prescribed_date')
    paginator = Paginator(prescriptions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'pharmacy/prescription_list.html', {'page_obj': page_obj})

@login_required
@pharmacy_required
def prescription_detail(request, prescription_id):
    prescription = get_object_or_404(Prescription, prescription_id=prescription_id)
    items = prescription.items.all()
    return render(request, 'pharmacy/prescription_detail.html', {
        'prescription': prescription,
        'items': items
    })

@login_required
@pharmacy_required
def prescription_create(request):
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.prescription_id = 'RX' + get_random_string(7, '0123456789')
            prescription.save()
            messages.success(request, 'Prescription created successfully!')
            return redirect('pharmacy:prescription_add_items', prescription_id=prescription.prescription_id)
    else:
        form = PrescriptionForm()
    return render(request, 'pharmacy/prescription_form.html', {'form': form, 'title': 'Create Prescription'})

@login_required
@pharmacy_required
def prescription_add_items(request, prescription_id):
    prescription = get_object_or_404(Prescription, prescription_id=prescription_id)
    if request.method == 'POST':
        form = PrescriptionItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.prescription = prescription
            item.save()
            messages.success(request, 'Medicine added to prescription!')
            return redirect('pharmacy:prescription_add_items', prescription_id=prescription_id)
    else:
        form = PrescriptionItemForm()
    
    items = prescription.items.all()
    return render(request, 'pharmacy/prescription_items.html', {
        'form': form,
        'prescription': prescription,
        'items': items
    })

@login_required
@pharmacy_required
def prescription_update_status(request, prescription_id):
    prescription = get_object_or_404(Prescription, prescription_id=prescription_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Prescription.STATUS_CHOICES):
            prescription.status = new_status
            prescription.save()
            messages.success(request, f'Prescription status updated to {new_status}')
        else:
            messages.error(request, 'Invalid status')
    return redirect('pharmacy:prescription_detail', prescription_id=prescription_id)
