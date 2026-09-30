from django.urls import path
from .views import CategoryListView, HomePageDataView, PlaceDetailView, PlaceListView

app_name = 'places'

urlpatterns = [
    path('home/', HomePageDataView.as_view(), name='home_page_data'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('places/', PlaceListView.as_view(), name='place_list'),
    path('places/<int:id>/', PlaceDetailView.as_view(), name='place_detail'),
]