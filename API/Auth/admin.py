from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, TokenBlacklist

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'username', 'is_staff', 'is_active',)
    list_filter = ('email', 'username', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email', 'username',)
    ordering = ('email',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(TokenBlacklist)
