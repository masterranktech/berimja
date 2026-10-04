from django.urls import path
from .views_web import (
    home_page_view,
    place_detail_page_view,
    place_questionnaire_page_view,
)

urlpatterns = [
    path('', home_page_view, name='home'),
    path('places/<int:id>/', place_detail_page_view, name='place_detail'),
    path('places/<int:id>/questionnaire/', place_questionnaire_page_view, name='place_questionnaire'),
]