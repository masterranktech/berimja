from django.db import models
from apps.common.models import TimeStampedModel
from apps.places.models import Category


class Section(TimeStampedModel):
    """بخش‌بندی سوالات برای تفکیک در رابط کاربری (مثلاً سوالات عمومی، خدمات کافه و...)"""
    title = models.CharField(max_length=150, verbose_name="عنوان بخش")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "بخش پرسشنامه"
        verbose_name_plural = "بخش‌های پرسشنامه"
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.title


class Question(TimeStampedModel):
    """مدل سوالات پرسشنامه که در مکان‌ها مجدداً استفاده می‌شوند."""
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name="بخش مرتبط"
    )
    categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name='questions',
        verbose_name="دسته‌بندی‌های مرتبط (خالی یعنی عمومی برای همه)"
    )
    text = models.CharField(max_length=300, verbose_name="متن سوال")
    is_general = models.BooleanField(
        default=False,
        verbose_name="سوال عمومی (نمایش برای همه مکان‌ها)"
    )
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "سوال"
        verbose_name_plural = "سوالات"
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.text


class QuestionOption(TimeStampedModel):
    """گزینه‌های قابل انتخاب برای هر سوال."""
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='options',
        verbose_name="سوال"
    )
    title = models.CharField(max_length=150, verbose_name="عنوان گزینه")
    value = models.IntegerField(
        default=1,
        verbose_name="ارزش عددی/وزن گزینه (مثلاً برای محاسبات آماری)"
    )
    sort_order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "گزینه سوال"
        verbose_name_plural = "گزینه‌های سوالات"
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f"{self.question.text[:30]}... -> {self.title}"