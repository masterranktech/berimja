from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from apps.common.models import TimeStampedModel
from apps.places.models import Place
from apps.questions.models import Question, QuestionOption


class TagSource(models.TextChoices):
    ADMIN = 'ADMIN', 'مدیر سیستم'
    AUTO = 'AUTO', 'سیستمی (داده‌محور)'
    SUGGESTED = 'SUGGESTED', 'پیشنهاد کاربران'


class TagStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'فعال'
    PENDING = 'PENDING', 'در انتظار تایید'
    REJECTED = 'REJECTED', 'رد شده'


class Tag(TimeStampedModel):
    """مدل تگ‌های معنایی برای تصمیم‌گیری کاربران."""
    name = models.CharField(max_length=100, unique=True, verbose_name="نام تگ")
    source = models.CharField(
        max_length=20,
        choices=TagSource.choices,
        default=TagSource.ADMIN,
        verbose_name="منبع تگ"
    )
    status = models.CharField(
        max_length=20,
        choices=TagStatus.choices,
        default=TagStatus.ACTIVE,
        verbose_name="وضعیت تگ"
    )

    class Meta:
        verbose_name = "تگ"
        verbose_name_plural = "تگ‌ها"
        ordering = ['name']

    def __str__(self):
        return self.name


class PlaceTag(TimeStampedModel):
    """ارتباط میان مکان و تگ به همراه میزان قدرت و اعتماد آماری."""
    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name='place_tags',
        verbose_name="مکان"
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='tagged_places',
        verbose_name="تگ"
    )
    strength = models.PositiveSmallIntegerField(
        default=100,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="میزان قدرت/اطمینان (۰ تا ۱۰۰)"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال و قابل نمایش"
    )
    source = models.CharField(
        max_length=20,
        choices=TagSource.choices,
        default=TagSource.ADMIN,
        verbose_name="منبع انتساب"
    )

    class Meta:
        verbose_name = "تگ مکان"
        verbose_name_plural = "تگ‌های مکان‌ها"
        unique_together = ('place', 'tag')
        ordering = ['-strength', '-updated_at']

    def __str__(self):
        return f"{self.place.name} - {self.tag.name} ({self.strength}%)"


class TagRule(TimeStampedModel):
    """قوانین استنتاج خودکار تگ‌ها بر اساس پاسخ‌های ساختاریافته کاربران."""
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='tag_rules',
        verbose_name="سوال مرتبط"
    )
    option = models.ForeignKey(
        QuestionOption,
        on_delete=models.CASCADE,
        related_name='tag_rules',
        verbose_name="گزینه مورد نظر"
    )
    target_tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='derived_rules',
        verbose_name="تگ هدف"
    )
    threshold_percentage = models.PositiveSmallIntegerField(
        default=60,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name="حداقل درصد آرا برای فعال‌سازی"
    )
    minimum_votes = models.PositiveIntegerField(
        default=5,
        verbose_name="حداقل تعداد کل آرا برای اعمال قانون"
    )

    class Meta:
        verbose_name = "قانون استنتاج تگ"
        verbose_name_plural = "قوانین استنتاج تگ‌ها"
        unique_together = ('question', 'option', 'target_tag')

    def __str__(self):
        return f"اگر {self.option.title} >= {self.threshold_percentage}% -> {self.target_tag.name}"