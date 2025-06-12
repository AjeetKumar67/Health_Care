from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils.crypto import get_random_string
from .models import Patient

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_patient_profile(sender, instance, created, **kwargs):
    """Create a Patient profile when a new user with user_type='PATIENT' is created"""
    if created and instance.user_type == 'PATIENT':
        # Generate a unique patient ID
        while True:
            patient_id = 'P' + get_random_string(9, '0123456789')
            if not Patient.objects.filter(patient_id=patient_id).exists():
                break
                
        Patient.objects.create(
            user=instance,
            patient_id=patient_id,
            phone=instance.phone,
            address=instance.address,
            # Set default values for required fields
            date_of_birth='2000-01-01',  # Default date, should be updated by user
            blood_group='O+',  # Default blood group, should be updated by user
            gender='O',  # Default gender, should be updated by user
            emergency_contact_name='To be updated',
            emergency_contact_phone='To be updated'
        )
