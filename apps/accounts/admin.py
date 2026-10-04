from django.contrib import admin
from django import forms
from .models import CustomUser, OTPRequest


class CustomUserChangeForm(forms.ModelForm):
    """فرم سفارشی ویرایش کاربر در پنل ادمین بدون اجبار گذرواژه"""
    class Meta:
        model = CustomUser
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # غیرفعال کردن اجباری بودن گذرواژه در فرم ادمین
        if 'password' in self.fields:
            self.fields['password'].required = False


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    form = CustomUserChangeForm

    list_display = ('phone_number', 'display_name', 'is_blocked', 'is_staff', 'is_active', 'created_at')
    search_fields = ('phone_number', 'display_name')
    list_filter = ('is_blocked', 'is_staff', 'is_active')
    ordering = ('-created_at',)

    # چیدمان تمیز و اختصاصی فیلدها در صفحه ویرایش کاربر
    fieldsets = (
        ('اطلاعات هویتی کاربر', {
            'fields': ('phone_number', 'display_name')
        }),
        ('وضعیت و دسترسی‌ها', {
            'fields': ('is_active', 'is_blocked', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
    )


@admin.register(OTPRequest)
class OTPRequestAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'code', 'is_used', 'expires_at', 'created_at')
    search_fields = ('phone_number',)
    list_filter = ('is_used',)
    readonly_fields = ('phone_number', 'code', 'expires_at', 'created_at')