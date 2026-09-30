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
    pagination_class = None


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


from rest_framework.views import APIView
from rest_framework.response import Response
from apps.tags.models import Tag


class HomePageDataView(APIView):
    """اندپوینت جامع صفحه نخست: شامل دسته‌بندی‌ها، جدیدترین‌ها، پرطرفدارها و تگ‌های فیلتر سریع"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        # ۱. دسته‌بندی‌های فعال
        categories = Category.objects.filter(is_active=True)
        categories_data = CategorySerializer(categories, many=True, context={'request': request}).data

        # ۲. تگ‌های پرتکرار برای فیلتر سریع در بالای صفحه
        quick_tags = Tag.objects.filter(status='ACTIVE')[:8].values('id', 'name')

        # ۳. بخش جدیدترین مکان‌ها
        latest_places = Place.objects.latest_places(limit=6)
        latest_data = PlaceListSerializer(latest_places, many=True, context={'request': request}).data

        # ۴. بخش محبوب‌ترین‌ها (بر اساس بیشترین نظر)
        popular_places = Place.objects.popular_places(limit=6)
        popular_data = PlaceListSerializer(popular_places, many=True, context={'request': request}).data

        return Response({
            "categories": categories_data,
            "quick_filters": quick_tags,
            "latest_places": latest_data,
            "popular_places": popular_data,
        })