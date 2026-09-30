import random
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import CustomUser
from apps.places.models import Category, Place
from apps.questions.models import Section, Question, QuestionOption
from apps.tags.models import Tag, PlaceTag, TagRule, TagSource, TagStatus
from apps.reviews.models import Review, Answer, Report, ReviewStatus, ReportType, ReportStatus


class Command(BaseCommand):
    help = "تزریق انبوه داده‌های تستی واقعی و به‌هم‌پیوسته برای تمام مدل‌های پروژه بریم‌جا"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("شروع تولید و ثبت انبوه داده‌های تستی...")

        # -------------------------------------------------------------
        # ۱. کاربران (۱۰ کاربر تستی)
        # -------------------------------------------------------------
        users_raw = [
            ("09121111111", "مهدی محمدی"),
            ("09122222222", "سارا احمدی"),
            ("09123333333", "علی رضایی"),
            ("09124444444", "نیلوفر کریمی"),
            ("09125555555", "حسین کاظمی"),
            ("09126666666", "رویا حسینی"),
            ("09127777777", "امیرحسین تهرانی"),
            ("09128888888", "مهسا کیانی"),
            ("09129999999", "پویا صبوری"),
            ("09120000001", "بهاره راد"),
        ]
        users = []
        for phone, name in users_raw:
            user, _ = CustomUser.objects.get_or_create(
                phone_number=phone,
                defaults={"display_name": name, "is_active": True}
            )
            users.append(user)
        self.stdout.write(f"- تعداد {len(users)} کاربر ثبت شد.")

        # -------------------------------------------------------------
        # ۲. دسته‌بندی‌ها (۶ دسته)
        # -------------------------------------------------------------
        cats_raw = [
            ("cafe", "کافه", "coffee"),
            ("restaurant", "رستوران", "utensils"),
            ("nature", "طبیعت و فضای سبز", "tree"),
            ("entertainment", "تفریح و سرگرمی", "gamepad"),
            ("cinema", "سینما", "film"),
            ("culture", "مکان‌های دیدنی و تاریخی", "landmark"),
        ]
        cats = {}
        for slug, name, icon in cats_raw:
            c, _ = Category.objects.get_or_create(
                slug=slug,
                defaults={"name": name, "icon": icon, "is_active": True}
            )
            cats[slug] = c
        self.stdout.write(f"- تعداد {len(cats)} دسته‌بندی ثبت شد.")

        # -------------------------------------------------------------
        # ۳. تگ‌های معنایی (۱۲ تگ)
        # -------------------------------------------------------------
        tag_list = [
            "اقتصادی", "قیمت متوسط", "گران و لوکس",
            "خلوت و آرام", "بسیار شلوغ", "دنج",
            "فضای باز", "مناسب قرار", "مناسب مطالعه و کار",
            "خانوادگی", "هیجان‌انگیز", "دسترسی به مترو"
        ]
        tags = {}
        for tname in tag_list:
            t, _ = Tag.objects.get_or_create(
                name=tname,
                defaults={"source": TagSource.ADMIN, "status": TagStatus.ACTIVE}
            )
            tags[tname] = t
        self.stdout.write(f"- تعداد {len(tags)} برچسب معنایی ثبت شد.")

        # -------------------------------------------------------------
        # ۴. بخش‌ها و سوالات پرسشنامه
        # -------------------------------------------------------------
        sec_general, _ = Section.objects.get_or_create(title="اطلاعات عمومی", defaults={"sort_order": 1})
        sec_atmosphere, _ = Section.objects.get_or_create(title="فضا و اتمسفر", defaults={"sort_order": 2})
        sec_service, _ = Section.objects.get_or_create(title="کیفیت خدمات و امکانات", defaults={"sort_order": 3})

        # سوال ۱: قیمت (عمومی)
        q_price, _ = Question.objects.get_or_create(
            text="سطح قیمت این مجموعه به چه صورت است؟",
            defaults={"section": sec_general, "is_general": True, "sort_order": 1, "is_active": True}
        )
        opt_p_eco, _ = QuestionOption.objects.get_or_create(question=q_price, title="اقتصادی و دانشجویی", defaults={"value": 1, "sort_order": 1})
        opt_p_mid, _ = QuestionOption.objects.get_or_create(question=q_price, title="متوسط و معقول", defaults={"value": 2, "sort_order": 2})
        opt_p_exp, _ = QuestionOption.objects.get_or_create(question=q_price, title="گران و لوکس", defaults={"value": 3, "sort_order": 3})

        # سوال ۲: شلوغی (عمومی)
        q_crowd, _ = Question.objects.get_or_create(
            text="میزان شلوغی و همهمه محیط چگونه بود؟",
            defaults={"section": sec_atmosphere, "is_general": True, "sort_order": 2, "is_active": True}
        )
        opt_c_quiet, _ = QuestionOption.objects.get_or_create(question=q_crowd, title="خلوت و آرام", defaults={"value": 1, "sort_order": 1})
        opt_c_norm, _ = QuestionOption.objects.get_or_create(question=q_crowd, title="معمولی", defaults={"value": 2, "sort_order": 2})
        opt_c_busy, _ = QuestionOption.objects.get_or_create(question=q_crowd, title="بسیار شلوغ و پرترافیک", defaults={"value": 3, "sort_order": 3})

        # سوال ۳: مناسبت فضا (کافه و رستوران)
        q_suit, _ = Question.objects.get_or_create(
            text="این فضا بیشتر مناسب چه موقعیتی است؟",
            defaults={"section": sec_atmosphere, "is_general": False, "sort_order": 3, "is_active": True}
        )
        q_suit.categories.set([cats["cafe"], cats["restaurant"]])
        opt_s_date, _ = QuestionOption.objects.get_or_create(question=q_suit, title="قرار دو نفره و خاص", defaults={"value": 1, "sort_order": 1})
        opt_s_study, _ = QuestionOption.objects.get_or_create(question=q_suit, title="کار لپ‌تاپی و مطالعه", defaults={"value": 2, "sort_order": 2})
        opt_s_fam, _ = QuestionOption.objects.get_or_create(question=q_suit, title="دورهمی خانوادگی یا دوستانه", defaults={"value": 3, "sort_order": 3})

        # سوال ۴: دسترسی به حمل و نقل (عمومی)
        q_access, _ = Question.objects.get_or_create(
            text="وضعیت دسترسی با حمل و نقل عمومی (مترو و اتوبوس) چطور است؟",
            defaults={"section": sec_service, "is_general": True, "sort_order": 4, "is_active": True}
        )
        opt_a_easy, _ = QuestionOption.objects.get_or_create(question=q_access, title="بسیار نزدیک به مترو یا BRT", defaults={"value": 1, "sort_order": 1})
        opt_a_hard, _ = QuestionOption.objects.get_or_create(question=q_access, title="نیاز به تاکسی یا خودرو شخصی", defaults={"value": 2, "sort_order": 2})

        # سوال ۵: فضای باز (کافه و رستوران و پارک)
        q_outdoor, _ = Question.objects.get_or_create(
            text="آیا امکان نشستن در فضای باز مطلوب وجود دارد؟",
            defaults={"section": sec_atmosphere, "is_general": False, "sort_order": 5, "is_active": True}
        )
        q_outdoor.categories.set([cats["cafe"], cats["restaurant"], cats["nature"]])
        opt_o_yes, _ = QuestionOption.objects.get_or_create(question=q_outdoor, title="بله، حیاط یا تراس بسیار دلنشین", defaults={"value": 1, "sort_order": 1})
        opt_o_no, _ = QuestionOption.objects.get_or_create(question=q_outdoor, title="خیر، فقط سالن سرپوشیده", defaults={"value": 2, "sort_order": 2})

        self.stdout.write("- بخش‌ها، سوالات و گزینه‌ها ایجاد شدند.")

        # -------------------------------------------------------------
        # ۵. قوانین استنتاج تگ‌ها (Tag Rules)
        # -------------------------------------------------------------
        rules_map = [
            (q_price, opt_p_eco, tags["اقتصادی"], 50, 2),
            (q_price, opt_p_mid, tags["قیمت متوسط"], 50, 2),
            (q_price, opt_p_exp, tags["گران و لوکس"], 50, 2),
            (q_crowd, opt_c_quiet, tags["خلوت و آرام"], 50, 2),
            (q_crowd, opt_c_busy, tags["بسیار شلوغ"], 50, 2),
            (q_suit, opt_s_date, tags["مناسب قرار"], 50, 2),
            (q_suit, opt_s_study, tags["مناسب مطالعه و کار"], 50, 2),
            (q_suit, opt_s_fam, tags["خانوادگی"], 50, 2),
            (q_access, opt_a_easy, tags["دسترسی به مترو"], 50, 2),
            (q_outdoor, opt_o_yes, tags["فضای باز"], 50, 2),
        ]
        for q, opt, target, thresh, min_votes in rules_map:
            TagRule.objects.get_or_create(
                question=q, option=opt, target_tag=target,
                defaults={"threshold_percentage": thresh, "minimum_votes": min_votes}
            )
        self.stdout.write("- قوانین استنتاج هوشمند ثبت شدند.")

        # -------------------------------------------------------------
        # ۶. مکان‌های واقعی تهران (۱۵ مکان در دسته‌های مختلف)
        # -------------------------------------------------------------
        places_data = [
            {
                "name": "کافه گودو یاس",
                "district": "منطقه ۶",
                "address": "خیابان نجات‌اللهی، کوچه یاس",
                "description": "کافه‌ای در خانه‌ای قاجاری با حیاط باصفا و حوض آب فیروزه‌ای.",
                "phone": "02188990011",
                "hours": "۸:۳۰ تا ۲۳:۳۰",
                "lat": 35.705120, "lng": 51.413210,
                "cats": [cats["cafe"]],
                "initial_tags": [tags["دنج"], tags["فضای باز"]]
            },
            {
                "name": "رستوران سنتی باغ صبا",
                "district": "منطقه ۱",
                "address": "خیابان شریعتی، بالاتر از پل رومی",
                "description": "رستوران اصیل ایرانی با فضای باز باغی و آلاچیق‌های سنتی.",
                "phone": "02122334455",
                "hours": "۱۲:۰۰ تا ۲۴:۰۰",
                "lat": 35.789210, "lng": 51.431250,
                "cats": [cats["restaurant"]],
                "initial_tags": [tags["خانوادگی"]]
            },
            {
                "name": "پارک جمشیدیه",
                "district": "منطقه ۱",
                "address": "انتهای خیابان باهنر (نیاوران)، خیابان فیضیه",
                "description": "بوستان سنگی کوهپایه‌ای، هوای پاک و چشم‌‌انداز فوق‌العاده شهر تهران.",
                "phone": "02122800000",
                "hours": "۲۴ ساعته",
                "lat": 35.824100, "lng": 51.462300,
                "cats": [cats["nature"]],
                "initial_tags": [tags["فضای باز"], tags["اقتصادی"]]
            },
            {
                "name": "پردیس سینمایی چارسو",
                "district": "منطقه ۱۱",
                "address": "تقاطع خیابان جمهوری و حافظ، طبقه ۷ بازار چارسو",
                "description": "مجموعه مدرن سینمایی با سالن‌های استاندارد و فودکورت بزرگ.",
                "phone": "02166724444",
                "hours": "۱۰:۰۰ تا ۲۴:۰۰",
                "lat": 35.694800, "lng": 51.412400,
                "cats": [cats["cinema"], cats["cafe"]],
                "initial_tags": [tags["دسترسی به مترو"]]
            },
            {
                "name": "کافه کتاب فلسفه",
                "district": "منطقه ۶",
                "address": "خیابان انقلاب، روبروی دانشگاه تهران",
                "description": "فضایی آرام، پر از کتاب و مناسب مطالعه با نور عالی.",
                "phone": "02166400011",
                "hours": "۹:۰۰ تا ۲۱:۳۰",
                "lat": 35.701200, "lng": 51.393400,
                "cats": [cats["cafe"]],
                "initial_tags": [tags["دنج"], tags["مناسب مطالعه و کار"]]
            },
            {
                "name": "پل طبیعت و پارک آب و آتش",
                "district": "منطقه ۳",
                "address": "بزرگراه حقانی، بعد از چهارراه جهان کودک",
                "description": "معماری چشم‌نواز، کافه‌های متعدد، پل پیاده‌روی معلق و گذرگاه محبوب شبانه.",
                "phone": "02188194574",
                "hours": "۶:۰۰ تا ۲۴:۰۰",
                "lat": 35.754700, "lng": 51.420800,
                "cats": [cats["nature"], cats["entertainment"]],
                "initial_tags": [tags["فضای باز"], tags["مناسب قرار"]]
            },
            {
                "name": "کاخ موزه گلستان",
                "district": "منطقه ۱۲",
                "address": "میدان پانزده خرداد، بازار تهران",
                "description": "شاهکار معماری دوره زندیه و قاجار، کاشی‌کاری‌های خیره‌کننده و تالار آینه.",
                "phone": "02133113335",
                "hours": "۹:۰۰ تا ۱۷:۰۰",
                "lat": 35.679800, "lng": 51.420500,
                "cats": [cats["culture"]],
                "initial_tags": [tags["دسترسی به مترو"], tags["خانوادگی"]]
            },
            {
                "name": "مجموعه اتاق فرار انیگما (برج میلاد)",
                "district": "منطقه ۲",
                "address": "بزرگراه همت، گذرگاه ورودی برج میلاد",
                "description": "سناریوهای مهیج، دکور رازآلود و معماهای چندسطحی برای گروه‌های دوستانه.",
                "phone": "02188620365",
                "hours": "۱۴:۰۰ تا ۲۳:۰۰",
                "lat": 35.744800, "lng": 51.375300,
                "cats": [cats["entertainment"]],
                "initial_tags": [tags["هیجان‌انگیز"]]
            },
            {
                "name": "کافه رستوران ویکولو",
                "district": "منطقه ۱",
                "address": "الهیه، خیابان آفریقای شمالی، مجتمع مدرن الهیه",
                "description": "طراحی مشابه کوچه‌های اروپایی، نوشیدنی‌های بار سرد تخصصی و منوی غذایی خاص.",
                "phone": "02126205966",
                "hours": "۹:۰۰ تا ۲۴:۰۰",
                "lat": 35.795100, "lng": 51.422300,
                "cats": [cats["cafe"], cats["restaurant"]],
                "initial_tags": [tags["گران و لوکس"], tags["مناسب قرار"]]
            },
            {
                "name": "دریاچه شهدای خلیج فارس (چیتگر)",
                "district": "منطقه ۲۲",
                "address": "انتهای بزرگراه همت غرب، دریاچه چیتگر",
                "description": "بزرگ‌ترین دریاچه مصنوعی تهران، پیست دوچرخه‌سواری، قایق‌سواری و بام‌لند.",
                "phone": "02144728080",
                "hours": "۶:۰۰ تا ۲۴:۰۰",
                "lat": 35.748200, "lng": 51.218500,
                "cats": [cats["nature"], cats["entertainment"]],
                "initial_tags": [tags["فضای باز"], tags["خانوادگی"]]
            },
            {
                "name": "کافه عمارت بلخ",
                "district": "منطقه ۱۱",
                "address": "خیابان فلسطین، پایین‌تر از جمهوری",
                "description": "عمارت قدیمی بازسازی‌شده با معماری آجری، حیاط مرکزی و نوشیدنی‌های اصیل ایرانی.",
                "phone": "02166487711",
                "hours": "۱۰:۰۰ تا ۲۲:۳۰",
                "lat": 35.696100, "lng": 51.402200,
                "cats": [cats["cafe"]],
                "initial_tags": [tags["دنج"], tags["فضای باز"]]
            },
            {
                "name": "موزه زمان (تماشاگه زمان)",
                "district": "منطقه ۱",
                "address": "زعفرانیه، خیابان سرلشکر فلاحی، نبش کوچه پروین",
                "description": "عمارتی تماشایی با گچ‌بری‌های چشم‌نواز در محاصره باغی مصفا و ساعت‌های تاریخی.",
                "phone": "02122417336",
                "hours": "۹:۰۰ تا ۱۸:۰۰",
                "lat": 35.808300, "lng": 51.417200,
                "cats": [cats["culture"], cats["cafe"]],
                "initial_tags": [tags["دنج"], tags["فضای باز"]]
            },
            {
                "name": "رستوران مسلم (بازار بزرگ)",
                "district": "منطقه ۱۲",
                "address": "راسته بازار تهران، نبش سبزه میدان",
                "description": "معروف‌ترین ته‌چین و کباب کوبیده سنتی پایتخت، بسیار پرتردد و شلوغ.",
                "phone": "02155602736",
                "hours": "۱۱:۰۰ تا ۱۸:۰۰",
                "lat": 35.676300, "lng": 51.418400,
                "cats": [cats["restaurant"]],
                "initial_tags": [tags["دسترسی به مترو"], tags["بسیار شلوغ"]]
            },
            {
                "name": "بولینگ عبدو (مجموعه چمران)",
                "district": "منطقه ۳",
                "address": "خیابان شریعتی، بالاتر از پل صدر",
                "description": "خطوط بولینگ استاندارد، سینما، بیلیارد و سالن‌های ورزشی متنوع برای جوانان.",
                "phone": "02122204555",
                "hours": "۱۰:۰۰ تا ۲۳:۳۰",
                "lat": 35.782000, "lng": 51.439800,
                "cats": [cats["entertainment"], cats["cinema"]],
                "initial_tags": [tags["هیجان‌انگیز"], tags["دسترسی به مترو"]]
            },
            {
                "name": "پارک جنگلی سرخه حصار",
                "district": "منطقه ۱۳",
                "address": "انتهای خیابان دماوند، بعد از ترمینال شرق",
                "description": "طبیعت بکر و کوهستانی در شرق تهران، پیست تخصصی دوچرخه و امکان کمپینگ.",
                "phone": "02177464000",
                "hours": "۶:۰۰ تا ۲۳:۰۰",
                "lat": 35.718000, "lng": 51.542000,
                "cats": [cats["nature"]],
                "initial_tags": [tags["اقتصادی"], tags["فضای باز"]]
            }
        ]

        places = []
        for item in places_data:
            place, _ = Place.objects.get_or_create(
                name=item["name"],
                defaults={
                    "district": item["district"],
                    "address": item["address"],
                    "description": item["description"],
                    "phone_number": item["phone"],
                    "working_hours": item["hours"],
                    "latitude": item["lat"],
                    "longitude": item["lng"],
                    "is_active": True
                }
            )
            place.categories.set(item["cats"])
            # انتساب تگ‌های اولیه ادمین
            for t in item["initial_tags"]:
                PlaceTag.objects.get_or_create(
                    place=place, tag=t,
                    defaults={"strength": 95, "source": TagSource.ADMIN, "is_active": True}
                )
            places.append(place)
        self.stdout.write(f"- تعداد {len(places)} مکان واقعی در تهران ثبت شد.")

        # -------------------------------------------------------------
        # ۷. ثبت بازخوردهای چندگانه واقعی و پاسخ‌ها (فعال‌سازی سیگنال‌ها)
        # -------------------------------------------------------------
        # مکان اول: کافه گودو یاس (۳ بازخورد)
        godo = places[0]
        r1, _ = Review.objects.get_or_create(user=users[0], place=godo, defaults={"comment": "یکی از قشنگ‌ترین حیاط‌های تهران رو داره، شربت‌هاش عالیه.", "status": ReviewStatus.APPROVED})
        Answer.objects.get_or_create(review=r1, question=q_price, defaults={"option": opt_p_mid})
        Answer.objects.get_or_create(review=r1, question=q_crowd, defaults={"option": opt_c_quiet})
        Answer.objects.get_or_create(review=r1, question=q_suit, defaults={"option": opt_s_date})
        Answer.objects.get_or_create(review=r1, question=q_access, defaults={"option": opt_a_easy})
        Answer.objects.get_or_create(review=r1, question=q_outdoor, defaults={"option": opt_o_yes})

        r2, _ = Review.objects.get_or_create(user=users[1], place=godo, defaults={"comment": "محیط بسیار رویایی و پرسنل با احترام.", "status": ReviewStatus.APPROVED})
        Answer.objects.get_or_create(review=r2, question=q_price, defaults={"option": opt_p_mid})
        Answer.objects.get_or_create(review=r2, question=q_crowd, defaults={"option": opt_c_quiet})
        Answer.objects.get_or_create(review=r2, question=q_suit, defaults={"option": opt_s_date})
        Answer.objects.get_or_create(review=r2, question=q_outdoor, defaults={"option": opt_o_yes})

        r3, _ = Review.objects.get_or_create(user=users[2], place=godo, defaults={"comment": "همیشه برای قرارهای مهمم اینجا رو انتخاب می‌کنم.", "status": ReviewStatus.APPROVED})
        Answer.objects.get_or_create(review=r3, question=q_price, defaults={"option": opt_p_mid})
        Answer.objects.get_or_create(review=r3, question=q_suit, defaults={"option": opt_s_date})
        Answer.objects.get_or_create(review=r3, question=q_outdoor, defaults={"option": opt_o_yes})

        # مکان پنجم: کافه کتاب فلسفه (۳ بازخورد برای فعال‌سازی مطالعه و اقتصادی)
        ketab = places[4]
        rk1, _ = Review.objects.get_or_create(user=users[3], place=ketab, defaults={"comment": "ساکت، پر از کتاب و اسپرسوی باکیفیت.", "status": ReviewStatus.APPROVED})
        Answer.objects.get_or_create(review=rk1, question=q_price, defaults={"option": opt_p_eco})
        Answer.objects.get_or_create(review=rk1, question=q_crowd, defaults={"option": opt_c_quiet})
        Answer.objects.get_or_create(review=rk1, question=q_suit, defaults={"option": opt_s_study})
        Answer.objects.get_or_create(review=rk1, question=q_access, defaults={"option": opt_a_easy})

        rk2, _ = Review.objects.get_or_create(user=users[4], place=ketab, defaults={"comment": "قیمت‌های منصفانه و فضای مناسب برای کار با لپ‌تاپ.", "status": ReviewStatus.APPROVED})
        Answer.objects.get_or_create(review=rk2, question=q_price, defaults={"option": opt_p_eco})
        Answer.objects.get_or_create(review=rk2, question=q_crowd, defaults={"option": opt_c_quiet})
        Answer.objects.get_or_create(review=rk2, question=q_suit, defaults={"option": opt_s_study})

        # مکان سیزدهم: رستوران مسلم (۲ بازخورد شلوغی و مترو)
        moslem = places[12]
        rm1, _ = Review.objects.get_or_create(user=users[5], place=moslem, defaults={"comment": "کیفیت ته‌چین بی‌نظیره ولی همیشه صف طولانی داره.", "status": ReviewStatus.APPROVED})
        Answer.objects.get_or_create(review=rm1, question=q_price, defaults={"option": opt_p_mid})
        Answer.objects.get_or_create(review=rm1, question=q_crowd, defaults={"option": opt_c_busy})
        Answer.objects.get_or_create(review=rm1, question=q_access, defaults={"option": opt_a_easy})

        rm2, _ = Review.objects.get_or_create(user=users[6], place=moslem, defaults={"comment": "همهمه زیاده ولی غذا در کمترین زمان تحویل داده میشه.", "status": ReviewStatus.APPROVED})
        Answer.objects.get_or_create(review=rm2, question=q_price, defaults={"option": opt_p_mid})
        Answer.objects.get_or_create(review=rm2, question=q_crowd, defaults={"option": opt_c_busy})
        Answer.objects.get_or_create(review=rm2, question=q_access, defaults={"option": opt_a_easy})

        # مکان سوم: پارک جمشیدیه (۲ بازخورد فضای باز و اقتصادی)
        jamshidieh = places[2]
        rj1, _ = Review.objects.get_or_create(user=users[7], place=jamshidieh, defaults={"comment": "هوای کوهستانی و پیاده‌روی عالی در دل سنگ‌ها.", "status": ReviewStatus.APPROVED})
        Answer.objects.get_or_create(review=rj1, question=q_price, defaults={"option": opt_p_eco})
        Answer.objects.get_or_create(review=rj1, question=q_outdoor, defaults={"option": opt_o_yes})

        rj2, _ = Review.objects.get_or_create(user=users[8], place=jamshidieh, defaults={"comment": "یکی از بهترین بوستان‌های تهران برای هوای پاک.", "status": ReviewStatus.APPROVED})
        Answer.objects.get_or_create(review=rj2, question=q_price, defaults={"option": opt_p_eco})
        Answer.objects.get_or_create(review=rj2, question=q_outdoor, defaults={"option": opt_o_yes})

        # مکان نهم: کافه رستوران ویکولو (۲ بازخورد لوکس و قرار)
        vicolo = places[8]
        rv1, _ = Review.objects.get_or_create(user=users[9], place=vicolo, defaults={"comment": "کوچه‌ای ایتالیایی در دل الهیه، فضایی فوق‌العاده خاص.", "status": ReviewStatus.APPROVED})
        Answer.objects.get_or_create(review=rv1, question=q_price, defaults={"option": opt_p_exp})
        Answer.objects.get_or_create(review=rv1, question=q_suit, defaults={"option": opt_s_date})

        rv2, _ = Review.objects.get_or_create(user=users[0], place=vicolo, defaults={"comment": "قیمت‌ها بالاست اما برای سالگرد و قرارهای خاص بهترین انتخابه.", "status": ReviewStatus.APPROVED})
        Answer.objects.get_or_create(review=rv2, question=q_price, defaults={"option": opt_p_exp})
        Answer.objects.get_or_create(review=rv2, question=q_suit, defaults={"option": opt_s_date})

        self.stdout.write("- فیدبک‌ها و پاسخ‌ها ثبت و موتور تجمیع خودکار فراخوانی شد.")

        # -------------------------------------------------------------
        # ۸. گزارش‌های خطا و پیشنهادها (Report)
        # -------------------------------------------------------------
        Report.objects.get_or_create(
            user=users[1], place=godo,
            defaults={
                "report_type": ReportType.SUGGESTION,
                "reason": "تغییر ساعت کاری در تعطیلات رسمی",
                "description": "در روزهای تعطیل صبح‌ها از ساعت ۹:۳۰ باز می‌کنند.",
                "status": ReportStatus.PENDING
            }
        )
        Report.objects.get_or_create(
            user=users[3], place=places[3],
            defaults={
                "report_type": ReportType.PROBLEM,
                "reason": "خرابی کارت‌خوان طبقه فودکورت",
                "description": "کارت‌خوان سالن سینما متصل نبود و معطلی داشت.",
                "status": ReportStatus.RESOLVED
            }
        )
        Report.objects.get_or_create(
            user=users[5], place=moslem,
            defaults={
                "report_type": ReportType.SUGGESTION,
                "reason": "پیشنهاد ثبت شعبه دوم",
                "description": "شعبه دوم مسلم در خیابان ۱۵ خرداد هم افتتاح شده است.",
                "status": ReportStatus.PENDING
            }
        )
        self.stdout.write("- گزارش‌ها و پیشنهادات کاربران ثبت شدند.")

        self.stdout.write(self.style.SUCCESS("\n تبریک! کل پایگاه داده با انبوه داده‌های تستی واقعی و به‌هم‌پیوسته پر شد."))