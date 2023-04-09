import random
from datetime import datetime ,timedelta
from django.conf import settings
from .models import UserModel
from rest_framework import  serializers
from .otp_send_email import send_otp,send_mail_pass
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone



        
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
        fields = ['id','username','phone_number','email','password1','password2' ]
        
      
    
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
        send_otp(val_data['email'],otp)
        return user
    



class UserProfileSerializer(UserSerializer):
    class Meta:
       model = UserModel
       fields = ['username','phone_number','email','password1','password2','profile_photo','gender','address' ]
    
    # def create(self, val_data):
    #     return get_user_model().objects.create_user(**val_data)
    def update(self,instance,val_data):
        '''update profile'''
        password=val_data.pop('password1',None)
        user=super().update(instance,val_data)
        if password :
            user.set_password(password)
            user.save()
        return user
    



class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)
    

    class Meta:
        fields = ['email']
        def update(self):
            otp=random.randint(1000,9999)
            otp_expiration=datetime.now()+timedelta(minutes=5) 
        
            user=UserModel(
           
            otp=otp,
            otp_expiration=otp_expiration,
            max_otp_try=settings.MAX_OTP_TRY,
            
                          )
            
            user.save()
            send_mail_pass(self.email,otp)
            
            return user
      
       

    


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)
    otp=serializers.CharField( max_length=4, write_only=True)
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ['password','otp','email']

    

    def validate(self, data):
        
            
        
        try:
            password = data.get('password')
            otp=data.get('otp')
            email=data.get('email')
            
           
            user = UserModel.objects.get(email=data['email'])
           
           
            if UserModel.objects.filter(email=email).exists():
                if( user.otp_expiration and user.otp ==otp and timezone.now() < user.otp_expiration ):
                    user.otp_expiration=None
                    user.max_otp_try=settings.MAX_OTP_TRY
                    user.max_otp_out=None
            user.set_password(password)
            user.save()
            # return (user)
            return super().validate(data)
        except Exception as e:
            raise AuthenticationFailed('The reset otp is invalid', 401)
        
    

    

        
       
