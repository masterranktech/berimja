from django.contrib import admin
from .models import Review, Answer, Report


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ('question', 'option')
    can_delete = False


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'place', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__phone_number', 'user__display_name', 'place__name', 'comment')
    inlines = [AnswerInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('review', 'question', 'option', 'created_at')
    list_filter = ('question',)
    search_fields = ('review__place__name', 'question__text', 'option__title')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('place', 'user', 'report_type', 'reason', 'status', 'created_at')
    list_filter = ('report_type', 'status')
    search_fields = ('place__name', 'user__phone_number', 'reason', 'description')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'report_type', 'get_target_place', 'user', 'status', 'created_at')
    list_filter = ('report_type', 'status', 'created_at')
    search_fields = ('reason', 'description', 'user__phone_number', 'place__name')
    readonly_fields = ('created_at', 'updated_at')

    @admin.display(description='مکان / موضوع')
    def get_target_place(self, obj):
        if obj.place:
            return obj.place.name
        return "✨ پیشنهاد مکان جدید (مستقل)"