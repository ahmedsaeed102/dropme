import kronos
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import get_template
from users_api.models import UserModel
from .utlis import get_user_weekly_logs


@kronos.register("0 8 * * 5")
def send_weekly_recycle_summary_email():
    subject = "Weekly Recycle Summary"
    from_email = settings.EMAIL_HOST_USER

    for user in UserModel.objects.all():
        logs, total_points, items = get_user_weekly_logs(user.id)
        context = {
            "username": user.username,
            "logs": logs,
            "total_points": total_points["points__sum"],
            "items": items,
        }
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
