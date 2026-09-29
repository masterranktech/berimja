from rest_framework import serializers
from .models import CustomUser, phone_regex


class OTPSendSerializer(serializers.Serializer):
    """سریالایزر دریافت شماره موبایل جهت ارسال پیامک کد ورود"""
    phone_number = serializers.CharField(
        max_length=11,
        validators=[phone_regex],
        error_messages={
            'max_length': 'شماره موبایل نباید بیش از ۱۱ رقم باشد.'
        }
    )


class OTPVerifySerializer(serializers.Serializer):
    """سریالایزر تایید کد یک‌بارمصرف"""
    phone_number = serializers.CharField(max_length=11, validators=[phone_regex])
    code = serializers.CharField(max_length=6, min_length=6)


class UserProfileSerializer(serializers.ModelSerializer):
    """سریالایزر اطلاعات پروفایل کاربری"""
    class Meta:
        model = CustomUser
        fields = ('id', 'phone_number', 'display_name', 'created_at')
        read_only_fields = ('id', 'phone_number', 'created_at')