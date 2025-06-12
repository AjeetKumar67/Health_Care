from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from simple_history.models import HistoricalRecords
from apps.patients.models import Patient
from apps.staff.models import Doctor


class DoctorSchedule(models.Model):
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'DOCTOR'},
        related_name='schedules'
    )
    day_of_week = models.IntegerField(choices=[
        (0, _('Monday')),
        (1, _('Tuesday')),
        (2, _('Wednesday')),
        (3, _('Thursday')),
        (4, _('Friday')),
        (5, _('Saturday')),
        (6, _('Sunday')),
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    break_start_time = models.TimeField(null=True, blank=True)
    break_end_time = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ['doctor', 'day_of_week']
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f'{self.doctor} - {self.get_day_of_week_display()}'


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No Show'),
    ]

    appointment_id = models.CharField(max_length=10, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time_slot = models.TimeField()
    symptoms = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.appointment_id} - {self.patient.user.get_full_name()} with Dr. {self.doctor.user.get_full_name()}"


class AppointmentHistory(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    status = models.CharField(max_length=20)
    notes = models.TextField()
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.appointment.appointment_id} - {self.status} at {self.changed_at}"


class AppointmentReminder(models.Model):
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='reminders'
    )
    reminder_type = models.CharField(
        max_length=10,
        choices=[
            ('EMAIL', _('Email')),
            ('SMS', _('SMS')),
            ('BOTH', _('Both'))
        ],
        default='BOTH'
    )
    reminder_sent = models.BooleanField(default=False)
    scheduled_time = models.DateTimeField()
    sent_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['scheduled_time']

    def __str__(self):
        return f'Reminder for {self.appointment}'
