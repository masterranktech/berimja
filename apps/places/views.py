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
from django.shortcuts import render
from apps.places.models import Place
from apps.tags.models import Tag
from django.shortcuts import get_object_or_404
from apps.reviews.models import ReviewStatus


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


def home_page_view(request):
    """رندر سمت سرور (SSR) صفحه اصلی همراه با تگ‌ها و فیلتر سریع"""
    active_tag = request.GET.get('tag', '').strip()

    # واکشی بهینه مکان‌ها به همراه تگ‌ها، تصاویر و دسته‌ها (جلوگیری از مشکل N+1)
    places_qs = Place.objects.filter(is_active=True).prefetch_related(
        'categories',
        'place_tags__tag',
        'images'
    ).order_by('-created_at')

    # اعمال فیلتر سریع در صورت انتخاب کاربر
    if active_tag:
        places_qs = places_qs.filter(
            place_tags__tag__name=active_tag,
            place_tags__is_active=True
        ).distinct()

    # دریافت ۸ تگ پرتکرار و فعال برای فیلترهای سریع بالای صفحه
    quick_tags = Tag.objects.filter(status='ACTIVE')[:8]

    context = {
        'places': places_qs,
        'quick_tags': quick_tags,
        'active_tag': active_tag,
    }
    return render(request, 'places/home.html', context)


def place_detail_page_view(request, id):
    """رندر سمت سرور (SSR) صفحه کامل جزئیات مکان"""
    place = get_object_or_404(
        Place.objects.prefetch_related(
            'categories',
            'images',
            'place_tags__tag',
            'reviews__user'
        ),
        id=id,
        is_active=True
    )

    # تگ‌های فعال با اطمینان آماری مرتب‌شده
    active_tags = place.place_tags.filter(
        is_active=True,
        tag__status='ACTIVE'
    ).select_related('tag').order_by('-strength')

    # بازخوردهای تاییدشده همراه با نظرات متنی
    approved_reviews = place.reviews.filter(
        status=ReviewStatus.APPROVED
    ).exclude(comment__isnull=True).exclude(comment__exact='').select_related('user').order_by('-created_at')

    context = {
        'place': place,
        'active_tags': active_tags,
        'approved_reviews': approved_reviews,
    }
    return render(request, 'places/place_detail.html', context)