# apps/tags/tests.py
from django.test import TestCase

from apps.accounts.models import CustomUser
from apps.places.models import Place
from apps.questions.models import Section, Question, QuestionOption
from apps.reviews.models import Review, Answer, ReviewStatus
from apps.tags.models import Tag, PlaceTag, TagRule, TagSource
from apps.tags.services import TagAggregationService


class TagAggregationServiceTests(TestCase):
    def setUp(self):
        self.place = Place.objects.create(name="رستوران تست", address="تهران")
        self.section = Section.objects.create(title="عمومی")
        self.question = Question.objects.create(section=self.section, text="میزان شلوغی؟")
        self.opt_quiet = QuestionOption.objects.create(question=self.question, title="خلوت", value=1)
        self.opt_busy = QuestionOption.objects.create(question=self.question, title="شلوغ", value=2)

        self.tag_quiet = Tag.objects.create(name="خلوت و آرام")

        # قانون: حداقل ۲ رای، حداقل ۵۰٪ برای تگ «خلوت و آرام»
        self.rule = TagRule.objects.create(
            question=self.question,
            option=self.opt_quiet,
            target_tag=self.tag_quiet,
            threshold_percentage=50,
            minimum_votes=2
        )

        self.user1 = CustomUser.objects.create(phone_number="09121111111")
        self.user2 = CustomUser.objects.create(phone_number="09122222222")

    def test_aggregation_does_not_activate_below_minimum_votes(self):
        """اگر تعداد آرا به حد نصاب نرسد، تگ ساخته نمی‌شود"""
        review = Review.objects.create(user=self.user1, place=self.place, status=ReviewStatus.APPROVED)
        Answer.objects.create(review=review, question=self.question, option=self.opt_quiet)

        TagAggregationService.calculate_tags_for_place(self.place)
        self.assertFalse(PlaceTag.objects.filter(place=self.place, tag=self.tag_quiet).exists())

    def test_aggregation_activates_tag_when_threshold_met(self):
        """با رسیدن تعداد آرا به حداقل و تامین درصد، تگ خودکار ساخته می‌شود"""
        # کاربر ۱ رای خلوت می‌دهد
        r1 = Review.objects.create(user=self.user1, place=self.place, status=ReviewStatus.APPROVED)
        Answer.objects.create(review=r1, question=self.question, option=self.opt_quiet)

        # کاربر ۲ نیز رای خلوت می‌دهد
        r2 = Review.objects.create(user=self.user2, place=self.place, status=ReviewStatus.APPROVED)
        Answer.objects.create(review=r2, question=self.question, option=self.opt_quiet)

        # سیگنال‌ها یا فراخوانی مستقیم
        TagAggregationService.calculate_tags_for_place(self.place)

        place_tag = PlaceTag.objects.filter(place=self.place, tag=self.tag_quiet).first()
        self.assertIsNotNone(place_tag)
        self.assertTrue(place_tag.is_active)
        self.assertEqual(place_tag.source, TagSource.AUTO)
        self.assertEqual(place_tag.strength, 100)