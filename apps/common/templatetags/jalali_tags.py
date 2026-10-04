import jdatetime
from django import template

register = template.Library()

@register.filter(name='to_jalali')
def to_jalali(value, date_format="%Y/%m/%d"):
    """تبدیل تاریخ میلادی به تاریخ شمسی با فرمت دلخواه"""
    if not value:
        return ""
    try:
        # تبدیل شی datetime/date به تقویم جلالی
        jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
        return jalali_date.strftime(date_format)
    except Exception:
        return value