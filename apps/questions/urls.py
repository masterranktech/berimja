from django.urls import path
from .views import PlaceQuestionnaireView

app_name = 'questions'

urlpatterns = [
    path('places/<int:place_id>/questions/', PlaceQuestionnaireView.as_view(), name='place_questions'),
]