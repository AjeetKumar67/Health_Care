from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils.crypto import get_random_string
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from .models import Category, Supplier, Item, PurchaseOrder, PurchaseOrderItem, StockTransaction
from .forms import (CategoryForm, SupplierForm, ItemForm, PurchaseOrderForm, 
                   PurchaseOrderItemForm, StockTransactionForm)
from apps.users.decorators import inventory_required

@login_required
@inventory_required
def inventory_dashboard(request):
    """Dashboard view for inventory staff"""
    # Get summary statistics
    total_items = Item.objects.count()
    low_stock_items = Item.objects.filter(current_stock__lte=F('minimum_stock')).count()
    active_suppliers = Supplier.objects.filter(is_active=True).count()
    pending_orders = PurchaseOrder.objects.filter(status='PENDING').count()
    
    # Get recent stock transactions
    recent_transactions = StockTransaction.objects.select_related(
        'item', 'performed_by'
    ).order_by('-transaction_date')[:5]
    
    # Get low stock items
    low_stock_items_list = Item.objects.filter(
        current_stock__lte=F('minimum_stock')
    ).select_related('category')[:5]
    
    # Get category statistics
    category_stats = Category.objects.annotate(
        item_count=Count('item')
    ).values('name', 'item_count')
    
    # Get recent purchase orders
    recent_orders = PurchaseOrder.objects.select_related(
        'supplier', 'ordered_by'
    ).order_by('-created_at')[:5]
    
    context = {
        'total_items': total_items,
        'low_stock_items': low_stock_items,
        'active_suppliers': active_suppliers,
        'pending_orders': pending_orders,
        'recent_transactions': recent_transactions,
        'low_stock_items_list': low_stock_items_list,
        'category_stats': category_stats,
        'recent_orders': recent_orders,
    }
    return render(request, 'inventory/dashboard.html', context)

@login_required
@inventory_required
def item_list(request):
    """View list of inventory items"""
    category_filter = request.GET.get('category', '')
    search_query = request.GET.get('search', '')
    stock_filter = request.GET.get('stock', '')
    
    items = Item.objects.select_related('category')
    
    if category_filter:
        items = items.filter(category_id=category_filter)
    
    if search_query:
        items = items.filter(
            Q(name__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    if stock_filter == 'low':
        items = items.filter(current_stock__lte=F('minimum_stock'))
    
    items = items.order_by('category', 'name')
    paginator = Paginator(items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'category_filter': category_filter,
        'search_query': search_query,
        'stock_filter': stock_filter,
    }
    return render(request, 'inventory/item_list.html', context)

@login_required
@inventory_required
def item_create(request):
    """Create new inventory item"""
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item created successfully!')
            return redirect('inventory:item_list')
    else:
        form = ItemForm()
    
    return render(request, 'inventory/item_form.html', {
        'form': form,
        'title': 'Add New Item'
    })

@login_required
@inventory_required
def item_edit(request, pk):
    """Edit existing inventory item"""
    item = get_object_or_404(Item, pk=pk)
    
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item updated successfully!')
            return redirect('inventory:item_list')
    else:
        form = ItemForm(instance=item)
    
    return render(request, 'inventory/item_form.html', {
        'form': form,
        'title': 'Edit Item',
        'item': item
    })

@login_required
@inventory_required
def supplier_list(request):
    """View list of suppliers"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    suppliers = Supplier.objects.all()
    
    if search_query:
        suppliers = suppliers.filter(
            Q(name__icontains=search_query) |
            Q(contact_person__icontains=search_query)
        )
    
    if status_filter:
        is_active = status_filter == 'active'
        suppliers = suppliers.filter(is_active=is_active)
    
    suppliers = suppliers.order_by('name')
    paginator = Paginator(suppliers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'inventory/supplier_list.html', context)

@login_required
@inventory_required
def supplier_create(request):
    """Create new supplier"""
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier created successfully!')
            return redirect('inventory:supplier_list')
    else:
        form = SupplierForm()
    
    return render(request, 'inventory/supplier_form.html', {
        'form': form,
        'title': 'Add New Supplier'
    })

@login_required
@inventory_required
def supplier_edit(request, pk):
    """Edit existing supplier"""
    supplier = get_object_or_404(Supplier, pk=pk)
    
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier updated successfully!')
            return redirect('inventory:supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    
    return render(request, 'inventory/supplier_form.html', {
        'form': form,
        'title': 'Edit Supplier',
        'supplier': supplier
    })

@login_required
@inventory_required
def category_list(request):
    """View list of item categories"""
    categories = Category.objects.annotate(
        item_count=Count('item')
    ).order_by('name')
    
    return render(request, 'inventory/category_list.html', {
        'categories': categories
    })

@login_required
@inventory_required
def category_create(request):
    """Create new item category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('inventory:category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'inventory/category_form.html', {
        'form': form,
        'title': 'Add New Category'
    })

@login_required
@inventory_required
def category_edit(request, pk):
    """Edit existing item category"""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('inventory:category_list')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'inventory/category_form.html', {
        'form': form,
        'title': 'Edit Category',
        'category': category
    })

