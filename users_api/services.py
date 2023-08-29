import random
import django_filters
from datetime import timedelta, datetime
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import get_template
from .models import UserModel


def email_send(
    *,
    subject: str,
    to: list,
    body: str = None,
    context: dict = {},
    template=None,
) -> None:
    email_from = settings.EMAIL_HOST_USER

    if template:
        template = get_template(template).render(context)

        send_mail(
            subject,
            None,
            email_from,
            to,
            fail_silently=False,
            html_message=template,
        )
    else:
        send_mail(
            subject,
            body,
            email_from,
            to,
        )


def send_otp(user: UserModel) -> None:
    """
    Function to send OTP email to user
    """

    context = {"username": user.username, "otp": user.otp}
    template = get_template("otp_email.html").render(context)

    subject = "Your One-Time Password (OTP) for DropMe"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email]

    send_mail(
        subject,
        None,
        email_from,
        recipient_list,
        fail_silently=False,
        html_message=template,
    )


def send_reset_password_email(email, otp):
    """Function to send reset password email with OTP"""

    user = UserModel.objects.get(email=email)
    user.otp = otp
    user.save()

    context = {"username": user.username, "otp": otp}
    template = get_template("reset_password_email.html").render(context)

    subject = "Password Reset Request for DropMe"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]

    send_mail(
        subject,
        None,
        email_from,
        recipient_list,
        fail_silently=False,
        html_message=template,
    )


def send_welcome_email(email):
    """Function to send welcome email to user after account verification"""

    # user = UserModel.objects.get(email=email)
    # context = {'username': user.username}
    # template = get_template('welcome_email.html').render(context)

    subject = "Welcome to DropMe"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]

    send_mail(
        subject,
        "Welcome to dropme",
        email_from,
        recipient_list,
        # fail_silently=False,
        # html_message=template
    )


def otp_generate() -> tuple[str, datetime]:
    """
    Generates a one-time password (OTP) and its expiration time.

    Returns:
        A tuple containing the OTP and its expiration time.
    """
    otp = random.randint(1000, 9999)
    otp_expiration = timezone.now() + timedelta(minutes=5)

    return otp, otp_expiration


def otp_set(*, user: UserModel) -> UserModel:
    otp, otp_expiration = otp_generate()

    user.otp = otp
    user.otp_expiration = otp_expiration
    user.max_otp_try = int(user.max_otp_try) - 1

    if user.max_otp_try == 0:
        user.max_otp_out = timezone.now() + timedelta(hours=1)
        user.max_otp_try = settings.MAX_OTP_TRY

    user.save()

    return user


class UserFilter(django_filters.FilterSet):
    email = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = UserModel
        fields = ["email"]


def user_list(*, filters=None) -> list[UserModel]:
    filters = filters or {}

    qs = UserModel.objects.all()

    return UserFilter(filters, qs).qs
