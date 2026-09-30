from django.db import models
from apps.common.models import TimeStampedModel
from .querysets import PlaceQuerySet


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