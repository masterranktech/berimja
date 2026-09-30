from django.urls import path
from .views import ReportCreateView, ReviewCreateView

app_name = 'reviews'

urlpatterns = [
    path('reviews/', ReviewCreateView.as_view(), name='review_create'),
    path('reports/', ReportCreateView.as_view(), name='report_create'),
]