from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.db.models import Count, Q
from .models import SupportCategory, SupportTicket, TicketResponse, Feedback, FAQ
from .forms import (CategoryForm, TicketForm, TicketResponseForm, TicketUpdateForm,
                   FeedbackForm, FeedbackResolutionForm, FAQForm)
from apps.users.decorators import staff_required

@login_required
def support_dashboard(request):
    """Support system dashboard view"""
    context = {
        'total_tickets': SupportTicket.objects.count(),
        'open_tickets': SupportTicket.objects.exclude(status__in=['RESOLVED', 'CLOSED']).count(),
        'my_tickets': SupportTicket.objects.filter(raised_by=request.user).count(),
        'recent_tickets': SupportTicket.objects.order_by('-created_at')[:5],
        'recent_feedback': Feedback.objects.order_by('-created_at')[:5],
        'feedback_count': Feedback.objects.count(),
        'unresolved_feedback': Feedback.objects.filter(is_resolved=False).count(),
        'categories': SupportCategory.objects.annotate(ticket_count=Count('supportticket')),
    }
    return render(request, 'support/dashboard.html', context)

@login_required
def ticket_list(request):
    """View list of support tickets"""
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    search_query = request.GET.get('search', '')
    
    tickets = SupportTicket.objects.select_related('category', 'raised_by', 'assigned_to')
    
    # Filter by user role
    if not request.user.is_staff:
        tickets = tickets.filter(raised_by=request.user)
    
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    if category_filter:
        tickets = tickets.filter(category_id=category_filter)
    if search_query:
        tickets = tickets.filter(
            Q(ticket_id__icontains=search_query) |
            Q(subject__icontains=search_query) |
            Q(raised_by__first_name__icontains=search_query) |
            Q(raised_by__last_name__icontains=search_query)
        )
    
    tickets = tickets.order_by('-created_at')
    paginator = Paginator(tickets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'search_query': search_query,
        'status_choices': SupportTicket.STATUS_CHOICES,
        'categories': SupportCategory.objects.all(),
    }
    return render(request, 'support/ticket_list.html', context)

@login_required
def ticket_create(request):
    """Create new support ticket"""
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.ticket_id = 'TKT' + get_random_string(7, '0123456789')
            ticket.raised_by = request.user
            ticket.save()
            messages.success(request, 'Support ticket created successfully!')
            return redirect('support:ticket_detail', ticket_id=ticket.ticket_id)
    else:
        form = TicketForm()
    
    return render(request, 'support/ticket_form.html', {
        'form': form,
        'title': 'Create Support Ticket'
    })

@login_required
def ticket_detail(request, ticket_id):
    """View support ticket details"""
    ticket = get_object_or_404(
        SupportTicket.objects.select_related('category', 'raised_by', 'assigned_to'),
        ticket_id=ticket_id
    )
    
    # Check if user has access
    if not request.user.is_staff and request.user != ticket.raised_by:
        messages.error(request, 'You do not have permission to view this ticket.')
        return redirect('support:ticket_list')
    
    responses = ticket.responses.select_related('responded_by').order_by('created_at')
    
    if request.method == 'POST':
        response_form = TicketResponseForm(request.POST, request.FILES)
        if response_form.is_valid():
            response = response_form.save(commit=False)
            response.ticket = ticket
            response.responded_by = request.user
            response.save()
            messages.success(request, 'Response added successfully!')
            return redirect('support:ticket_detail', ticket_id=ticket_id)
    else:
        response_form = TicketResponseForm()
    
    if request.user.is_staff:
        update_form = TicketUpdateForm(instance=ticket)
    else:
        update_form = None
    
    context = {
        'ticket': ticket,
        'responses': responses,
        'response_form': response_form,
        'update_form': update_form,
    }
    return render(request, 'support/ticket_detail.html', context)

@login_required
@staff_required
def ticket_edit(request, ticket_id):
    """Edit support ticket details"""
    ticket = get_object_or_404(SupportTicket, ticket_id=ticket_id)
    
    if request.method == 'POST':
        form = TicketUpdateForm(request.POST, instance=ticket)
        if form.is_valid():
            ticket = form.save()
            if ticket.status in ['RESOLVED', 'CLOSED'] and not ticket.resolved_at:
                ticket.resolved_at = timezone.now()
                ticket.save()
            messages.success(request, 'Ticket updated successfully!')
            return redirect('support:ticket_detail', ticket_id=ticket_id)
    else:
        form = TicketUpdateForm(instance=ticket)
    
    return render(request, 'support/ticket_edit.html', {
        'form': form,
        'ticket': ticket,
        'title': 'Edit Support Ticket'
    })

@login_required
def ticket_respond(request, ticket_id):
    """Add response to a ticket"""
    ticket = get_object_or_404(SupportTicket, ticket_id=ticket_id)
    
    # Check if user has access
    if not request.user.is_staff and request.user != ticket.raised_by:
        messages.error(request, 'You do not have permission to respond to this ticket.')
        return redirect('support:ticket_list')
    
    if request.method == 'POST':
        form = TicketResponseForm(request.POST, request.FILES)
        if form.is_valid():
            response = form.save(commit=False)
            response.ticket = ticket
            response.responded_by = request.user
            response.save()
            messages.success(request, 'Response added successfully!')
    
    return redirect('support:ticket_detail', ticket_id=ticket_id)

