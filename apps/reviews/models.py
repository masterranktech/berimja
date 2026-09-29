from django.conf import settings
from django.db import models
from apps.common.models import TimeStampedModel
from apps.places.models import Place
from apps.questions.models import Question, QuestionOption


class ReviewStatus(models.TextChoices):
    PENDING = 'PENDING', 'در انتظار بررسی'
    APPROVED = 'APPROVED', 'تأیید شده'
    REJECTED = 'REJECTED', 'رد شده'


class ReportType(models.TextChoices):
    PROBLEM = 'PROBLEM', 'گزارش مشکل'
    SUGGESTION = 'SUGGESTION', 'پیشنهاد اصلاح/بهبود'


class ReportStatus(models.TextChoices):
    PENDING = 'PENDING', 'در انتظار بررسی'
    RESOLVED = 'RESOLVED', 'رسیدگی شده'
    REJECTED = 'REJECTED', 'رد شده'


class Review(TimeStampedModel):
    """مدل بازخورد ساختاریافته کاربر برای یک مکان مشخص."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="کاربر"
    )
    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="مکان"
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name="نظر متنی (اختیاری)"
    )
    status = models.CharField(
        max_length=20,
        choices=ReviewStatus.choices,
        default=ReviewStatus.APPROVED,
        verbose_name="وضعیت بازخورد"
    )

    class Meta:
        verbose_name = "بازخورد کاربر"
        verbose_name_plural = "بازخوردهای کاربران"
        unique_together = ('user', 'place')
        ordering = ['-created_at']

    def __str__(self):
        return f"بازخورد {self.user} برای {self.place.name}"


class Answer(TimeStampedModel):
    """پاسخ کاربر به یک سوال خاص درون یک بازخورد."""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name="بازخورد والد"
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name="سوال"
    )
    option = models.ForeignKey(
        QuestionOption,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name="گزینه انتخابی"
    )

    class Meta:
        verbose_name = "پاسخ ساختاریافته"
        verbose_name_plural = "پاسخ‌های ساختاریافته"
        unique_together = ('review', 'question')

    def __str__(self):
        return f"{self.question.text[:25]} -> {self.option.title}"


class Report(TimeStampedModel):
    """گزارش مشکلات یا پیشنهادات تغییر اطلاعات مکان از سمت کاربران."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name="کاربر گزارش‌دهنده"
    )
    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name="مکان مرتبط"
    )
    report_type = models.CharField(
        max_length=20,
        choices=ReportType.choices,
        default=ReportType.PROBLEM,
        verbose_name="نوع گزارش"
    )
    reason = models.CharField(
        max_length=200,
        verbose_name="عنوان/دلیل گزارش"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="توضیحات تکمیلی"
    )
    status = models.CharField(
        max_length=20,
        choices=ReportStatus.choices,
        default=ReportStatus.PENDING,
        verbose_name="وضعیت بررسی"
    )

    class Meta:
        verbose_name = "گزارش کاربر"
        verbose_name_plural = "گزارش‌های کاربران"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_report_type_display()}: {self.place.name} توسط {self.user}"