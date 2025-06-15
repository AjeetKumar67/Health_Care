from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)

class User(AbstractUser):
    ROLES = (
        ('ADMIN', 'Administrator'),
        ('DOCTOR', 'Doctor'),
        ('NURSE', 'Nurse'),
        ('LABTECH', 'Lab Technician'),
        ('RECEPTIONIST', 'Receptionist'),
        ('PATIENT', 'Patient'),
    )
    
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(max_length=150, unique=True)
    phone = models.CharField(max_length=15, blank=True)
    role = models.CharField(max_length=20, choices=ROLES, default='PATIENT')
    reset_password_token = models.CharField(max_length=100, blank=True)
    reset_password_expires = models.DateTimeField(null=True, blank=True)
    refresh_token = models.TextField(blank=True, null=True)

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='custom_user_set',
        related_query_name='custom_user',
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class TokenBlacklist(models.Model):
    token = models.CharField(max_length=500)
    blacklisted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'token_blacklist'
