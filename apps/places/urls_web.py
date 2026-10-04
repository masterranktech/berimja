from django.urls import path
from .views import home_page_view, place_detail_page_view

urlpatterns = [
    # صفحه اصلی سایت
    path('', home_page_view, name='home'),
    # صفحه جزئیات مکان
    path('places/<int:id>/', place_detail_page_view, name='place_detail'),
]