from django.contrib import admin
from .models import SupportCategory, SupportTicket, TicketResponse, Feedback, FAQ

@admin.register(SupportCategory)
class SupportCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority')
    list_filter = ('priority',)
    search_fields = ('name', 'description')
    ordering = ('priority', 'name')

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'category', 'subject', 'status', 'priority', 'raised_by', 'assigned_to', 'created_at')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('ticket_id', 'subject', 'description', 'raised_by__username', 'assigned_to__user__username')
    ordering = ('-created_at',)
    raw_id_fields = ('raised_by', 'assigned_to')

class TicketResponseInline(admin.TabularInline):
    model = TicketResponse
    extra = 0
    raw_id_fields = ('responded_by',)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('feedback_type', 'subject', 'user', 'rating', 'is_resolved', 'created_at')
    list_filter = ('feedback_type', 'is_resolved', 'rating')
    search_fields = ('subject', 'message', 'user__username')
    ordering = ('-created_at',)
    raw_id_fields = ('user', 'resolved_by')

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'created_by', 'is_published', 'created_at')
    list_filter = ('category', 'is_published')
    search_fields = ('question', 'answer')
    ordering = ('category', '-created_at')
    raw_id_fields = ('created_by',)
