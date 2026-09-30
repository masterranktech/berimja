from django_filters import rest_framework as filters
from apps.places.models import Place


class PlaceFilter(filters.FilterSet):
    """فیلتر مکان‌ها بر اساس اسلاگ دسته‌بندی و نام/شناسه تگ‌ها"""
    category = filters.CharFilter(field_name='categories__slug', lookup_expr='exact')
    district = filters.CharFilter(field_name='district', lookup_expr='icontains')
    tag = filters.CharFilter(method='filter_by_tag')

    class Meta:
        model = Place
        fields = ['category', 'district', 'tag']

    def filter_by_tag(self, queryset, name, value):
        """فیلتر مکان‌هایی که تگ فعال با این شناسه یا نام را دارند"""
        if value.isdigit():
            return queryset.filter(place_tags__tag_id=value, place_tags__is_active=True)
        return queryset.filter(place_tags__tag__name=value, place_tags__is_active=True)