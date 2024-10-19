import threading
import random
import django_filters
from datetime import timedelta, datetime
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import get_template
from .models import UserModel

def user_get(*, id: int) -> UserModel:
    return get_object_or_404(UserModel, pk=id)

class EmailThread(threading.Thread):
    def __init__(self, *, subject: str, email_to: list, email_from: str, html=None, body: str | None = None,):
        self.subject = subject
        self.body = body
        self.html = html
        self.email_to = email_to
        self.email_from = email_from
        threading.Thread.__init__(self)
    def run(self):
        send_mail(self.subject, self.body, self.email_from, self.email_to, fail_silently=False, html_message=self.html,)


def email_send(*, subject: str, to: list, body: str | None = None, context: dict = {}, template: str | None = None,) -> None:
    email_from = f'DropMe <{settings.EMAIL_HOST_USER}>'
    if template:
        template = get_template(template).render(context)
        EmailThread(subject=subject, email_to=to, email_from=email_from, html=template).start()
    else:
        EmailThread(subject=subject, email_to=to, email_from=email_from, body=body).start()


def send_otp(user: UserModel) -> None:
    """Function to send OTP email to user"""
    context = {"username": user.username, "otp": user.otp}
    subject = "Your One-Time Password (OTP) for DropMe"
    recipient_list = [user.email]
    email_send(subject=subject, to=recipient_list, context=context, template="otp_email.html")


def send_reset_password_email(email, otp):
    """Function to send reset password email with OTP"""
    user = UserModel.objects.get(email=email)
    user.otp = otp
    user.save()
    context = {"username": user.username, "otp": otp}
    subject = "Password Reset Request for DropMe"
    recipient_list = [email]
    email_send(subject=subject, to=recipient_list, context=context, template="reset_password_email.html")


def send_welcome_email(email):
    """Function to send welcome email to user after account verification"""
    user = UserModel.objects.get(email=email)
    context = {'username': user.username}
    subject = "Welcome to Drop Me - Your Journey Towards a Sustainable Future Begins Here!"
    recipient_list = [email]
    email_send( subject=subject, to=recipient_list, context=context, template="welcome_email.html")


def otp_generate() -> tuple[str, datetime]:
    """
    Generates a one-time password (OTP) and its expiration time.
    Returns: A tuple containing the OTP and its expiration time.
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
