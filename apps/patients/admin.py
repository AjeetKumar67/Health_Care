from django.contrib import admin
from .models import Patient, MedicalRecord, PatientDocument

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('patient_id', 'get_full_name', 'gender', 'blood_group', 'phone')
    search_fields = ('patient_id', 'user__first_name', 'user__last_name', 'phone')
    list_filter = ('gender', 'blood_group')

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'
    get_full_name.admin_order_field = 'user__first_name'

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'date', 'diagnosis')
    list_filter = ('date',)
    search_fields = ('patient__user__first_name', 'patient__user__last_name', 'diagnosis')
    date_hierarchy = 'date'

@admin.register(PatientDocument)
class PatientDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'patient', 'document_type', 'uploaded_at')
    list_filter = ('document_type', 'uploaded_at')
    search_fields = ('title', 'patient__user__first_name', 'patient__user__last_name')
