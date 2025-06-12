from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.db.models import Count, Q
from .models import TestCategory, LabTest, TestRequest, TestResult
from .forms import (TestCategoryForm, LabTestForm, TestRequestForm, 
                   TestResultForm, SampleCollectionForm)
from apps.users.decorators import lab_required

@login_required
@lab_required
def lab_dashboard(request):
    """Dashboard view for lab staff"""
    # Get summary statistics
    total_requests = TestRequest.objects.count()
    pending_samples = TestRequest.objects.filter(status='REQUESTED').count()
    in_progress = TestRequest.objects.filter(status='IN_PROGRESS').count()
    completed_today = TestRequest.objects.filter(
        status='COMPLETED',
        result_date__date=timezone.now().date()
    ).count()
    
    # Get test requests by status
    status_stats = TestRequest.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Get recent test requests
    recent_requests = TestRequest.objects.select_related(
        'patient', 'test', 'technician'
    ).order_by('-requested_date')[:5]
    
    context = {
        'total_requests': total_requests,
        'pending_samples': pending_samples,
        'in_progress': in_progress,
        'completed_today': completed_today,
        'status_stats': status_stats,
        'recent_requests': recent_requests,
        'recent_requests': recent_requests,
    }
    return render(request, 'lab/dashboard.html', context)

@login_required
@lab_required
def test_request_list(request):
    """View for listing all test requests"""
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    requests = TestRequest.objects.select_related('patient', 'test', 'technician')
    
    if status_filter:
        requests = requests.filter(status=status_filter)
    
    if search_query:
        requests = requests.filter(
            Q(request_id__icontains=search_query) |
            Q(patient__user__first_name__icontains=search_query) |
            Q(patient__user__last_name__icontains=search_query) |
            Q(test__name__icontains=search_query)
        )
    
    requests = requests.order_by('-requested_date')
    paginator = Paginator(requests, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    return render(request, 'lab/test_request_list.html', context)

@login_required
@lab_required
def test_request_detail(request, request_id):
    """View test request details"""
    test_request = get_object_or_404(TestRequest, request_id=request_id)
    test_result = TestResult.objects.filter(test_request=test_request).first()
    
    context = {
        'test_request': test_request,
        'test_result': test_result,
    }
    return render(request, 'lab/test_request_detail.html', context)

@login_required
@lab_required
def test_request_create(request):
    """Create new test request"""
    if request.method == 'POST':
        form = TestRequestForm(request.POST)
        if form.is_valid():
            test_request = form.save(commit=False)
            test_request.request_id = 'LAB' + get_random_string(7, '0123456789')
            test_request.requested_by = request.user
            test_request.save()
            messages.success(request, 'Test request created successfully!')
            return redirect('lab:test_request_detail', request_id=test_request.request_id)
    else:
        form = TestRequestForm()
    
    return render(request, 'lab/test_request_form.html', {
        'form': form,
        'title': 'Create Test Request'
    })

@login_required
@lab_required
def collect_sample(request, request_id):
    """Mark sample as collected and update test request"""
    test_request = get_object_or_404(TestRequest, request_id=request_id)
    
    if request.method == 'POST':
        form = SampleCollectionForm(request.POST, instance=test_request)
        if form.is_valid():
            test_request = form.save(commit=False)
            test_request.status = 'SAMPLE_COLLECTED'
            test_request.save()
            messages.success(request, 'Sample collection recorded successfully!')
            return redirect('lab:test_request_detail', request_id=request_id)
    else:
        form = SampleCollectionForm(instance=test_request)
    
    return render(request, 'lab/sample_collection_form.html', {
        'form': form,
        'test_request': test_request
    })

@login_required
@lab_required
def enter_test_result(request, request_id):
    """Enter test results"""
    test_request = get_object_or_404(TestRequest, request_id=request_id)
    test_result = TestResult.objects.filter(test_request=test_request).first()
    
    if request.method == 'POST':
        form = TestResultForm(request.POST, instance=test_result)
        if form.is_valid():
            result = form.save(commit=False)
            result.test_request = test_request
            result.performed_by = request.user
            result.save()
            
            test_request.status = 'COMPLETED'
            test_request.result_date = timezone.now()
            test_request.save()
            
            messages.success(request, 'Test results entered successfully!')
            return redirect('lab:test_request_detail', request_id=request_id)
    else:
        form = TestResultForm(instance=test_result)
    
    return render(request, 'lab/test_result_form.html', {
        'form': form,
        'test_request': test_request
    })

@login_required
@lab_required
def update_test_status(request, request_id):
    """Update test request status"""
    test_request = get_object_or_404(TestRequest, request_id=request_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(TestRequest.STATUS_CHOICES):
            test_request.status = new_status
            test_request.save()
            messages.success(request, 'Status updated successfully!')
        else:
            messages.error(request, 'Invalid status!')
    
    return redirect('lab:test_request_detail', request_id=request_id)

@login_required
@lab_required
def lab_test_list(request):
    """View list of available lab tests"""
    category_filter = request.GET.get('category', '')
    search_query = request.GET.get('search', '')
    
    tests = LabTest.objects.select_related('category')
    
    if category_filter:
        tests = tests.filter(category_id=category_filter)
    
    if search_query:
        tests = tests.filter(
            Q(name__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    tests = tests.order_by('category', 'name')
    paginator = Paginator(tests, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = TestCategory.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'category_filter': category_filter,
        'search_query': search_query,
    }
    return render(request, 'lab/lab_test_list.html', context)

@login_required
@lab_required
def lab_test_create(request):
    """Create new lab test"""
    if request.method == 'POST':
        form = LabTestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lab test created successfully!')
            return redirect('lab:lab_test_list')
    else:
        form = LabTestForm()
    
    return render(request, 'lab/lab_test_form.html', {
        'form': form,
        'title': 'Add New Lab Test'
    })

@login_required
@lab_required
def lab_test_edit(request, pk):
    """Edit existing lab test"""
    lab_test = get_object_or_404(LabTest, pk=pk)
    
    if request.method == 'POST':
        form = LabTestForm(request.POST, instance=lab_test)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lab test updated successfully!')
            return redirect('lab:lab_test_list')
    else:
        form = LabTestForm(instance=lab_test)
    
    return render(request, 'lab/lab_test_form.html', {
        'form': form,
        'title': 'Edit Lab Test',
        'lab_test': lab_test
    })

@login_required
@lab_required
def test_category_list(request):
    """View list of test categories"""
    categories = TestCategory.objects.annotate(
        test_count=Count('labtest')
    ).order_by('name')
    
    return render(request, 'lab/test_category_list.html', {
        'categories': categories
    })

@login_required
@lab_required
def test_category_create(request):
    """Create new test category"""
    if request.method == 'POST':
        form = TestCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Test category created successfully!')
            return redirect('lab:test_category_list')
    else:
        form = TestCategoryForm()
    
    return render(request, 'lab/test_category_form.html', {
        'form': form,
        'title': 'Add New Test Category'
    })

@login_required
@lab_required
def test_category_edit(request, pk):
    """Edit existing test category"""
    category = get_object_or_404(TestCategory, pk=pk)
    
    if request.method == 'POST':
        form = TestCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Test category updated successfully!')
            return redirect('lab:test_category_list')
    else:
        form = TestCategoryForm(instance=category)
    
    return render(request, 'lab/test_category_form.html', {
        'form': form,
        'title': 'Edit Test Category',
        'category': category
    })
