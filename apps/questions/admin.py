from django.contrib import admin
from .models import Section, Question, QuestionOption


class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 3
    fields = ('title', 'value', 'sort_order')


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'sort_order', 'created_at')
    ordering = ('sort_order',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'section', 'is_general', 'is_active', 'sort_order')
    list_filter = ('is_general', 'is_active', 'section', 'categories')
    search_fields = ('text',)
    filter_horizontal = ('categories',)
    inlines = [QuestionOptionInline]


@admin.register(QuestionOption)
class QuestionOptionAdmin(admin.ModelAdmin):
    list_display = ('title', 'question', 'value', 'sort_order')
    list_filter = ('question__section',)
    search_fields = ('title', 'question__text')