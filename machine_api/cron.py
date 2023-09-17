import kronos
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import get_template
from users_api.models import UserModel
from .utlis import get_user_weekly_logs


@kronos.register("0 8 * * 5")
def send_weekly_recycle_summary_email():
    from_email = settings.EMAIL_HOST_USER

    for user in UserModel.objects.filter(is_active=True):
        subject = "Weekly Recycle Summary - Your Impact with Drop Me!"
        data = get_user_weekly_logs(user.id)

        if not data["recycled"]:
            subject = "Weekly Recycling Update - Join the Recycling Revolution"

        context = {"username": user.username}
        context.update(data)

        template = get_template("recylce_weekly_summary_template.html").render(context)

        send_mail(
            subject,
            None,
            from_email,
            [user.email],
            fail_silently=False,
            html_message=template,
        )

    print("Weekly Summary Emails Sent")
