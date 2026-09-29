from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, OTPRequest
from .serializers import OTPSendSerializer, OTPVerifySerializer, UserProfileSerializer


class OTPSendView(APIView):
    """ارسال کد یک‌بارمصرف به شماره موبایل کاربر"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OTPSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']

        # ابطال کدهای استفاده‌نشده قبلی برای این شماره
        OTPRequest.objects.filter(phone_number=phone_number, is_used=False).update(is_used=True)

        # تولید کد جدید ۲ دقیقه‌ای
        otp = OTPRequest.generate_code(phone_number=phone_number, validity_minutes=2)

        # در محیط توسعه کد در ترمینال پرینت می‌شود (در پروداکشن وب‌سرویس SMS فراخوانی خواهد شد)
        print(f"\n==========================================")
        print(f"[OTP Console] کد ورود برای {phone_number}: {otp.code}")
        print(f"==========================================\n")

        return Response(
            {"message": "کد تأیید برای شماره شما ارسال شد."},
            status=status.HTTP_200_OK
        )


class OTPVerifyView(APIView):
    """اعتبارسنجی کد ارسالی و صدور توکن‌های JWT"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        code = serializer.validated_data['code']

        otp_request = OTPRequest.objects.filter(
            phone_number=phone_number,
            code=code,
            is_used=False
        ).first()

        if not otp_request:
            return Response(
                {"error": "کد واردشده نامعتبر است."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if otp_request.is_expired:
            return Response(
                {"error": "کد تایید منقضی شده است. لطفاً مجدداً درخواست دهید."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # علامت‌گذاری کد به عنوان استفاده‌شده
        otp_request.is_used = True
        otp_request.save()

        # بازیابی یا ساخت کاربر
        user, _ = CustomUser.objects.get_or_create(phone_number=phone_number)

        if user.is_blocked:
            return Response(
                {"error": "حساب کاربری شما مسدود شده است."},
                status=status.HTTP_403_FORBIDDEN
            )

        # تولید توکن JWT
        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserProfileSerializer(user).data
        }, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    """دریافت و ویرایش نام نمایشی کاربر جاری"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)