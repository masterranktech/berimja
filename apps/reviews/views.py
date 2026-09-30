from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ReportCreateSerializer, ReviewCreateSerializer


class ReviewCreateView(APIView):
    """ثبت بازخورد جدید ساختاریافته (نیاز به لاگین)"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ReviewCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        review = serializer.save()
        return Response({
            "message": "بازخورد شما با موفقیت ثبت شد و در آمار مکان لحاظ گردید.",
            "review_id": review.id
        }, status=status.HTTP_201_CREATED)


class ReportCreateView(APIView):
    """ثبت گزارش یا پیشنهاد برای مکان (نیاز به لاگین)"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ReportCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        report = serializer.save()
        return Response({
            "message": "گزارش شما با موفقیت ثبت شد و توسط مدیران بررسی خواهد شد.",
            "report_id": report.id
        }, status=status.HTTP_201_CREATED)