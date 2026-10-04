import random
import re
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from apps.common.models import TimeStampedModel
from django.core.exceptions import ValidationError

phone_regex = RegexValidator(
    regex=r'^09\d{9}$',
    message="شماره موبایل باید با ۰۹ شروع شده و ۱۱ رقم باشد."
)

def validate_display_name(value):
    """اعتبارسنجی نام نمایشی: حداقل ۳ کاراکتر، بدون استفاده از شماره موبایل و ارقام"""
    val = value.strip()
    if len(val) < 3:
        raise ValidationError('نام نمایشی باید حداقل ۳ کاراکتر باشد.')
    # جلوگیری از وارد کردن شماره تلفن یا فرمت‌های مشابه موبایل
    if re.search(r'09\d{9}', val) or re.search(r'\d{7,}', val):
        raise ValidationError('استفاده از شماره تماس به عنوان نام نمایشی مجاز نیست.')


class CustomUserManager(BaseUserManager):
    """منیجر سفارشی برای مدیریت ساخت کاربر با شماره موبایل به جای یوزرنیم."""

    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('شماره موبایل الزامی است.')
        phone_number = phone_number.strip()
        user = self.model(phone_number=phone_number, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('سوپریوزر باید فیلد is_staff=True داشته باشد.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('سوپریوزر باید فیلد is_superuser=True داشته باشد.')

        return self.create_user(phone_number, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """مدل کاربری اصلی پروژه بر پایه شماره موبایل."""
    phone_number = models.CharField(
        max_length=11,
        unique=True,
        validators=[phone_regex],
        verbose_name="شماره تلفن همراه"
    )
    display_name = models.CharField(
        max_length=100,
        validators=[validate_display_name],
        verbose_name="نام و نام خانوادگی / نام مستعار"
    )
    is_blocked = models.BooleanField(
        default=False,
        verbose_name="مسدود شده"
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name="دسترسی ادمین"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال"
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['display_name']

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"

    def __str__(self):
        return self.display_name or self.phone_number

class OTPRequest(TimeStampedModel):
    """مدل ذخیره کد یکبار مصرف پیامکی برای ورود و ثبت‌نام."""
    phone_number = models.CharField(
        max_length=11,
        validators=[phone_regex],
        verbose_name="شماره تلفن همراه"
    )
    code = models.CharField(
        max_length=6,
        verbose_name="کد تأیید"
    )
    is_used = models.BooleanField(
        default=False,
        verbose_name="استفاده شده"
    )
    expires_at = models.DateTimeField(
        verbose_name="تاریخ انقضا"
    )

    class Meta:
        verbose_name = "درخواست کد یکبار مصرف"
        verbose_name_plural = "درخواست‌های کد یکبار مصرف"
        ordering = ['-created_at']

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @classmethod
    def generate_code(cls, phone_number, validity_minutes=2):
        """تولید یک کد ۶ رقمی تصادفی و ثبت انقضا."""
        code = str(random.randint(100000, 999999))
        expires_at = timezone.now() + timezone.timedelta(minutes=validity_minutes)
        return cls.objects.create(
            phone_number=phone_number,
            code=code,
            expires_at=expires_at
        )