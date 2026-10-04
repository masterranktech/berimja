import re
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from apps.accounts.models import CustomUser, OTPRequest, phone_regex
from django.core.exceptions import ValidationError

def login_phone_view(request):
    """مرحله ۱: دریافت شماره تلفن و ارسال OTP"""
    if request.user.is_authenticated:
        return redirect('places_web:home')

    if request.method == 'POST':
        phone = request.POST.get('phone_number', '').strip()
        try:
            phone_regex(phone)
        except ValidationError:
            messages.error(request, 'شماره موبایل واردشده نامعتبر است. نمونه صحیح: ۰۹۱۲۳۴۵۶۷۸۹')
            return render(request, 'accounts/login_phone.html')

        OTPRequest.objects.filter(phone_number=phone, is_used=False).update(is_used=True)
        otp = OTPRequest.generate_code(phone_number=phone, validity_minutes=2)

        print(f"\n[OTP Web Console] کد ورود به سایت برای {phone}: {otp.code}\n")

        request.session['auth_phone_number'] = phone
        return redirect('accounts_web:verify_code')

    return render(request, 'accounts/login_phone.html')


def verify_code_view(request):
    """مرحله ۲: بررسی کد. اگر کاربر قبلاً ثبت شده -> ورود مستقیم به خانه؛ اگر جدید است -> مرحله انتخاب نام"""
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

        # بررسی وجود کاربر از قبل
        user = CustomUser.objects.filter(phone_number=phone).first()

        if user:
            # کاربر قبلی است و نام دارد -> ورود مستقیم
            if user.is_blocked:
                messages.error(request, 'حساب کاربری شما مسدود شده است.')
                return redirect('accounts_web:login_phone')

            login(request, user)
            del request.session['auth_phone_number']
            return redirect('places_web:home')
        else:
            # کاربر جدید است -> علامت‌گذاری تأیید شماره و ارسال به مرحله انتخاب نام
            request.session['otp_verified_phone'] = phone
            return redirect('accounts_web:register_name')

    return render(request, 'accounts/verify_code.html', {'phone_number': phone})


def register_name_view(request):
    """مرحله ۳ (فقط کاربران جدید): دریافت نام نمایشی معتبر و ثبت نهایی کاربر"""
    phone = request.session.get('otp_verified_phone')
    if not phone:
        return redirect('accounts_web:login_phone')

    if request.method == 'POST':
        display_name = request.POST.get('display_name', '').strip()

        # اعتبارسنجی: حداقل ۳ کاراکتر
        if len(display_name) < 3:
            messages.error(request, 'نام نمایشی باید حداقل ۳ کاراکتر باشد.')
            return render(request, 'accounts/register_name.html')

        # اعتبارسنجی: عدم استفاده از شماره موبایل یا زنجیره اعداد
        if re.search(r'09\d{9}', display_name) or re.search(r'\d{6,}', display_name):
            messages.error(request, 'استفاده از شماره موبایل یا شماره تماس به عنوان نام نمایشی مجاز نیست.')
            return render(request, 'accounts/register_name.html')

        # ساخت کاربر با نام و شماره
        user = CustomUser.objects.create_user(
            phone_number=phone,
            display_name=display_name
        )

        login(request, user)
        # پاکسازی سشن‌های موقت
        if 'auth_phone_number' in request.session:
            del request.session['auth_phone_number']
        del request.session['otp_verified_phone']

        return redirect('places_web:home')

    return render(request, 'accounts/register_name.html')


def logout_view(request):
    logout(request)
    return redirect('places_web:home')