from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Doctor, DoctorAvailability, Appointment
from .serializers import DoctorSerializer, DoctorAvailabilitySerializer, AppointmentSerializer
from Auth.permissions import IsAdmin, IsDoctor, IsNurse, IsReceptionist, IsPatient

class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        doctor = self.get_object()
        availabilities = DoctorAvailability.objects.filter(doctor=doctor)
        serializer = DoctorAvailabilitySerializer(availabilities, many=True)
        return Response(serializer.data)

class DoctorAvailabilityViewSet(viewsets.ModelViewSet):
    queryset = DoctorAvailability.objects.all()
    serializer_class = DoctorAvailabilitySerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdmin | IsDoctor]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        if self.request.user.role == 'DOCTOR':
            return DoctorAvailability.objects.filter(doctor__user=self.request.user)
        return DoctorAvailability.objects.all()

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    
    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [permissions.IsAuthenticated & (IsReceptionist | IsPatient)]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated & (IsAdmin | IsReceptionist)]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'PATIENT':
            return Appointment.objects.filter(patient__user=user)
        elif user.role == 'DOCTOR':
            return Appointment.objects.filter(doctor__user=user)
        return Appointment.objects.all()
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        if appointment.status != 'SCHEDULED':
            return Response(
                {"detail": "Only scheduled appointments can be cancelled"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appointment.status = 'CANCELLED'
        appointment.save()
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        appointment = self.get_object()
        if not request.user.role == 'DOCTOR':
            return Response(
                {"detail": "Only doctors can mark appointments as completed"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if appointment.status != 'SCHEDULED':
            return Response(
                {"detail": "Only scheduled appointments can be marked as completed"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appointment.status = 'COMPLETED'
        appointment.save()
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)
