from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Count
from apps.places.models import Category, Place
from apps.questions.models import Section
from apps.reviews.models import Review, ReviewStatus
from apps.tags.models import Tag


def home_page_view(request):
    """رندر سمت سرور صفحه اصلی همراه با فیلتر ترکیبی دسته‌بندی، تگ‌ها و سرچ متنی"""
    selected_category = request.GET.get('category', '').strip()
    active_tag = request.GET.get('tag', '').strip()
    search_query = request.GET.get('q', '').strip()

    selected_category_obj = None
    if selected_category:
        selected_category_obj = Category.objects.filter(slug=selected_category, is_active=True).first()

    # ۱. کوئری پایه مکان‌های فعال همراه با واکشی روابط
    places_qs = Place.objects.filter(is_active=True).prefetch_related(
        'categories',
        'place_tags__tag',
        'images'
    ).order_by('-created_at')

    # ۲. اعمال فیلتر دسته‌بندی
    if selected_category:
        places_qs = places_qs.filter(categories__slug=selected_category)

    # ۳. اعمال همزمان فیلتر تگ (ترکیب با دسته‌بندی)
    if active_tag:
        places_qs = places_qs.filter(
            place_tags__tag__name=active_tag,
            place_tags__is_active=True
        )

    # ۴. اعمال جستجوی متنی
    if search_query:
        places_qs = places_qs.filter(name__icontains=search_query)

    places_qs = places_qs.distinct()

    # ۵. کنترل تعداد موارد نمایشی جهت بهینه‌سازی تجربه کاربری
    has_filter = bool(selected_category or active_tag or search_query)
    total_count = places_qs.count()

    if not has_filter:
        places_list = places_qs[:6]
    else:
        places_list = places_qs[:12]

    # ۶. واکشی پرکاربردترین دسته‌ها
    popular_categories = Category.objects.filter(is_active=True).annotate(
        places_count=Count('places')
    ).order_by('-places_count', 'name')[:5]

    # ۷. تگ‌های تجربی فعال برای نوار فیلتر حسی
    quick_tags = Tag.objects.filter(status='ACTIVE')[:10]

    context = {
        'places': places_list,
        'total_count': total_count,
        'has_filter': has_filter,
        'categories': popular_categories,
        'selected_category': selected_category,
        'selected_category_obj': selected_category_obj,
        'quick_tags': quick_tags,
        'active_tag': active_tag,
        'search_query': search_query,
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

