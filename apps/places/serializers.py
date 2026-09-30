from rest_framework import serializers
from apps.places.models import Category, Place, PlaceImage
from apps.tags.models import PlaceTag


class CategorySerializer(serializers.ModelSerializer):
    """سریالایزر دسته‌بندی‌ها"""
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'icon')


class PlaceImageSerializer(serializers.ModelSerializer):
    """سریالایزر تصاویر گالری مکان"""
    class Meta:
        model = PlaceImage
        fields = ('id', 'image', 'alt_text', 'sort_order', 'is_cover')


class PlaceTagItemSerializer(serializers.ModelSerializer):
    """سریالایزر تگ‌های فعال متصل به مکان همراه با درصد اطمینان"""
    tag_id = serializers.IntegerField(source='tag.id', read_only=True)
    name = serializers.CharField(source='tag.name', read_only=True)

    class Meta:
        model = PlaceTag
        fields = ('tag_id', 'name', 'strength')


class PlaceListSerializer(serializers.ModelSerializer):
    """سریالایزر کارت‌های مکان در صفحه اصلی و لیست جستجو"""
    categories = CategorySerializer(many=True, read_only=True)
    cover_image = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Place
        fields = (
            'id', 'name', 'district', 'address',
            'cover_image', 'categories', 'tags'
        )

    def get_cover_image(self, obj):
        cover = obj.cover_image
        if cover and cover.image:
            request = self.context.get('request')
            return request.build_absolute_uri(cover.image.url) if request else cover.image.url
        return None

    def get_tags(self, obj):
        active_tags = obj.place_tags.filter(is_active=True).select_related('tag')[:5]
        return PlaceTagItemSerializer(active_tags, many=True).data


class PlaceDetailSerializer(serializers.ModelSerializer):
    """سریالایزر اطلاعات کامل صفحه جزئیات مکان"""
    categories = CategorySerializer(many=True, read_only=True)
    images = PlaceImageSerializer(many=True, read_only=True)
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Place
        fields = (
            'id', 'name', 'description', 'district', 'address',
            'latitude', 'longitude', 'phone_number', 'working_hours',
            'categories', 'images', 'tags', 'created_at'
        )

    def get_tags(self, obj):
        active_tags = obj.place_tags.filter(is_active=True).select_related('tag')
        return PlaceTagItemSerializer(active_tags, many=True).data