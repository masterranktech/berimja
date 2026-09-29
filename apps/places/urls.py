from django.urls import path
from .views import CategoryListView, PlaceListView, PlaceDetailView

app_name = 'places'

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('places/', PlaceListView.as_view(), name='place_list'),
    path('places/<int:id>/', PlaceDetailView.as_view(), name='place_detail'),
]