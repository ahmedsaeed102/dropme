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

    context = {'username': user.username, 'otp': otp}
    template = get_template('otp_email.html').render(context)
    
    subject = 'Your One-Time Password (OTP) for DropMe'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]

    send_mail(
        subject, 
        None, 
        email_from, 
        recipient_list, 
        fail_silently=False, 
        html_message=template
    )


""" 2) reset password using email_link """

from django.core.mail import EmailMessage
import threading


# class EmailThread(threading.Thread):

#     def __init__(self, email):
#         self.email = email
#         threading.Thread.__init__(self)

#     def run(self):
#         self.email.send()
     
# def send_mail_pass(data):
      
#       email = EmailMessage(subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
#       EmailThread(email).start()


def send_mail_pass(email, otp):
    user = UserModel.objects.get(email=email)
    user.otp = otp
    user.save()
    
    subject = 'Welcome to DropMe'
    message = f'Hi {user.username}, Use this otp to reset your password in DropMe app,this is your OTP:{otp} enjoy recycling :).'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from,recipient_list)

