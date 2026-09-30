from rest_framework import serializers
from apps.questions.models import Question, QuestionOption, Section


class QuestionOptionSerializer(serializers.ModelSerializer):
    """سریالایزر گزینه‌های سوال"""

    class Meta:
        model = QuestionOption
        fields = ('id', 'title', 'value', 'sort_order')


class QuestionSerializer(serializers.ModelSerializer):
    """سریالایزر سوال همراه با گزینه‌های انتخابی"""
    options = QuestionOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'text', 'is_general', 'sort_order', 'options')


class SectionWithQuestionsSerializer(serializers.ModelSerializer):
    """سریالایزر بخش‌های پرسشنامه به همراه سوالات مرتبط"""
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = ('id', 'title', 'sort_order', 'questions')

    def get_questions(self, obj):
        place_categories = self.context.get('place_categories', [])
        # سوالات این بخش که یا عمومی هستند یا به دسته‌بندی‌های این مکان متصلند
        questions = obj.questions.filter(is_active=True).filter(
            categories__in=place_categories
        ) | obj.questions.filter(is_active=True, is_general=True)

        return QuestionSerializer(questions.distinct().order_by('sort_order', 'id'), many=True).data