@login_required
@inventory_required
def purchase_order_list(request):
    """View list of purchase orders"""
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    orders = PurchaseOrder.objects.select_related('supplier', 'ordered_by')
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(supplier__name__icontains=search_query)
        )
    
    orders = orders.order_by('-created_at')
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    return render(request, 'inventory/purchase_order_list.html', context)

@login_required
@inventory_required
def purchase_order_detail(request, order_number):
    """View purchase order details"""
    purchase_order = get_object_or_404(PurchaseOrder, order_number=order_number)
    order_items = PurchaseOrderItem.objects.filter(
        purchase_order=purchase_order
    ).select_related('item')
    
    context = {
        'purchase_order': purchase_order,
        'order_items': order_items,
    }
    return render(request, 'inventory/purchase_order_detail.html', context)

@login_required
@inventory_required
def purchase_order_create(request):
    """Create new purchase order"""
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.ordered_by = request.user
            order.save()
            messages.success(request, 'Purchase order created successfully!')
            return redirect('inventory:purchase_order_detail', order_number=order.order_number)
    else:
        # Generate unique order number
        order_number = f'PO{get_random_string(6).upper()}'
        form = PurchaseOrderForm(initial={'order_number': order_number})
    
    return render(request, 'inventory/purchase_order_form.html', {
        'form': form,
        'title': 'Create Purchase Order'
    })

@login_required
@inventory_required
def transaction_list(request):
    """View list of stock transactions"""
    type_filter = request.GET.get('type', '')
    search_query = request.GET.get('search', '')
    
    transactions = StockTransaction.objects.select_related('item', 'performed_by')
    
    if type_filter:
        transactions = transactions.filter(transaction_type=type_filter)
    
    if search_query:
        transactions = transactions.filter(
            Q(transaction_id__icontains=search_query) |
            Q(item__name__icontains=search_query)
        )
    
    transactions = transactions.order_by('-transaction_date')
    paginator = Paginator(transactions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'type_filter': type_filter,
        'search_query': search_query,
    }
    return render(request, 'inventory/transaction_list.html', context)

@login_required
@inventory_required
def transaction_create(request):
    """Create new stock transaction"""
    if request.method == 'POST':
        form = StockTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.transaction_id = f'TRX{get_random_string(6).upper()}'
            transaction.performed_by = request.user
            
            # Update item stock
            item = transaction.item
            if transaction.transaction_type in ['IN', 'RETURN']:
                item.current_stock += transaction.quantity
            else:  # OUT or ADJUSTMENT
                item.current_stock -= transaction.quantity
            item.save()
            
            transaction.save()
            messages.success(request, 'Stock transaction recorded successfully!')
            return redirect('inventory:transaction_list')
    else:
        form = StockTransactionForm()
    
    return render(request, 'inventory/transaction_form.html', {
        'form': form,
        'title': 'New Stock Transaction'
    })
