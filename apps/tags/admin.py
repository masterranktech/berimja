from django.contrib import admin
from .models import Tag, PlaceTag, TagRule


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'source', 'status', 'created_at')
    list_filter = ('source', 'status')
    search_fields = ('name',)


@admin.register(PlaceTag)
class PlaceTagAdmin(admin.ModelAdmin):
    list_display = ('place', 'tag', 'strength', 'source', 'is_active', 'updated_at')
    list_filter = ('is_active', 'source', 'tag')
    search_fields = ('place__name', 'tag__name')


@admin.register(TagRule)
class TagRuleAdmin(admin.ModelAdmin):
    list_display = ('target_tag', 'question', 'option', 'threshold_percentage', 'minimum_votes')
    list_filter = ('target_tag', 'question')
    search_fields = ('target_tag__name', 'question__text', 'option__title')