# apps/accounts/tests.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.accounts.models import CustomUser, OTPRequest


class AccountAuthTests(APITestCase):
    def setUp(self):
        self.phone_number = "09121111111"
        self.send_otp_url = reverse('accounts:otp_send')
        self.verify_otp_url = reverse('accounts:otp_verify')
        self.profile_url = reverse('accounts:profile')

    def test_send_otp_success(self):
        """ارسال موفق کد یک‌بارمصرف با شماره معتبر"""
        response = self.client.post(self.send_otp_url, {"phone_number": self.phone_number})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(OTPRequest.objects.filter(phone_number=self.phone_number, is_used=False).exists())

    def test_send_otp_invalid_phone_format(self):
        """اعتبارسنجی فرمت نامعتبر شماره موبایل"""
        response = self.client.post(self.send_otp_url, {"phone_number": "12345"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_verify_otp_success_and_jwt_generation(self):
        """تایید صحیح کد OTP و صدور توکن‌های دسترسی"""
        otp = OTPRequest.generate_code(phone_number=self.phone_number, validity_minutes=2)
        response = self.client.post(self.verify_otp_url, {
            "phone_number": self.phone_number,
            "code": otp.code
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertTrue(CustomUser.objects.filter(phone_number=self.phone_number).exists())

        # بررسی باطل شدن کد بعد از مصرف
        otp.refresh_from_db()
        self.assertTrue(otp.is_used)

    def test_verify_otp_wrong_code(self):
        """تلاش برای تایید با کد اشتباه"""
        OTPRequest.generate_code(phone_number=self.phone_number, validity_minutes=2)
        response = self.client.post(self.verify_otp_url, {
            "phone_number": self.phone_number,
            "code": "999999"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_profile_access_with_jwt(self):
        """دسترسی به پروفایل کاربری با توکن لاگین"""
        user = CustomUser.objects.create(phone_number=self.phone_number, display_name="تست کننده")
        self.client.force_authenticate(user=user)

        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["phone_number"], self.phone_number)