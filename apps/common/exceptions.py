# apps/common/exceptions.py
from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.exceptions import Throttled


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        custom_data = {
            "success": False,
            "status_code": response.status_code,
            "message": "خطایی رخ داده است.",
            "errors": None
        }

        # سفارشی‌سازی خطای Throttling (کد 429)
        if isinstance(exc, Throttled):
            wait_seconds = int(exc.wait) if exc.wait is not None else 60
            custom_data["message"] = f"تعداد درخواست‌ها بیش از حد مجاز است. لطفاً {wait_seconds} ثانیه دیگر مجدداً تلاش کنید."
            custom_data["errors"] = {
                "available_in_seconds": wait_seconds
            }
        elif response.status_code == status.HTTP_400_BAD_REQUEST:
            custom_data["message"] = "اطلاعات ارسالی نامعتبر است."
            custom_data["errors"] = response.data
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            custom_data["message"] = "برای دسترسی به این بخش باید وارد حساب کاربری خود شوید."
            custom_data["errors"] = response.data
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            custom_data["message"] = "شما دسترسی لازم برای انجام این عملیات را ندارید."
            custom_data["errors"] = response.data
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            custom_data["message"] = "مورد درخواستی یافت نشد."
            custom_data["errors"] = response.data
        else:
            custom_data["errors"] = response.data

        response.data = custom_data

    return response