@login_required
def feedback_list(request):
    """View list of feedback"""
    feedback_type = request.GET.get('type', '')
    resolved = request.GET.get('resolved', '')
    search_query = request.GET.get('search', '')
    
    feedback = Feedback.objects.select_related('user', 'resolved_by')
    
    # Filter by user role
    if not request.user.is_staff:
        feedback = feedback.filter(user=request.user)
    
    if feedback_type:
        feedback = feedback.filter(feedback_type=feedback_type)
    if resolved:
        feedback = feedback.filter(is_resolved=(resolved == 'yes'))
    if search_query:
        feedback = feedback.filter(
            Q(subject__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query)
        )
    
    feedback = feedback.order_by('-created_at')
    paginator = Paginator(feedback, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'feedback_type': feedback_type,
        'resolved': resolved,
        'search_query': search_query,
        'feedback_types': Feedback.FEEDBACK_TYPES,
    }
    return render(request, 'support/feedback_list.html', context)

@login_required
def feedback_create(request):
    """Create new feedback"""
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            messages.success(request, 'Feedback submitted successfully!')
            return redirect('support:feedback_list')
    else:
        form = FeedbackForm()
    
    return render(request, 'support/feedback_form.html', {
        'form': form,
        'title': 'Submit Feedback'
    })

@login_required
def feedback_detail(request, pk):
    """View feedback details"""
    feedback = get_object_or_404(
        Feedback.objects.select_related('user', 'resolved_by'),
        pk=pk
    )
    
    # Check if user has access
    if not request.user.is_staff and request.user != feedback.user:
        messages.error(request, 'You do not have permission to view this feedback.')
        return redirect('support:feedback_list')
    
    context = {
        'feedback': feedback,
        'resolution_form': FeedbackResolutionForm(instance=feedback) if request.user.is_staff else None,
    }
    return render(request, 'support/feedback_detail.html', context)

@login_required
@staff_required
def feedback_resolve(request, pk):
    """Resolve feedback"""
    feedback = get_object_or_404(Feedback, pk=pk)
    
    if request.method == 'POST':
        form = FeedbackResolutionForm(request.POST, instance=feedback)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.is_resolved = True
            feedback.resolved_by = request.user.staff
            feedback.save()
            messages.success(request, 'Feedback marked as resolved!')
    
    return redirect('support:feedback_detail', pk=pk)

@login_required
def faq_list(request):
    """View FAQ list"""
    category_filter = request.GET.get('category', '')
    search_query = request.GET.get('search', '')
    
    faqs = FAQ.objects.select_related('category', 'created_by')
    
    # Only staff can see unpublished FAQs
    if not request.user.is_staff:
        faqs = faqs.filter(is_published=True)
    
    if category_filter:
        faqs = faqs.filter(category_id=category_filter)
    if search_query:
        faqs = faqs.filter(
            Q(question__icontains=search_query) |
            Q(answer__icontains=search_query)
        )
    
    faqs = faqs.order_by('category', '-created_at')
    
    context = {
        'faqs': faqs,
        'category_filter': category_filter,
        'search_query': search_query,
        'categories': SupportCategory.objects.all(),
    }
    return render(request, 'support/faq_list.html', context)

@login_required
@staff_required
def faq_create(request):
    """Create new FAQ"""
    if request.method == 'POST':
        form = FAQForm(request.POST)
        if form.is_valid():
            faq = form.save(commit=False)
            faq.created_by = request.user.staff
            faq.save()
            messages.success(request, 'FAQ created successfully!')
            return redirect('support:faq_list')
    else:
        form = FAQForm()
    
    return render(request, 'support/faq_form.html', {
        'form': form,
        'title': 'Create FAQ'
    })

@login_required
@staff_required
def faq_edit(request, pk):
    """Edit FAQ"""
    faq = get_object_or_404(FAQ, pk=pk)
    
    if request.method == 'POST':
        form = FAQForm(request.POST, instance=faq)
        if form.is_valid():
            form.save()
            messages.success(request, 'FAQ updated successfully!')
            return redirect('support:faq_list')
    else:
        form = FAQForm(instance=faq)
    
    return render(request, 'support/faq_form.html', {
        'form': form,
        'faq': faq,
        'title': 'Edit FAQ'
    })

@login_required
@staff_required
def faq_toggle_publish(request, pk):
    """Toggle FAQ published status"""
    faq = get_object_or_404(FAQ, pk=pk)
    faq.is_published = not faq.is_published
    faq.save()
    messages.success(
        request,
        f'FAQ {"published" if faq.is_published else "unpublished"} successfully!'
    )
    return redirect('support:faq_list')

@login_required
@staff_required
def category_list(request):
    """View list of support categories"""
    categories = SupportCategory.objects.annotate(
        ticket_count=Count('supportticket'),
        faq_count=Count('faq')
    ).order_by('priority', 'name')
    
    return render(request, 'support/category_list.html', {
        'categories': categories
    })

@login_required
@staff_required
def category_create(request):
    """Create new support category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Support category created successfully!')
            return redirect('support:category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'support/category_form.html', {
        'form': form,
        'title': 'Create Support Category'
    })

@login_required
@staff_required
def category_edit(request, pk):
    """Edit support category"""
    category = get_object_or_404(SupportCategory, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Support category updated successfully!')
            return redirect('support:category_list')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'support/category_form.html', {
        'form': form,
        'category': category,
        'title': 'Edit Support Category'
    })
