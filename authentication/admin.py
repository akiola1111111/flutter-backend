from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'is_approved', 'is_staff', 'is_active')
    list_filter = ('user_type', 'is_approved', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Farm Assist Info', {
            'fields': ('user_type', 'phone_number', 'address', 'is_approved')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Farm Assist Info', {
            'fields': ('user_type', 'phone_number', 'address', 'is_approved')
        }),
    )