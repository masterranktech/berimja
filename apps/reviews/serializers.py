from django.db import transaction
from rest_framework import serializers
from apps.places.models import Place
from apps.questions.models import Question, QuestionOption
from apps.reviews.models import Answer, Report, Review, ReviewStatus


class AnswerInputSerializer(serializers.Serializer):
    """اعتبارسنجی ورودی هر پاسخ"""
    question_id = serializers.IntegerField()
    option_id = serializers.IntegerField()

    def validate(self, attrs):
        question = Question.objects.filter(id=attrs['question_id'], is_active=True).first()
        if not question:
            raise serializers.ValidationError("سوال مورد نظر یافت نشد یا غیرفعال است.")

        option = QuestionOption.objects.filter(id=attrs['option_id'], question=question).first()
        if not option:
            raise serializers.ValidationError("گزینه انتخابی متعلق به این سوال نیست.")

        attrs['question_obj'] = question
        attrs['option_obj'] = option
        return attrs


class ReviewCreateSerializer(serializers.ModelSerializer):
    """سریالایزر ثبت بازخورد کامل به همراه پاسخ‌ها"""
    place_id = serializers.IntegerField(write_only=True)
    answers = AnswerInputSerializer(many=True, write_only=True)

    class Meta:
        model = Review
        fields = ('id', 'place_id', 'comment', 'answers', 'created_at')
        read_only_fields = ('id', 'created_at')

    def validate(self, attrs):
        user = self.context['request'].user
        place_id = attrs['place_id']

        place = Place.objects.filter(id=place_id, is_active=True).first()
        if not place:
            raise serializers.ValidationError({"place_id": "مکان مورد نظر یافت نشد."})

        # قانون بیزینس: هر کاربر تنها ۱ بازخورد به ازای هر مکان
        if Review.objects.filter(user=user, place=place).exists():
            raise serializers.ValidationError({"detail": "شما قبلاً برای این مکان بازخورد ثبت کرده‌اید."})

        if not attrs.get('answers'):
            raise serializers.ValidationError({"answers": "حداقل باید به یک سوال پاسخ دهید."})

        # بررسی تکراری نبودن پاسخ به یک سوال در یک درخواست
        question_ids = [ans['question_id'] for ans in attrs['answers']]
        if len(question_ids) != len(set(question_ids)):
            raise serializers.ValidationError({"answers": "برای هر سوال تنها می‌توانید یک گزینه را انتخاب کنید."})

        attrs['place_obj'] = place
        return attrs

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        place = validated_data.pop('place_obj')
        validated_data.pop('place_id')
        user = self.context['request'].user

        with transaction.atomic():
            review = Review.objects.create(
                user=user,
                place=place,
                status=ReviewStatus.APPROVED,
                comment=validated_data.get('comment', '')
            )

            for item in answers_data:
                Answer.objects.create(
                    review=review,
                    question=item['question_obj'],
                    option=item['option_obj']
                )

        return review


class ReportCreateSerializer(serializers.ModelSerializer):
    """سریالایزر ارسال گزارش مشکل یا پیشنهاد توسط کاربر"""
    place_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Report
        fields = ('id', 'place_id', 'report_type', 'reason', 'description', 'created_at')
        read_only_fields = ('id', 'created_at')

    def validate_place_id(self, value):
        if not Place.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("مکان مورد نظر یافت نشد.")
        return value

    def create(self, validated_data):
        place_id = validated_data.pop('place_id')
        place = Place.objects.get(id=place_id)
        user = self.context['request'].user
        return Report.objects.create(user=user, place=place, **validated_data)