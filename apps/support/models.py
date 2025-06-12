from django.db import models
from apps.users.models import User
from apps.staff.models import Staff

class SupportCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    priority = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Support Categories"

class SupportTicket(models.Model):
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('ASSIGNED', 'Assigned'),
        ('IN_PROGRESS', 'In Progress'),
        ('ON_HOLD', 'On Hold'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]
    
    ticket_id = models.CharField(max_length=10, unique=True)
    category = models.ForeignKey(SupportCategory, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    raised_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='raised_tickets')
    assigned_to = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='assigned_tickets')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Ticket {self.ticket_id} - {self.subject}"

class TicketResponse(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='responses')
    responded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to='ticket_attachments/', null=True, blank=True)
    
    def __str__(self):
        return f"Response to Ticket {self.ticket.ticket_id}"

class Feedback(models.Model):
    FEEDBACK_TYPES = [
        ('GENERAL', 'General Feedback'),
        ('COMPLAINT', 'Complaint'),
        ('SUGGESTION', 'Suggestion'),
        ('APPRECIATION', 'Appreciation'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    rating = models.PositiveIntegerField(null=True, blank=True)  # 1-5 rating
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='resolved_feedback')
    resolution_notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.feedback_type} - {self.subject}"

class FAQ(models.Model):
    category = models.ForeignKey(SupportCategory, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField()
    created_by = models.ForeignKey(Staff, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)
    
    def __str__(self):
        return self.question
