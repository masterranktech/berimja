# apps/questions/views.py
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from apps.places.models import Place
from apps.questions.models import Section
from .serializers import SectionWithQuestionsSerializer


class PlaceQuestionnaireView(APIView):
    """دریافت داینامیک سوالات مرتبط با یک مکان بر اساس دسته‌بندی‌های آن"""
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=['Questions'],
        summary="دریافت سوالات پرسشنامه متناسب با مکان",
        responses={200: SectionWithQuestionsSerializer(many=True)}
    )
    def get(self, request, place_id):
        place = get_object_or_404(Place, id=place_id, is_active=True)
        place_categories = place.categories.all()

        sections = Section.objects.prefetch_related('questions__options').order_by('sort_order', 'id')
        serializer = SectionWithQuestionsSerializer(
            sections,
            many=True,
            context={'place_categories': place_categories}
        )
        filtered_data = [sec for sec in serializer.data if len(sec['questions']) > 0]
        return Response(filtered_data, status=status.HTTP_200_OK)