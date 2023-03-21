""" this function handle sending email to user in case of 
1)activate account after sign up """

from django.conf import settings
from django.core.mail import send_mail
from .models import UserModel
  
def send_otp(email, otp):
    user = UserModel.objects.get(email=email)
    user.otp = otp
    user.save()
    
    subject = 'Welcome to DropMe'
    message = f'Hi {user.username}, thank you for registering in DropMe app,this is your OTP:{otp} enjoy recycling :).'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from,recipient_list)


""" 2) reset password using email_link """

from django.core.mail import EmailMessage
import threading


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()
     
def send_mail_pass(data):
      
      email = EmailMessage(subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
      EmailThread(email).start()
