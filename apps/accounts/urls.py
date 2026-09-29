from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import OTPSendView, OTPVerifyView, UserProfileView

app_name = 'accounts'

urlpatterns = [
    path('otp/send/', OTPSendView.as_view(), name='otp_send'),
    path('otp/verify/', OTPVerifyView.as_view(), name='otp_verify'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='profile'),
]