from apps.places.models import Place
from apps.reviews.models import Answer, ReviewStatus
from apps.tags.models import PlaceTag, TagRule, TagSource


class TagAggregationService:
    """موتور پردازش داده‌ها و اعمال قوانین استنتاج تگ‌ها بر مبنای پاسخ‌های ساختاریافته کاربران."""

    @classmethod
    def calculate_tags_for_place(cls, place: Place):
        """محاسبه و به‌روزرسانی وضعیت و قدرت (strength) تگ‌های یک مکان."""
        rules = TagRule.objects.select_related('question', 'option', 'target_tag').all()

        for rule in rules:
            # ۱. واکشی پاسخ‌های تاییدشده مرتبط با این مکان و این سوال
            base_answers = Answer.objects.filter(
                review__place=place,
                review__status=ReviewStatus.APPROVED,
                question=rule.question
            )

            total_votes = base_answers.count()

            # در صورتی که حداقل آرای تعیین‌شده برای این قانون حاصل نشده باشد، رد می‌شویم
            if total_votes < rule.minimum_votes:
                continue

            # ۲. شمارش آرای گزینه هدف
            target_option_votes = base_answers.filter(option=rule.option).count()

            # محاسبه درصد انتخاب گزینه هدف
            percentage = int((target_option_votes / total_votes) * 100)

            # ۳. بررسی شرط آستانه درصد آرا (Threshold)
            if percentage >= rule.threshold_percentage:
                # ایجاد یا به‌روزرسانی تگ متناظر مکان
                PlaceTag.objects.update_or_create(
                    place=place,
                    tag=rule.target_tag,
                    defaults={
                        'strength': percentage,
                        'is_active': True,
                        'source': TagSource.AUTO
                    }
                )
            else:
                # اگر تگ قبلاً به‌صورت خودکار فعال بوده اما اکنون آرا افت کرده است، غیرفعال می‌شود
                PlaceTag.objects.filter(
                    place=place,
                    tag=rule.target_tag,
                    source=TagSource.AUTO
                ).update(
                    is_active=False,
                    strength=percentage
                )