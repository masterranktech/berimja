# apps/reviews/tests.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import CustomUser
from apps.places.models import Place
from apps.questions.models import Section, Question, QuestionOption
from apps.reviews.models import Review, Answer


class ReviewEndpointTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(phone_number="09121111111")
        self.place = Place.objects.create(name="کافه تست", address="تهران")
        self.section = Section.objects.create(title="عمومی")
        self.question = Question.objects.create(
            section=self.section,
            text="سطح قیمت؟",
            is_general=True
        )
        self.option = QuestionOption.objects.create(question=self.question, title="اقتصادی", value=1)
        self.review_url = reverse('reviews:review_create')

    def test_review_creation_requires_login(self):
        """عدم دسترسی به ثبت بازخورد بدون احراز هویت"""
        payload = {
            "place_id": self.place.id,
            "comment": "عالی",
            "answers": [{"question_id": self.question.id, "option_id": self.option.id}]
        }
        response = self.client.post(self.review_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_submit_review_success(self):
        """ثبت بازخورد موفق به همراه ذخیره اتمیک پاسخ‌ها"""
        self.client.force_authenticate(user=self.user)
        payload = {
            "place_id": self.place.id,
            "comment": "بسیار خوب",
            "answers": [{"question_id": self.question.id, "option_id": self.option.id}]
        }
        response = self.client.post(self.review_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.filter(user=self.user, place=self.place).count(), 1)
        self.assertEqual(Answer.objects.filter(question=self.question, option=self.option).count(), 1)

    def test_duplicate_review_prevention(self):
        """جلوگیری از ثبت بازخورد تکراری توسط همان کاربر برای همان مکان"""
        self.client.force_authenticate(user=self.user)
        payload = {
            "place_id": self.place.id,
            "answers": [{"question_id": self.question.id, "option_id": self.option.id}]
        }

        # ثبت اول
        first_resp = self.client.post(self.review_url, payload, format='json')
        self.assertEqual(first_resp.status_code, status.HTTP_201_CREATED)

        # ثبت مجدد
        second_resp = self.client.post(self.review_url, payload, format='json')
        self.assertEqual(second_resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Review.objects.filter(user=self.user, place=self.place).count(), 1)