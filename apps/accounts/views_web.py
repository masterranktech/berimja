from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from apps.accounts.models import CustomUser, OTPRequest, phone_regex
from django.core.exceptions import ValidationError

def login_phone_view(request):
    """مرحله اول: دریافت شماره موبایل و ارسال کد OTP"""
    if request.user.is_authenticated:
        return redirect('places_web:home')

    if request.method == 'POST':
        phone = request.POST.get('phone_number', '').strip()
        try:
            phone_regex(phone)
        except ValidationError:
            messages.error(request, 'شماره موبایل واردشده نامعتبر است. نمونه صحیح: ۰۹۱۲۳۴۵۶۷۸۹')
            return render(request, 'accounts/login_phone.html')

        # ابطال کدهای قبلی و صدور کد ۲ دقیقه‌ای
        OTPRequest.objects.filter(phone_number=phone, is_used=False).update(is_used=True)
        otp = OTPRequest.generate_code(phone_number=phone, validity_minutes=2)

        # پرینت در ترمینال (یا ارسال از طریق وب‌سرویس SMS)
        print(f"\n[OTP Web Console] کد ورود به سایت برای {phone}: {otp.code}\n")

        # ذخیره موقت شماره در سشن برای مرحله تایید
        request.session['auth_phone_number'] = phone
        return redirect('accounts_web:verify_code')

    return render(request, 'accounts/login_phone.html')


def verify_code_view(request):
    """مرحله دوم: اعتبارسنجی کد یک‌بارمصرف و ورود با سشن سروری امن"""
    phone = request.session.get('auth_phone_number')
    if not phone:
        return redirect('accounts_web:login_phone')

    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        otp_req = OTPRequest.objects.filter(phone_number=phone, code=code, is_used=False).order_by('-created_at').first()

        if not otp_req or otp_req.is_expired:
            messages.error(request, 'کد تأیید نامعتبر یا منقضی شده است.')
            return render(request, 'accounts/verify_code.html', {'phone_number': phone})

        otp_req.is_used = True
        otp_req.save()

        user, _ = CustomUser.objects.get_or_create(phone_number=phone)
        if user.is_blocked:
            messages.error(request, 'حساب کاربری شما مسدود شده است.')
            return redirect('accounts_web:login_phone')

        # ورود امن سروری جنگو (تنظیم کوکی HttpOnly امن)
        login(request, user)
        del request.session['auth_phone_number']

        next_url = request.GET.get('next') or 'places_web:home'
        return redirect(next_url)

    return render(request, 'accounts/verify_code.html', {'phone_number': phone})


def logout_view(request):
    """خروج و انقضای نشست سروری"""
    logout(request)
    return redirect('places_web:home')