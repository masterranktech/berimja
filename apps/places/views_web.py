from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from apps.places.models import Place
from apps.questions.models import Section
from apps.reviews.models import Review, ReviewStatus
from apps.tags.models import Tag


def home_page_view(request):
    """رندر سمت سرور (SSR) صفحه اصلی همراه با تگ‌ها و فیلتر سریع"""
    active_tag = request.GET.get('tag', '').strip()

    # واکشی بهینه مکان‌ها به همراه تگ‌ها، تصاویر و دسته‌ها (جلوگیری از مشکل N+1)
    places_qs = Place.objects.filter(is_active=True).prefetch_related(
        'categories',
        'place_tags__tag',
        'images'
    ).order_by('-created_at')

    # اعمال فیلتر سریع در صورت انتخاب کاربر
    if active_tag:
        places_qs = places_qs.filter(
            place_tags__tag__name=active_tag,
            place_tags__is_active=True
        ).distinct()

    # دریافت ۸ تگ پرتکرار و فعال برای فیلترهای سریع بالای صفحه
    quick_tags = Tag.objects.filter(status='ACTIVE')[:8]

    context = {
        'places': places_qs,
        'quick_tags': quick_tags,
        'active_tag': active_tag,
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