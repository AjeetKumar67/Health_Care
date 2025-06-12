from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import Building, Ward, Bed, Equipment, MaintenanceRecord
from .forms import (BuildingForm, WardForm, BedForm, EquipmentForm,
                   MaintenanceRecordForm)
from apps.users.decorators import staff_required

@login_required
@staff_required
def infrastructure_dashboard(request):
    """Dashboard view for infrastructure management"""
    # Get summary statistics
    total_buildings = Building.objects.count()
    total_wards = Ward.objects.count()
    available_beds = Bed.objects.filter(status='AVAILABLE', is_active=True).count()
    maintenance_due = Equipment.objects.filter(
        next_maintenance__lte=timezone.now().date()
    ).count()
    
    # Get ward occupancy stats
    wards = Ward.objects.annotate(
        total_beds=Count('bed'),
        available_beds=Count('bed', filter=Q(bed__status='AVAILABLE')),
    )
    
    # Get equipment needing maintenance
    equipment_due_maintenance = Equipment.objects.filter(
        next_maintenance__lte=timezone.now().date() + timedelta(days=7)
    ).select_related('location')[:5]
    
    # Get recent maintenance records
    recent_maintenance = MaintenanceRecord.objects.select_related(
        'equipment'
    ).order_by('-maintenance_date')[:5]
    
    context = {
        'total_buildings': total_buildings,
        'total_wards': total_wards,
        'available_beds': available_beds,
        'maintenance_due': maintenance_due,
        'wards': wards,
        'equipment_due_maintenance': equipment_due_maintenance,
        'recent_maintenance': recent_maintenance,
    }
    return render(request, 'infrastructure/dashboard.html', context)

