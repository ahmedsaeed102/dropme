import kronos
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import get_template
from users_api.models import UserModel, LanguageChoices
from .utlis import get_user_logs, get_remaining_points


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