import kronos
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import get_template
from users_api.models import UserModel, LanguageChoices
from .utlis import get_user_logs, get_remaining_points
from django.template.loader import render_to_string
from django.utils.html import strip_tags

@kronos.register("0 8 * * 5")
def send_weekly_recycle_summary_email():
    from_email = f'DropMe <{settings.EMAIL_HOST_USER}>'

    for user in UserModel.objects.filter(is_active=True):
        data = get_user_logs(user.id)
        remaining_points = get_remaining_points(user)
        context = {"username": user.username, "rank":user.ranking, "remaining_points": remaining_points, "total_points": user.total_points}
        context.update(data)

        if data['recycled']:
            if user.preferred_language == LanguageChoices.ARABIC:
                subject = "تقدمك الأسبوعي في إعادة التدوير مع Drop Me 🌱"
                template = get_template("active_recylce_weekly_summary_arabic.html").render(context)
            else:
                subject = "Your Weekly Recycling Progress with Drop Me 🌱"
                template = get_template("active_recylce_weekly_summary_english.html").render(context)

        elif not data["recycled"]:
            if user.preferred_language == LanguageChoices.ARABIC:
                subject = "لنبدأ رحلتك في إعادة التدوير مع Drop Me 🌱"
                template = get_template("inactive_recylce_weekly_summary_arabic.html").render(context)
            else:
                subject = "Let's Get Started on Your Recycling Journey with Drop Me 🌱"
                template = get_template("inactive_recylce_weekly_summary_english.html").render(context)

        send_mail(subject, None, from_email, [user.email], fail_silently=False, html_message=template)
    print("Weekly Summary Emails Sent")

