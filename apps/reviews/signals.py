from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.reviews.models import Answer, Review
from apps.tags.services import TagAggregationService


@receiver(post_save, sender=Answer)
@receiver(post_delete, sender=Answer)
def trigger_tag_aggregation_on_answer(sender, instance, **kwargs):
    """اجرای موتور تجمیع تگ‌ها به ازای ایجاد، ویرایش یا حذف پاسخ."""
    place = instance.review.place
    TagAggregationService.calculate_tags_for_place(place)


@receiver(post_save, sender=Review)
def trigger_tag_aggregation_on_review_status_change(sender, instance, **kwargs):
    """اجرای مجدد موتور تجمیع در صورت تغییر وضعیت بازخورد (مثلاً تأیید یا رد شدن توسط ادمین)."""
    TagAggregationService.calculate_tags_for_place(instance.place)