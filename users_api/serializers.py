import random
from datetime import datetime ,timedelta
from django.conf import settings

from django.contrib.auth import (get_user_model,authenticate)
from .models import UserModel
from rest_framework import  serializers

class UserLogSerializer(serializers.ModelSerializer):
    class Meta:
       model = UserModel
       fields = ['username','phone_number','email','password','profile_photo','gender','address' ]
    
    # def create(self, val_data):
    #     return get_user_model().objects.create_user(**val_data)
    def update(self,instance,val_data):
        '''update profile'''
        password=val_data.pop('password',None)
        user=super.update(instance,val_data)
        if password :
            user.set_password(password)
            user.save()
        return user
    

        
class UserSerializer(serializers.ModelSerializer):
    password1=serializers.CharField(
        write_only=True,
        min_length=settings.MIN_PASSWORD_LENGTH,
        error_messages={'min_length':f"Password must be longer than{settings.MIN_PASSWORD_LENGTH} length"}
        )
    password2=serializers.CharField(
        write_only=True,
        min_length=settings.MIN_PASSWORD_LENGTH,
        error_messages={'min_length':f"Password must be longer than{settings.MIN_PASSWORD_LENGTH} length"}
        )
    class Meta:
        model = UserModel
        fields = ['username','phone_number','email','password1','password2' ]
    
    # to check password validation in sign up form
    def validate(self,data):
        if data['password1']!=data['password2']:
            raise serializers.ValidationError("the two password does not match")
        return data
    
    # create and return user with encrybted password
    def create(self, val_data):
        otp=random.randint(1000,9999)
        otp_expiration=datetime.now()+timedelta(minutes=5) 
        
        user=UserModel(
            username=val_data['username'],
            phone_number=val_data['phone_number'],
            email=val_data['email'],
            otp=otp,
            otp_expiration=otp_expiration,
            max_otp_try=settings.MAX_OTP_TRY,
            
        )
        user.set_password(val_data['password1'])
        user.save()
        return user
    
  
    
    # @action(detail=True,methods=['PATCH'])
    # def verify_otp(self,request,pk=None):
    #     # if ()
    #     pass
    
# from django.conf import settings
# from django.core.mail import send_mail

    
# subject = 'Welcome to DropMe'
# message = f'Hi {user.username}, thank you for registering in DropMe app enjoy recycling :).'
# email_from = settings.EMAIL_HOST_USER
# recipient_list = [user.email, ]
# send_mail( subject, message, email_from, recipient_list )
