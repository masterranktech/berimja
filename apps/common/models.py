from django.db import models


class TimeStampedModel(models.Model):
    """
    یک کلاس انتزاعی (Abstract) پایه برای تمام مدل‌ها
    جهت نگهداری خودکار زمان ایجاد و آخرین ویرایش.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی")

    class Meta:
        abstract = True