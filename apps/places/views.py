from rest_framework import generics, permissions
from apps.places.models import Category, Place
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
    pagination_class = None  # ارسال همه دسته‌ها بدون صفحه‌بندی


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