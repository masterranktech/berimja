from django.db import models
from django.db.models import Count, Q


class PlaceQuerySet(models.QuerySet):
    """کوئری‌ست اختصاصی مکان‌ها برای اعمال فیلترهای سریع و بخش‌های صفحه اصلی."""

    def active(self):
        """فقط مکان‌های فعال همراه با بهینه‌سازی واکشی روابط"""
        return self.filter(is_active=True).prefetch_related(
            'categories',
            'place_tags__tag',
            'images'
        ).distinct()

    def latest_places(self, limit=6):
        """جدیدترین مکان‌های ثبت‌شده"""
        return self.active().order_by('-created_at')[:limit]

    def popular_places(self, limit=6):
        """محبوب‌ترین مکان‌ها بر اساس بیشترین تعداد بازخوردهای تاییدشده"""
        return self.active().annotate(
            approved_reviews_count=Count(
                'reviews',
                filter=Q(reviews__status='APPROVED')
            )
        ).order_by('-approved_reviews_count', '-created_at')[:limit]

    def by_quick_tag(self, tag_name, limit=6):
        """فیلتر مکان‌ها با تگ فعال مشخص"""
        return self.active().filter(
            place_tags__tag__name=tag_name,
            place_tags__is_active=True
        ).order_by('-place_tags__strength')[:limit]