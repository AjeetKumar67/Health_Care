from rest_framework import serializers
from .models import Doctor, DoctorAvailability, Appointment

class DoctorSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = Doctor
        fields = ['id', 'user', 'specialization', 'qualification', 'experience_years', 'consultation_fee']
    
    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'full_name': obj.user.get_full_name(),
            'email': obj.user.email
        }

class DoctorAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorAvailability
        fields = '__all__'

class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = ['id', 'patient', 'doctor', 'patient_name', 'doctor_name', 
                 'appointment_date', 'appointment_time', 'reason', 'status', 
                 'notes', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_patient_name(self, obj):
        return obj.patient.user.get_full_name()
    
    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.get_full_name()}"
    
    def validate(self, data):
        # Check if the doctor is available at the requested time
        if self.context['request'].method in ['POST', 'PUT', 'PATCH']:
            doctor = data.get('doctor')
            date = data.get('appointment_date')
            time = data.get('appointment_time')
            
            # Check doctor availability for the day
            day_of_week = date.weekday()
            availability = DoctorAvailability.objects.filter(
                doctor=doctor,
                day_of_week=day_of_week,
                is_available=True
            ).first()
            
            if not availability:
                raise serializers.ValidationError("Doctor is not available on this day")
            
            if time < availability.start_time or time > availability.end_time:
                raise serializers.ValidationError("Appointment time is outside doctor's working hours")
            
            # Check for overlapping appointments
            existing_appointments = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=date,
                status='SCHEDULED'
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            for existing_apt in existing_appointments:
                if abs((existing_apt.appointment_time.hour * 60 + existing_apt.appointment_time.minute) - 
                       (time.hour * 60 + time.minute)) < 30:  # 30-minute slot
                    raise serializers.ValidationError("This time slot is already booked")
        
        return data
