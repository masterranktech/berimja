from django.contrib import admin
from .models import CustomUser, OTPRequest


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'display_name', 'is_blocked', 'is_staff', 'created_at')
    search_fields = ('phone_number', 'display_name')
    list_filter = ('is_blocked', 'is_staff', 'is_active')


@admin.register(OTPRequest)
class OTPRequestAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'code', 'is_used', 'expires_at', 'created_at')
    search_fields = ('phone_number',)
    list_filter = ('is_used',)