# Building Views
@login_required
@staff_required
def building_list(request):
    """View list of buildings"""
    search_query = request.GET.get('search', '')
    buildings = Building.objects.annotate(ward_count=Count('ward'))
    
    if search_query:
        buildings = buildings.filter(
            Q(name__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    
    buildings = buildings.order_by('name')
    paginator = Paginator(buildings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'infrastructure/building_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
    })

@login_required
@staff_required
def building_create(request):
    """Create new building"""
    if request.method == 'POST':
        form = BuildingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Building created successfully!')
            return redirect('infrastructure:building_list')
    else:
        form = BuildingForm()
    
    return render(request, 'infrastructure/building_form.html', {
        'form': form,
        'title': 'Add New Building'
    })

@login_required
@staff_required
def building_detail(request, pk):
    """View building details"""
    building = get_object_or_404(Building, pk=pk)
    wards = Ward.objects.filter(building=building).annotate(
        total_beds=Count('bed'),
        available_beds=Count('bed', filter=Q(bed__status='AVAILABLE')),
    )
    
    return render(request, 'infrastructure/building_detail.html', {
        'building': building,
        'wards': wards,
    })

@login_required
@staff_required
def building_edit(request, pk):
    """Edit existing building"""
    building = get_object_or_404(Building, pk=pk)
    
    if request.method == 'POST':
        form = BuildingForm(request.POST, instance=building)
        if form.is_valid():
            form.save()
            messages.success(request, 'Building updated successfully!')
            return redirect('infrastructure:building_detail', pk=pk)
    else:
        form = BuildingForm(instance=building)
    
    return render(request, 'infrastructure/building_form.html', {
        'form': form,
        'title': 'Edit Building',
        'building': building
    })

# Ward Views
@login_required
@staff_required
def ward_list(request):
    """View list of wards"""
    building_filter = request.GET.get('building', '')
    type_filter = request.GET.get('type', '')
    search_query = request.GET.get('search', '')
    
    wards = Ward.objects.select_related('building').annotate(
        total_beds=Count('bed'),
        available_beds=Count('bed', filter=Q(bed__status='AVAILABLE')),
    )
    
    if building_filter:
        wards = wards.filter(building_id=building_filter)
    
    if type_filter:
        wards = wards.filter(ward_type=type_filter)
    
    if search_query:
        wards = wards.filter(
            Q(name__icontains=search_query) |
            Q(building__name__icontains=search_query)
        )
    
    wards = wards.order_by('building', 'name')
    paginator = Paginator(wards, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    buildings = Building.objects.all()
    
    context = {
        'page_obj': page_obj,
        'buildings': buildings,
        'building_filter': building_filter,
        'type_filter': type_filter,
        'search_query': search_query,
        'ward_types': Ward.WARD_TYPES,
    }
    return render(request, 'infrastructure/ward_list.html', context)

@login_required
@staff_required
def ward_create(request):
    """Create new ward"""
    if request.method == 'POST':
        form = WardForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ward created successfully!')
            return redirect('infrastructure:ward_list')
    else:
        form = WardForm()
    
    return render(request, 'infrastructure/ward_form.html', {
        'form': form,
        'title': 'Add New Ward'
    })

@login_required
@staff_required
def ward_detail(request, pk):
    """View ward details"""
    ward = get_object_or_404(Ward, pk=pk)
    beds = Bed.objects.filter(ward=ward)
    equipment = Equipment.objects.filter(location=ward)
    
    context = {
        'ward': ward,
        'beds': beds,
        'equipment': equipment,
    }
    return render(request, 'infrastructure/ward_detail.html', context)

@login_required
@staff_required
def ward_edit(request, pk):
    """Edit existing ward"""
    ward = get_object_or_404(Ward, pk=pk)
    
    if request.method == 'POST':
        form = WardForm(request.POST, instance=ward)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ward updated successfully!')
            return redirect('infrastructure:ward_detail', pk=pk)
    else:
        form = WardForm(instance=ward)
    
    return render(request, 'infrastructure/ward_form.html', {
        'form': form,
        'title': 'Edit Ward',
        'ward': ward
    })

# Bed Views
@login_required
@staff_required
def bed_list(request):
    """View list of beds"""
    ward_filter = request.GET.get('ward', '')
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    beds = Bed.objects.select_related('ward', 'ward__building')
    
    if ward_filter:
        beds = beds.filter(ward_id=ward_filter)
    
    if status_filter:
        beds = beds.filter(status=status_filter)
    
    if search_query:
        beds = beds.filter(
            Q(bed_number__icontains=search_query) |
            Q(ward__name__icontains=search_query)
        )
    
    beds = beds.order_by('ward', 'bed_number')
    paginator = Paginator(beds, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    wards = Ward.objects.all()
    
    context = {
        'page_obj': page_obj,
        'wards': wards,
        'ward_filter': ward_filter,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': Bed.STATUS_CHOICES,
    }
    return render(request, 'infrastructure/bed_list.html', context)

@login_required
@staff_required
def bed_create(request):
    """Create new bed"""
    if request.method == 'POST':
        form = BedForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bed created successfully!')
            return redirect('infrastructure:bed_list')
    else:
        form = BedForm()
    
    return render(request, 'infrastructure/bed_form.html', {
        'form': form,
        'title': 'Add New Bed'
    })

@login_required
@staff_required
def bed_edit(request, pk):
    """Edit existing bed"""
    bed = get_object_or_404(Bed, pk=pk)
    
    if request.method == 'POST':
        form = BedForm(request.POST, instance=bed)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bed updated successfully!')
            return redirect('infrastructure:bed_list')
    else:
        form = BedForm(instance=bed)
    
    return render(request, 'infrastructure/bed_form.html', {
        'form': form,
        'title': 'Edit Bed',
        'bed': bed
    })

# Equipment Views
@login_required
@staff_required
def equipment_list(request):
    """View list of equipment"""
    type_filter = request.GET.get('type', '')
    location_filter = request.GET.get('location', '')
    search_query = request.GET.get('search', '')
    
    equipment = Equipment.objects.select_related('location', 'location__building')
    
    if type_filter:
        equipment = equipment.filter(equipment_type=type_filter)
    
    if location_filter:
        equipment = equipment.filter(location_id=location_filter)
    
    if search_query:
        equipment = equipment.filter(
            Q(name__icontains=search_query) |
            Q(serial_number__icontains=search_query) |
            Q(manufacturer__icontains=search_query)
        )
    
    equipment = equipment.order_by('name')
    paginator = Paginator(equipment, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    wards = Ward.objects.all()
    
    context = {
        'page_obj': page_obj,
        'wards': wards,
        'type_filter': type_filter,
        'location_filter': location_filter,
        'search_query': search_query,
        'equipment_types': Equipment.EQUIPMENT_TYPES,
    }
    return render(request, 'infrastructure/equipment_list.html', context)

@login_required
@staff_required
def equipment_create(request):
    """Create new equipment"""
    if request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipment created successfully!')
            return redirect('infrastructure:equipment_list')
    else:
        form = EquipmentForm()
    
    return render(request, 'infrastructure/equipment_form.html', {
        'form': form,
        'title': 'Add New Equipment'
    })

@login_required
@staff_required
def equipment_detail(request, pk):
    """View equipment details"""
    equipment = get_object_or_404(Equipment, pk=pk)
    maintenance_records = MaintenanceRecord.objects.filter(
        equipment=equipment
    ).order_by('-maintenance_date')
    
    context = {
        'equipment': equipment,
        'maintenance_records': maintenance_records,
    }
    return render(request, 'infrastructure/equipment_detail.html', context)

@login_required
@staff_required
def equipment_edit(request, pk):
    """Edit existing equipment"""
    equipment = get_object_or_404(Equipment, pk=pk)
    
    if request.method == 'POST':
        form = EquipmentForm(request.POST, instance=equipment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipment updated successfully!')
            return redirect('infrastructure:equipment_detail', pk=pk)
    else:
        form = EquipmentForm(instance=equipment)
    
    return render(request, 'infrastructure/equipment_form.html', {
        'form': form,
        'title': 'Edit Equipment',
        'equipment': equipment
    })

# Maintenance Record Views
@login_required
@staff_required
def maintenance_list(request):
    """View list of maintenance records"""
    equipment_filter = request.GET.get('equipment', '')
    search_query = request.GET.get('search', '')
    
    records = MaintenanceRecord.objects.select_related('equipment')
    
    if equipment_filter:
        records = records.filter(equipment_id=equipment_filter)
    
    if search_query:
        records = records.filter(
            Q(equipment__name__icontains=search_query) |
            Q(performed_by__icontains=search_query)
        )
    
    records = records.order_by('-maintenance_date')
    paginator = Paginator(records, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    equipment = Equipment.objects.all()
    
    context = {
        'page_obj': page_obj,
        'equipment': equipment,
        'equipment_filter': equipment_filter,
        'search_query': search_query,
    }
    return render(request, 'infrastructure/maintenance_list.html', context)

@login_required
@staff_required
def maintenance_create(request):
    """Create new maintenance record"""
    if request.method == 'POST':
        form = MaintenanceRecordForm(request.POST)
        if form.is_valid():
            record = form.save()
            # Update equipment's last and next maintenance dates
            equipment = record.equipment
            equipment.last_maintenance = record.maintenance_date
            equipment.next_maintenance = record.next_maintenance
            equipment.save()
            messages.success(request, 'Maintenance record created successfully!')
            return redirect('infrastructure:maintenance_list')
    else:
        # Pre-select equipment if provided in URL
        equipment_id = request.GET.get('equipment')
        initial = {'equipment': equipment_id} if equipment_id else {}
        form = MaintenanceRecordForm(initial=initial)
    
    return render(request, 'infrastructure/maintenance_form.html', {
        'form': form,
        'title': 'Add Maintenance Record'
    })
