# apps/places/views.py
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers

from apps.places.models import Category, Place
from apps.tags.models import Tag
from .filters import PlaceFilter
from .serializers import (
    CategorySerializer,
    PlaceDetailSerializer,
    PlaceListSerializer,
)


class CategoryListView(generics.ListAPIView):
    """لیست دسته‌بندی‌های فعال سایت"""
    permission_classes = [permissions.AllowAny]
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    pagination_class = None

    @extend_schema(tags=['Places'], summary="لیست دسته‌بندی‌ها")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PlaceListView(generics.ListAPIView):
    """لیست مکان‌های فعال همراه با فیلتر سریع دسته‌بندی، تگ و جستجوی متنی"""
    permission_classes = [permissions.AllowAny]
    serializer_class = PlaceListSerializer
    filterset_class = PlaceFilter
    search_fields = ['name', 'address', 'district']

    def get_queryset(self):
        return Place.objects.filter(is_active=True).prefetch_related(
            'categories',
            'place_tags__tag',
            'images'
        ).distinct()

    @extend_schema(tags=['Places'], summary="لیست مکان‌ها با فیلتر و جستجو")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PlaceDetailView(generics.RetrieveAPIView):
    """دریافت اطلاعات کامل صفحه جزئیات یک مکان"""
    permission_classes = [permissions.AllowAny]
    serializer_class = PlaceDetailSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return Place.objects.filter(is_active=True).prefetch_related(
            'categories',
            'images',
            'place_tags__tag'
        )

    @extend_schema(tags=['Places'], summary="مشاهده جزئیات یک مکان")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class HomePageDataView(APIView):
    """اندپوینت جامع صفحه نخست: شامل دسته‌بندی‌ها، جدیدترین‌ها، پرطرفدارها و تگ‌های فیلتر سریع"""
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=['Places'],
        summary="دریافت یکپارچه داده‌های صفحه اول",
        responses={
            200: inline_serializer(
                name='HomePageResponse',
                fields={
                    'categories': CategorySerializer(many=True),
                    'quick_filters': inline_serializer(
                        name='QuickFilterItem',
                        fields={
                            'id': serializers.IntegerField(),
                            'name': serializers.CharField()
                        },
                        many=True
                    ),
                    'latest_places': PlaceListSerializer(many=True),
                    'popular_places': PlaceListSerializer(many=True),
                }
            )
        }
    )
    def get(self, request):
        categories = Category.objects.filter(is_active=True)
        categories_data = CategorySerializer(categories, many=True, context={'request': request}).data

        quick_tags = Tag.objects.filter(status='ACTIVE')[:8].values('id', 'name')
        latest_places = Place.objects.latest_places(limit=6)
        latest_data = PlaceListSerializer(latest_places, many=True, context={'request': request}).data

        popular_places = Place.objects.popular_places(limit=6)
        popular_data = PlaceListSerializer(popular_places, many=True, context={'request': request}).data

        return Response({
            "categories": categories_data,
            "quick_filters": quick_tags,
            "latest_places": latest_data,
            "popular_places": popular_data,
        })