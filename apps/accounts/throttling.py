from rest_framework.throttling import AnonRateThrottle, SimpleRateThrottle


class OTPSendPhoneThrottle(SimpleRateThrottle):
    """
    محدودسازی ارسال پیامک بر اساس شماره موبایل دریافت شده در بدنه درخواست
    """
    scope = 'otp_send_phone'

    def get_cache_key(self, request, view):
        phone_number = request.data.get('phone_number')
        if not phone_number:
            return None  # اعتبارسنجی فرمت را به سریالایزر واگذار می‌کند
        return self.cache_format % {
            'scope': self.scope,
            'ident': phone_number.strip()
        }


class OTPSendIPThrottle(AnonRateThrottle):
    """
    محدودسازی تعداد کل درخواست‌های ارسال پیامک بر اساس IP درخواست‌دهنده
    """
    scope = 'otp_send_ip'