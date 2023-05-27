import kronos
from users_api.models import UserModel
from django.conf import settings
from django.core.mail import send_mail


@kronos.register("0 8 * * 5")
def send_weekly_recycle_summary_email():
    subject = "Weekly Recycle Summary"
    message = "Here is your weekly recycle summary"
    from_email = settings.EMAIL_HOST_USER

    recievers = []
    for user in UserModel.objects.all():
        recievers.append(user.email)

    send_mail(subject, message, from_email, recievers)
    # send_mail(
    #     subject,
    #     None,
    #     email_from,
    #     recipient_list,
    #     fail_silently=False,
    #     html_message=template,
    # )
