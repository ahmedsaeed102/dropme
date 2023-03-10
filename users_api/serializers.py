import random
from datetime import datetime ,timedelta
from django.conf import settings
from .models import UserModel
from rest_framework import  serializers
from .otp_send_email import send_otp
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.exceptions import AuthenticationFailed



        
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
    redirect_url = serializers.CharField(max_length=500, required=False)

    class Meta:
        fields = ['email']


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(
        min_length=1, write_only=True)
    uidb64 = serializers.CharField(
        min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = UserModel.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)

            user.set_password(password)
            user.save()

            return (user)
        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid', 401)
        return super().validate(attrs)


    
