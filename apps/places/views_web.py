from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Count, Q
from apps.places.models import Category, Place
from apps.questions.models import Section
from apps.reviews.models import Review, ReviewStatus
from apps.tags.models import Tag
from django.http import JsonResponse
import json
from apps.reviews.models import Report, ReportType, ReportStatus


def home_page_view(request):
    """رندر سمت سرور صفحه اصلی همراه با فیلتر ترکیبی دسته‌بندی، تگ‌ها، سرچ متنی، کلکسیون‌ها و فیلتر مناطق"""
    selected_category = request.GET.get('category', '').strip()
    active_tag = request.GET.get('tag', '').strip()
    search_query = request.GET.get('q', '').strip()
    active_tab = request.GET.get('tab', 'popular').strip() or 'popular'
    selected_collection = request.GET.get('collection', '').strip()
    selected_district = request.GET.get('district', '').strip()
    selected_price = request.GET.get('price', '').strip()  # <--- فیلتر جدید سطح قیمت

    # ۱. استخراج شیء دسته‌بندی
    selected_category_obj = None
    if selected_category:
        selected_category_obj = Category.objects.filter(slug=selected_category, is_active=True).first()

    # ۲. کوئری پایه مکان‌های فعال
    places_qs = Place.objects.filter(is_active=True).prefetch_related(
        'categories',
        'place_tags__tag',
        'images'
    ).annotate(
        total_reviews_count=Count('reviews', filter=Q(reviews__status='APPROVED'))
    )

    # ۳. اعمال فیلتر سطح قیمت بر اساس تگ‌های معنایی مدل
    if selected_price == 'economic':
        places_qs = places_qs.filter(
            place_tags__tag__name__in=['اقتصادی', 'اقتصادی و دانشجویی'],
            place_tags__is_active=True
        )
    elif selected_price == 'medium':
        places_qs = places_qs.filter(
            place_tags__tag__name__in=['قیمت متوسط', 'متوسط', 'متوسط و معقول'],
            place_tags__is_active=True
        )
    elif selected_price == 'luxury':
        places_qs = places_qs.filter(
            place_tags__tag__name__in=['گران و لوکس', 'گران'],
            place_tags__is_active=True
        )

    # ۴. اعمال فیلتر دسته‌بندی
    if selected_category:
        places_qs = places_qs.filter(categories__slug=selected_category)

    # ۵. اعمال فیلتر تگ تجربی
    if active_tag:
        places_qs = places_qs.filter(
            place_tags__tag__name=active_tag,
            place_tags__is_active=True
        )

    # ۶. اعمال فیلتر محدوده و منطقه شهری
    if selected_district:
        places_qs = places_qs.filter(district__iexact=selected_district)

    # ۷. فیلتر کلکسیون‌های سناریومحور
    if selected_collection == 'work':
        places_qs = places_qs.filter(
            place_tags__tag__name__in=['مناسب مطالعه', 'خلوت', 'دنج'],
            place_tags__is_active=True
        )
    elif selected_collection == 'night':
        places_qs = places_qs.filter(
            working_hours__iregex=r'(24|۲۴|بامداد|شب)'
        )
    elif selected_collection == 'outdoor':
        places_qs = places_qs.filter(
            place_tags__tag__name__in=['فضای باز', 'حیاط'],
            place_tags__is_active=True
        )

    # ۸. جستجوی متنی هیرو
    if search_query:
        places_qs = places_qs.filter(name__icontains=search_query)

    # ۹. اعمال فیلتر و مرتب‌سازی تب‌های تعاملی ویترین
    if active_tab == 'latest':
        places_qs = places_qs.order_by('-created_at')
    elif active_tab == 'cozy':
        places_qs = places_qs.filter(
            place_tags__tag__name__in=['خلوت', 'دنج', 'خلوت و آرام'],
            place_tags__is_active=True
        ).order_by('-place_tags__strength', '-created_at')
    else:
        active_tab = 'popular'
        places_qs = places_qs.annotate(
            approved_reviews_count=Count('reviews', filter=Q(reviews__status='APPROVED'))
        ).order_by('-approved_reviews_count', '-created_at')

    places_qs = places_qs.distinct()

    # ۱۰. استخراج مناطق پرپاتوق
    available_districts = (
        Place.objects.filter(is_active=True)
        .exclude(district__isnull=True)
        .exclude(district__exact='')
        .values('district')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    has_filter = bool(
        selected_category or active_tag or search_query or
        selected_district or selected_collection or selected_price
    )
    total_count = places_qs.count()
    places_list = places_qs[:6] if not has_filter else places_qs[:12]

    popular_categories = Category.objects.filter(is_active=True).annotate(
        places_count=Count('places')
    ).order_by('-places_count', 'name')[:5]

    quick_tags = Tag.objects.filter(status='ACTIVE')[:10]

    recent_reviews = (
        Review.objects.filter(
            status=ReviewStatus.APPROVED,
            place__is_active=True
        )
        .exclude(comment__isnull=True)
        .exclude(comment__exact='')
        .select_related('user', 'place')
        .order_by('-created_at')[:6]
    )

    context = {
        'places': places_list,
        'total_count': total_count,
        'has_filter': has_filter,
        'active_tab': active_tab,
        'categories': popular_categories,
        'selected_category': selected_category,
        'selected_category_obj': selected_category_obj,
        'quick_tags': quick_tags,
        'active_tag': active_tag,
        'search_query': search_query,
        'selected_collection': selected_collection,
        'selected_district': selected_district,
        'available_districts': available_districts,
        'selected_price': selected_price,
        'recent_reviews': recent_reviews,
    }
    return render(request, 'places/home.html', context)


def place_detail_page_view(request, id):
    """رندر سمت سرور (SSR) صفحه کامل جزئیات مکان همراه با نظرات تاییدشده"""
    place = get_object_or_404(
        Place.objects.prefetch_related(
            'categories',
            'images',
            'place_tags__tag',
            'reviews__user'
        ),
        id=id,
        is_active=True
    )

    # تگ‌های فعال با اطمینان آماری مرتب‌شده
    active_tags = place.place_tags.filter(
        is_active=True,
        tag__status='ACTIVE'
    ).select_related('tag').order_by('-strength')

    # نظرات تاییدشده همراه با نظر متنی
    approved_reviews = place.reviews.filter(
        status=ReviewStatus.APPROVED
    ).exclude(comment__isnull=True).exclude(comment__exact='').select_related('user').order_by('-created_at')

    context = {
        'place': place,
        'active_tags': active_tags,
        'approved_reviews': approved_reviews,
    }
    return render(request, 'places/place_detail.html', context)


def place_questionnaire_page_view(request, id):
    """رندر سروری صفحه پرسشنامه با پشتیبانی از بازخورد قبلی جهت ویرایش"""
    place = get_object_or_404(Place.objects.prefetch_related('categories'), id=id, is_active=True)

    # ۱. بررسی ورود کاربر
    if not request.user.is_authenticated:
        messages.info(request, 'برای ثبت یا ویرایش تجربه و بازخورد ابتدا وارد حساب کاربری خود شوید.')
        return redirect(f"/accounts/login/?next={request.path}")

    # ۲. واکشی بازخورد قبلی کاربر در صورت وجود (پشتیبانی از ویرایش به جای مسدود کردن)
    existing_review = Review.objects.filter(user=request.user, place=place).prefetch_related('answers').first()

    # ساخت نگاشت پاسخ‌های قبلی: {question_id: option_id}
    user_answers_map = {}
    if existing_review:
        user_answers_map = {ans.question_id: ans.option_id for ans in existing_review.answers.all()}

    # ۳. واکشی بخش‌ها و سوالات متناسب با دسته‌بندی‌های مکان
    place_categories = place.categories.all()
    sections = Section.objects.prefetch_related('questions__options').order_by('sort_order', 'id')

    questionnaire_sections = []
    for sec in sections:
        matched_questions = sec.questions.filter(is_active=True).filter(
            categories__in=place_categories
        ) | sec.questions.filter(is_active=True, is_general=True)

        distinct_questions = matched_questions.distinct().order_by('sort_order', 'id')
        if distinct_questions.exists():
            questionnaire_sections.append({
                'section': sec,
                'questions': distinct_questions
            })

    context = {
        'place': place,
        'questionnaire_sections': questionnaire_sections,
        'existing_review': existing_review,
        'user_answers_map': user_answers_map,
    }
    return render(request, 'places/questionnaire.html', context)


def random_place_view(request):
    """انتخاب یک مکان تصادفی با اولویت مکان‌های دارای بازخورد و تگ فعال و هدایت کاربر به آن"""
    # ۱. اولویت با مکان‌های فعال و باکیفیتی که تگ فعال دارند
    random_place = Place.objects.filter(
        is_active=True,
        place_tags__is_active=True
    ).distinct().order_by('?').first()

    # ۲. در صورت خالی بودن شرط اول، فال‌بک به تمام مکان‌های فعال
    if not random_place:
        random_place = Place.objects.filter(is_active=True).order_by('?').first()

    # ۳. اگر مکانی وجود داشت ریدایرکت کن، در غیر این صورت به صفحه اصلی برگردان
    if random_place:
        return redirect('places_web:place_detail', id=random_place.id)

    messages.info(request, 'در حال حاضر مقصدی برای پیشنهاد تصادفی یافت نشد.')
    return redirect('places_web:home')


from django.shortcuts import render, redirect
from django.contrib import messages
from apps.places.models import Category, Place
from apps.reviews.models import Report, ReportType, ReportStatus


def suggest_place_page_view(request):
    """صفحه اختصاصی و مستقل معرفی و پیشنهاد مکان جدید توسط کاربر"""
    if not request.user.is_authenticated:
        messages.info(request, 'برای معرفی مکان جدید، لطفاً ابتدا وارد حساب کاربری خود شوید.')
        return redirect(f"/accounts/login/?next={request.path}")

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        district = request.POST.get('district', '').strip()
        category = request.POST.get('category', '').strip()
        address = request.POST.get('address', '').strip()
        notes = request.POST.get('notes', '').strip()

        if not name or not district or not address:
            messages.error(request, 'لطفاً نام، منطقه و نشانی مکان را به طور کامل وارد کنید.')
            return render(request, 'places/suggest_place.html', {
                'categories': Category.objects.filter(is_active=True),
                'form_data': request.POST
            })

        reason_text = f"پیشنهاد مکان جدید: {name} ({district})"
        description_text = (
            f"نام مکان: {name}\n"
            f"دسته‌بندی: {category}\n"
            f"منطقه / محله: {district}\n"
            f"نشانی دقیق: {address}\n"
            f"توضیحات و ویژگی‌ها: {notes}"
        )

        # ثبت پیشنهاد کاملاً مستقل و بدون اتصال به مکان‌های قبلی
        Report.objects.create(
            user=request.user,
            place=None,  # <--- بدون مکان مرتبط
            report_type=ReportType.SUGGESTION,
            reason=reason_text[:200],
            description=description_text,
            status=ReportStatus.PENDING
        )

        messages.success(request, 'پیشنهاد شما با موفقیت ثبت شد و پس از بررسی تیم بریم‌جا به لیست پاتوق‌ها اضافه خواهد شد.')
        return redirect('places_web:home')

    categories = Category.objects.filter(is_active=True)
    return render(request, 'places/suggest_place.html', {'categories': categories})