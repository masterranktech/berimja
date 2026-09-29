from django.contrib import admin
from .models import Category, Place, PlaceImage


class PlaceImageInline(admin.TabularInline):
    model = PlaceImage
    extra = 1
    fields = ('image', 'alt_text', 'is_cover', 'sort_order')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'district', 'is_active', 'created_at')
    list_filter = ('is_active', 'categories', 'district')
    search_fields = ('name', 'address', 'district')
    filter_horizontal = ('categories',)
    inlines = [PlaceImageInline]


@admin.register(PlaceImage)
class PlaceImageAdmin(admin.ModelAdmin):
    list_display = ('place', 'is_cover', 'sort_order', 'created_at')
    list_filter = ('is_cover',)