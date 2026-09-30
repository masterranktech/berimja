# apps/accounts/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, serializers
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, inline_serializer

from .serializers import OTPSendSerializer, OTPVerifySerializer, UserProfileSerializer
from .models import CustomUser, OTPRequest
from .throttling import OTPSendPhoneThrottle, OTPSendIPThrottle


class OTPSendView(APIView):
    """ارسال کد یک‌بارمصرف به شماره موبایل کاربر همراه با محدودکننده نرخ درخواست"""
    permission_classes = [permissions.AllowAny]
    throttle_classes = [OTPSendPhoneThrottle, OTPSendIPThrottle]

    @extend_schema(
        tags=['Accounts'],
        request=OTPSendSerializer,
        responses={
            200: inline_serializer(
                name='OTPSendResponse',
                fields={'message': serializers.CharField()}
            )
        },
        summary="ارسال پیامک کد یک‌بارمصرف (OTP)"
    )
    def post(self, request):
        serializer = OTPSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        OTPRequest.objects.filter(phone_number=phone_number, is_used=False).update(is_used=True)
        otp = OTPRequest.generate_code(phone_number=phone_number, validity_minutes=2)

        print(f"\n[OTP Console] کد ورود برای {phone_number}: {otp.code}\n")

        return Response(
            {"message": "کد تأیید برای شماره شما ارسال شد."},
            status=status.HTTP_200_OK
        )


class OTPVerifyView(APIView):
    """بررسی کد یک‌بارمصرف و صدور توکن JWT"""
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=['Accounts'],
        request=OTPVerifySerializer,
        responses={
            200: inline_serializer(
                name='OTPVerifyResponse',
                fields={
                    'refresh': serializers.CharField(),
                    'access': serializers.CharField(),
                    'user': UserProfileSerializer()
                }
            )
        },
        summary="بررسی کد تأیید و صدور توکن دسترسی"
    )
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        code = serializer.validated_data['code']

        otp_request = OTPRequest.objects.filter(
            phone_number=phone_number,
            code=code,
            is_used=False
        ).order_by('-created_at').first()

        # بررسی وجود کد و منقضی نشدن آن با پراپرتی is_expired
        if not otp_request or otp_request.is_expired:
            return Response(
                {"detail": "کد تأیید نامعتبر یا منقضی شده است."},
                status=status.HTTP_400_BAD_REQUEST
            )

        otp_request.is_used = True
        otp_request.save()

        user, _ = CustomUser.objects.get_or_create(phone_number=phone_number)
        if user.is_blocked:
            return Response(
                {"detail": "حساب کاربری شما مسدود شده است."},
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserProfileSerializer(user).data
        }, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    """مشاهده و ویرایش مشخصات پروفایل کاربر"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=['Accounts'], responses=UserProfileSerializer, summary="مشاهده پروفایل کاربر جاری")
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(tags=['Accounts'], request=UserProfileSerializer, responses=UserProfileSerializer, summary="ویرایش پروفایل")
    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)