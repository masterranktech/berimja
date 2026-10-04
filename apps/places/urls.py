from django.urls import path
from .views import (
    CategoryListView,
    HomePageDataView,
    PlaceDetailView,
    PlaceListView,
)

app_name = 'places_api'

urlpatterns = [
    path('home/', HomePageDataView.as_view(), name='home_data'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('', PlaceListView.as_view(), name='place_list'),
    path('<int:id>/', PlaceDetailView.as_view(), name='place_detail'),
]