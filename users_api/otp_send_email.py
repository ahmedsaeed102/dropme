from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import get_template
from .models import UserModel


def send_otp(email, otp):
    """
    this function handle sending email to user in case of activating account after sign up
    """
    user = UserModel.objects.get(email=email)
    user.otp = otp
    user.save()

    context = {"username": user.username, "otp": otp}
    template = get_template("otp_email.html").render(context)

    subject = "Your One-Time Password (OTP) for DropMe"
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


""" 2) reset password using otp """


def send_mail_pass(email, otp):
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


""" 3) send welcome email to user after sign up """


def send_welcome_email(email):
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
