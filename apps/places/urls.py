from django.urls import path
from .views import (
    CategoryListView,
    HomePageDataView,
    PlaceDetailView,
    PlaceListView,
    home_page_view,
    place_detail_page_view
)

app_name = 'places'

urlpatterns = [
    # اندپوینت‌های REST API (خروجی JSON برای اپلیکیشن موبایل یا درخواست‌های Fetch)
    path('api/home/', HomePageDataView.as_view(), name='api_home'),
    path('api/categories/', CategoryListView.as_view(), name='api_category_list'),
    path('api/places/', PlaceListView.as_view(), name='api_place_list'),
    path('api/places/<int:id>/', PlaceDetailView.as_view(), name='api_place_detail'),

    # صفحات وبسایت (رندر سروری تمپلیت‌های HTML)
    path('places/<int:id>/', place_detail_page_view, name='place_detail'),
]