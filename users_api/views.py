import os
import random
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone
from django.http import HttpResponsePermanentRedirect

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .otp_send_email import send_otp,send_mail_pass
from .models import UserModel
from .serializers import UserSerializer, UserProfileSerializer, SetNewPasswordSerializer, ResetPasswordEmailRequestSerializer

# from django.contrib.sites.shortcuts import get_current_site
# from django.urls import reverse
# from django.contrib.auth.tokens import PasswordResetTokenGenerator
# from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
# from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode


class CustomRedirect(HttpResponsePermanentRedirect):
    allowed_schemes = [os.environ.get('APP_SCHEME'), 'http', 'https']


# custom serializer from rest_framework_simplejwt.serializers
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self,attrs):
        data = super().validate(attrs)

        # Add custom claims
        data['username'] = self.user.username
        data['email'] = self.user.email
        
        return data


# for login
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class=MyTokenObtainPairSerializer

# for signup
class UserViewSet(viewsets.ModelViewSet):
    queryset=UserModel.objects.all()
    serializer_class=UserSerializer 

    """ to check if the user enter the correct otp or if he/she is already verified (is_active=True)"""
    @action(detail=True,methods=['PATCH'])
    def verify_otp(self,request,pk=None):
        instance=self.get_object()
        if( not instance.is_active and instance.otp_expiration and instance.otp == request.data.get("otp") and timezone.now() < instance.otp_expiration ):
            instance.is_active=True
            instance.otp_expiration=None
            instance.max_otp_try=settings.MAX_OTP_TRY
            instance.max_otp_out=None
            instance.save()
            return Response("Successfully verfied the user .",status=status.HTTP_200_OK)
        return Response("user already verfied or otp is incorrect .",status=status.HTTP_400_BAD_REQUEST)
   
    """ to regenerate otp until max try """
    @action(detail=True,methods=['PATCH'])
    def regenerate_otp(self,request,pk=None):
        instance=self.get_object()
        if int( instance.max_otp_try== 0) and timezone.now() < instance.max_otp_out:
            return Response("Max OTP try reached, try after an hour.", status=status.HTTP_400_BAD_REQUEST)

        otp=random.randint(1000,9999)
        otp_expiration=datetime.now()+timedelta(minutes=5) 
        max_otp_try=int(instance.max_otp_try)-1

        instance.otp=otp
        instance.otp_expiration=otp_expiration
        instance.max_otp_try=max_otp_try

        if max_otp_try == 0:
            instance.max_otp_out=timezone.now()+datetime.timedelta(hours=1)
        elif max_otp_try == -1:
            instance.max_otp_try=max_otp_try

        send_otp(instance.email, otp)
        instance.save()
        return Response("successfully regenrated the new OTP.",status=status.HTTP_200_OK)

    
# for edit_profile
class ManageUserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes=(permissions.IsAuthenticated,)
    
    def get_object(self):
        return self.request.user
    
# for reseting password
# class ResetPasswordView(generics.RetrieveUpdateAPIView):
    
#     serializer_class = UserProfileSerializer
#     permission_classes=(permissions.IsAuthenticated,)
    
#     def get_object(self):
#         return self.request.user


class RequestPasswordResetEmail(generics.GenericAPIView,):
    """ generate otp for reset password """
    serializer_class = ResetPasswordEmailRequestSerializer
    def post(self, request,pk=None):
        serializer = self.serializer_class(data=request.data)
        email = request.data.get('email', '')
        user = UserModel.objects.filter(email=email).first()
        if user:
            # send email with otp
            send_mail_pass(email,user.otp)
        
            return Response("Reset password email sent",status=status.HTTP_200_OK)
        else:
            return Response("There is no account registered with this email.",status=status.HTTP_404_NOT_FOUND)


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
       
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)

    
class RequestPasswordOtp(generics.GenericAPIView):
    """ regenerate otp for reset password """
    serializer_class = ResetPasswordEmailRequestSerializer    
    def post(self, request,pk=None):
        serializer = self.serializer_class(data=request.data)
        email = request.data.get('email', '')
        instance = UserModel.objects.get(email=email)
        if int( instance.max_otp_try== 0) and timezone.now() < instance.max_otp_out :
            
            return Response("Max OTP try reached ,try after an hour.",status=status.HTTP_400_BAD_REQUEST)

        otp=random.randint(1000,9999)
        otp_expiration=datetime.now()+timedelta(minutes=5) 
        max_otp_try=int(instance.max_otp_try)-1

        instance.otp=otp
        instance.otp_expiration=otp_expiration
        instance.max_otp_try=max_otp_try

        if max_otp_try == 0:
            instance.max_otp_out=timezone.now()+datetime.timedelta(hours=1)
        elif max_otp_try == -1:
            instance.max_otp_try=max_otp_try
        send_otp(instance.email,otp)
        instance.save()
        return Response("successfully regenrated the new OTP.",status=status.HTTP_200_OK)

# @api_view(['PUT'])
# def reset_password(request):
#     """reset_password with email, OTP and new password"""
#     data = request.data
#     user = UserModel.objects.get(email=data['email'])
#     if user.is_active:
#         # Check if otp is valid
#         if data['otp'] == user.opt:
#             if new_password != '':
#                 # Change Password
#                 user.set_password(data['password'])
#                 user.save() # Here user otp will also be changed on save automatically 
#                 return Response('any response or you can add useful information with response as well. ')
#             else:
#                 message = {
#                     'detail': 'Password cant be empty'}
#                 return Response(message, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             message = {
#                 'detail': 'OTP did not matched'}
#             return Response(message, status=status.HTTP_400_BAD_REQUEST)
#     else:
#         message = {
#             'detail': 'Something went wrong'}
#         return Response(message, status=status.HTTP_400_BAD_REQUEST)