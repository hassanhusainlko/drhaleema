from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'get_full_name', 'email', 'phone_number', 'is_staff', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone_number')
    list_filter = ('is_staff', 'gender')

    fieldsets = UserAdmin.fieldsets + (
        ('Patient Profile', {'fields': ('phone_number', 'date_of_birth', 'gender', 'address')}),
    )