NOTIFICATION_SCHEDULE = [
    # {
    #     "time": "53 17 21 3 *",
    #     "title_en": "A Gift for Mother Earth – Recycle & Win! 🌱",
    #     "title_ar": "هدية لكوكب الأرض – قم بإعادة التدوير واربح! 🌱",
    #     "message_en": (
    #         "This Mother’s Day, let’s honor not just our moms, but also Mother Earth! 🌍💚<br>"
    #         "Recycle today at Maadi Club & earn 30+ points for a sustainable future. 🚀♻"
    #     ),
    #     "message_ar": (
    #         "في يوم الأم، لنكرم ليس فقط أمهاتنا، ولكن أيضًا أمنا الأرض! 🌍💚<br>"
    #         "قم بإعادة التدوير اليوم في نادي المعادي واربح 30+ نقطة لمستقبل مستدام. 🚀♻"
    #     ),
    # },
    {
        "time": "15 18 23 3 *",
        "title_en": "9 Days to Eid: Let’s Go Green! 🎉",
        "title_ar": "9 أيام حتى العيد: لنصبح أكثر صداقة للبيئة! 🎉",
        "message_en": "Eid is around the corner! Start your journey to rewards—recycle today & get 10+ bonus points per day! 🎊♻",
        "message_ar": "العيد يقترب! ابدأ رحلتك نحو المكافآت – أعد التدوير اليوم واحصل على 10+ نقاط إضافية يوميًا! 🎊♻",
    },
    # {
    #     "time": "53 17 24 3 *",
    #     "title_en": "Surprise Monday: Mystery Bonus Awaits! 🎁♻",
    #     "title_ar": "الإثنين المفاجئ: مكافأة غامضة بانتظارك! 🎁♻",
    #     "message_en": "Recycle today & unlock a mystery reward in your wallet! What will it be? Only one way to find out! 🎁♻",
    #     "message_ar": "قم بإعادة التدوير اليوم وافتح مكافأة غامضة في محفظتك! ما هي؟ هناك طريقة واحدة فقط لمعرفة ذلك! 🎁♻",
    # },
    # {
    #     "time": "53 17 25 3 *",
    #     "title_en": "Green Habits Challenge: Can You Go 3 Days? 🌱",
    #     "title_ar": "تحدي العادات الخضراء: هل يمكنك الاستمرار 3 أيام؟ 🌱",
    #     "message_en": "A habit takes 3 days to form! Recycle today, tomorrow & the next day to unlock a special streak reward! 🌍♻",
    #     "message_ar": "يستغرق بناء العادة 3 أيام! قم بإعادة التدوير اليوم وغدًا واليوم التالي لفتح مكافأة استمرارية خاصة! 🌍♻",
    # },
    # {
    #     "time": "53 17 26 3 *",
    #     "title_en": "Ramadan’s Last Wednesday: Make It Count! 🌟",
    #     "title_ar": "آخر أربعاء في رمضان: اجعله مميزًا! 🌟",
    #     "message_en": "Small actions, big rewards! Recycle today & get a 1.5x points boost—only for today! Let’s make it a habit. ♻🌟",
    #     "message_ar": "خطوات صغيرة، مكافآت كبيرة! أعد التدوير اليوم واحصل على زيادة 1.5x في النقاط – فقط لليوم! اجعلها عادة! ♻🌟",
    # },
    # {
    #     "time": "53 17 27 3 *",
    #     "title_en": "Eid Leaderboard: Are You on It? 🏆",
    #     "title_ar": "لوحة الصدارة للعيد: هل أنت من المتصدرين؟ 🏆",
    #     "message_en": "The top recyclers before Eid win a grand reward! Check your points & keep recycling to climb the leaderboard! 🏆♻",
    #     "message_ar": "أفضل من يعيد التدوير قبل العيد سيحصل على مكافأة كبرى! تحقق من نقاطك واستمر في إعادة التدوير لتصعد في الترتيب! 🏆♻",
    # },
    # {
    #     "time": "53 17 27 3 *",
    #     "title_en": "Last Call Before Friday’s Big Boost! 🚀",
    #     "title_ar": "آخر فرصة قبل زيادة النقاط الكبيرة يوم الجمعة! 🚀",
    #     "message_en": "Tomorrow is Ramadan’s Last Friday! Warm up today & get 15+ bonus points. Tomorrow, we go BIG! 🚀♻",
    #     "message_ar": "غدًا آخر جمعة في رمضان! جهّز نفسك اليوم واحصل على 15+ نقطة إضافية. غدًا، ستكون المفاجأة كبيرة! 🚀♻",
    # },
    # {
    #     "time": "53 17 28 3 *",
    #     "title_en": "Ramadan’s Last Friday: Earn Double Rewards! 🌙♻",
    #     "title_ar": "آخر جمعة في رمضان: اربح ضعف المكافآت! 🌙♻",
    #     "message_en": "A blessed Friday for good deeds! Recycle today & earn double points as we approach Eid. Small action, big impact! 💚♻",
    #     "message_ar": "يوم جمعة مبارك للأعمال الصالحة! قم بإعادة التدوير اليوم واحصل على ضعف النقاط مع اقتراب العيد. خطوة صغيرة، تأثير كبير! 💚♻",
    # },
    # {
    #     "time": "53 17 29 3 *",
    #     "title_en": "Eid Prep: Clean Up & Earn Rewards! 🎊♻",
    #     "title_ar": "استعداد العيد: نظّف مكانك واربح المكافآت! 🎊♻",
    #     "message_en": "Getting ready for Eid? Declutter your space & drop off recyclables at Maadi Club to earn an extra Eid bonus! Let’s make it a green celebration. 🌍🎉",
    #     "message_ar": "تستعد للعيد؟ نظّف مساحتك وأسقط المواد القابلة للتدوير في نادي المعادي لتحصل على مكافأة العيد الإضافية! دعونا نجعلها احتفالية صديقة للبيئة! 🌍🎉",
    # },
    # {
    #     "time": "53 17 31 3 *",
    #     "title_en": "Eid Mubarak! 🎊 A Special Gift Awaits You! 🎁",
    #     "title_ar": "عيد مبارك! 🎊 مكافأة خاصة في انتظارك! 🎁",
    #     "message_en": "Your sustainability efforts deserve a reward! 🎉 Check your Drop Me wallet for an exclusive Eid surprise gift. Thank you for making a difference! 💚♻",
    #     "message_ar": "جهودك في الاستدامة تستحق مكافأة! 🎉 تحقق من محفظة Drop Me للحصول على هدية مفاجئة خاصة بالعيد. شكرًا لك على صنع الفرق! 💚♻",
    # },
]

def send_email(user, title_en, title_ar, message_en, message_ar):
    from_email = f'DropMe <{settings.EMAIL_HOST_USER}>'
    if user.preferred_language == LanguageChoices.ARABIC:
        title = title_ar
        message = message_ar
        language = "ar"
        direction = "rtl"
    else:
        title = title_en
        message = message_en
        language = "en"
        direction = "ltr"

    context = {"title": title, "message": message, "language": language, "direction": direction}

    html_content = render_to_string("campaign_email.html", context)
    plain_message = strip_tags(html_content)

    send_mail(subject=title, message=plain_message, html_message=html_content, from_email=from_email, recipient_list=[user.email])

# Dynamically register email jobs
for notification in NOTIFICATION_SCHEDULE:
    @kronos.register(notification['time'])
    def scheduled_email(notification=notification):
        for user in UserModel.objects.filter(is_active=True):
            print("heree scheduled_email")
            send_email(user, notification["title_en"], notification["title_ar"], notification["message_en"], notification["message_ar"])
