from django.contrib import admin
from .models import Doctor, DoctorAvailability, Appointment

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'get_email', 'specialization', 'experience_years', 'consultation_fee')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'specialization')
    list_filter = ('specialization', 'experience_years')
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'day_of_week', 'start_time', 'end_time', 'is_available')
    search_fields = ('doctor__user__first_name', 'doctor__user__last_name')
    list_filter = ('day_of_week', 'is_available')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'appointment_date', 'appointment_time', 'status')
    search_fields = ('patient__user__first_name', 'patient__user__last_name', 
                    'doctor__user__first_name', 'doctor__user__last_name')
    list_filter = ('status', 'appointment_date')
