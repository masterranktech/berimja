from django.db import models
from apps.common.models import TimeStampedModel
from .querysets import PlaceQuerySet
import re
from datetime import datetime
import pytz
from django.conf import settings


class Category(TimeStampedModel):
    """مدل دسته‌بندی مکان‌ها (مانند کافه، رستوران، طبیعت و...)"""
    name = models.CharField(max_length=100, unique=True, verbose_name="نام دسته‌بندی")
    slug = models.SlugField(max_length=100, unique=True, allow_unicode=True, verbose_name="اسلاگ (شناسه متنی)")
    icon = models.CharField(max_length=50, blank=True, null=True, verbose_name="آیکون یا کلاس CSS")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ['name']

    def __str__(self):
        return self.name


class Place(TimeStampedModel):
    """مدل مکان فیزیکی در شهر تهران"""
    objects = PlaceQuerySet.as_manager()
    name = models.CharField(max_length=200, verbose_name="نام مکان")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات کوتاه")
    categories = models.ManyToManyField(
        Category,
        related_name='places',
        verbose_name="دسته‌بندی‌ها"
    )
    address = models.CharField(max_length=500, verbose_name="آدرس کامل")
    district = models.CharField(max_length=100, blank=True, null=True, verbose_name="منطقه شهری")
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="عرض جغرافیایی"
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="طول جغرافیایی"
    )
    phone_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="شماره تماس")
    working_hours = models.CharField(max_length=200, blank=True, null=True, verbose_name="ساعات کاری")
    is_active = models.BooleanField(default=True, verbose_name="فعال و قابل نمایش")

    class Meta:
        verbose_name = "مکان"
        verbose_name_plural = "مکان‌ها"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def cover_image(self):
        """دریافت تصویر کاور یا اولین تصویر موجود مکان"""
        cover = self.images.filter(is_cover=True).first()
        if not cover:
            cover = self.images.first()
        return cover

    @property
    def is_open_now(self):
        """
        بررسی وضعیت باز بودن مکان در لحظه فعلی بر اساس working_hours.
        فرمت‌های پشتیبانی شده: '8:30 تا 23:30' یا '10:00 تا 24:00' یا '24 ساعته'
        """
        if not self.working_hours:
            return False

        hours_str = self.working_hours.strip()
        if "۲۴ ساعته" in hours_str or "24 ساعته" in hours_str:
            return True

        # تبدیل اعداد فارسی به انگلیسی
        persian_digits = '۰۱۲۳۴۵۶۷۸۹'
        english_digits = '0123456789'
        translation_table = str.maketrans(persian_digits, english_digits)
        normalized = hours_str.translate(translation_table)

        # استخراج ساعت شروع و پایان (مثلاً 08:30 تا 23:30)
        times = re.findall(r'(\d{1,2}(?::\d{2})?)', normalized)
        if len(times) < 2:
            return False

        try:
            def parse_time_str(t_str):
                parts = t_str.split(':')
                h = int(parts[0])
                m = int(parts[1]) if len(parts) > 1 else 0
                if h == 24:
                    h = 23
                    m = 59
                return h, m

            start_h, start_m = parse_time_str(times[0])
            end_h, end_m = parse_time_str(times[1])

            # زمان محلی تهران
            tz = pytz.timezone(getattr(settings, 'TIME_ZONE', 'Asia/Tehran'))
            now = datetime.now(tz)
            now_minutes = now.hour * 60 + now.minute
            start_minutes = start_h * 60 + start_m
            end_minutes = end_h * 60 + end_m

            if start_minutes <= end_minutes:
                return start_minutes <= now_minutes <= end_minutes
            else:
                # مکان‌هایی که تا بعد از نیمه‌شب باز هستند (مثلاً ۱۸ تا ۲ بامداد)
                return now_minutes >= start_minutes or now_minutes <= end_minutes
        except Exception:
            return False


class PlaceImage(TimeStampedModel):
    """مدل نگهداری تصاویر مکان"""
    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="مکان"
    )
    image = models.ImageField(upload_to='places/%Y/%m/', verbose_name="فایل تصویر")
    alt_text = models.CharField(max_length=200, blank=True, null=True, verbose_name="متن جایگزین")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")
    is_cover = models.BooleanField(default=False, verbose_name="تصویر کاور")

    class Meta:
        verbose_name = "تصویر مکان"
        verbose_name_plural = "تصاویر مکان‌ها"
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return f"تصویر {self.place.name}"