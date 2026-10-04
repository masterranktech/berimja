# apps/reviews/urls.py
from django.urls import path
from .views import ReportCreateView, ReviewCreateView

app_name = 'reviews_api'

urlpatterns = [
    # اندپوینت ثبت بازخورد در /api/reviews/
    path('', ReviewCreateView.as_view(), name='review_create'),
    # اندپوینت گزارش خطا در /api/reviews/reports/
    path('reports/', ReportCreateView.as_view(), name='report_create'),
]