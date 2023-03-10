from django.shortcuts import render
from .serializers import UserSerializer,UserProfileSerializer,SetNewPasswordSerializer, ResetPasswordEmailRequestSerializer
from rest_framework import  viewsets,status,generics,permissions,authentication
from rest_framework.settings import api_settings
from .models import UserModel
from rest_framework.permissions import IsAuthenticated

# help in otp function

import random
from datetime import datetime ,timedelta
from django.conf import settings
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response
from .otp_send_email import send_otp,send_mail_pass


from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
import os
from django.http import HttpResponsePermanentRedirect


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView





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


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        email = request.data.get('email', '')

        if UserModel.objects.filter(email=email).exists():
            user = UserModel.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(
                request=request).domain
            relativeLink = reverse(
                'password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})

            redirect_url = request.data.get('redirect_url', '')
            absurl = 'http://'+current_site + relativeLink
            email_body = 'Hello, \n Use link below to reset your password  \n' + \
                absurl+"?redirect_url="+redirect_url
            data = {'email_body': email_body, 'to_email': user.email,
                    'email_subject': 'Reset your passsword'}
            send_mail_pass(data)
        return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)


class PasswordTokenCheckAPI(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def get(self, request, uidb64, token):

        redirect_url = request.GET.get('redirect_url')

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = UserModel.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                if len(redirect_url) > 3:
                    return CustomRedirect(redirect_url+'?token_valid=False')
                else:
                    return CustomRedirect(os.environ.get('FRONTEND_URL', '')+'?token_valid=False')

            if redirect_url and len(redirect_url) > 3:
                return CustomRedirect(redirect_url+'?token_valid=True&message=Credentials Valid&uidb64='+uidb64+'&token='+token)
            else:
                return CustomRedirect(os.environ.get('FRONTEND_URL', '')+'?token_valid=False')

        except DjangoUnicodeDecodeError as identifier:
            try:
                if not PasswordResetTokenGenerator().check_token(user):
                    return CustomRedirect(redirect_url+'?token_valid=False')
                    
            except UnboundLocalError as e:
                return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_400_BAD_REQUEST)



class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)



class CustomRedirect(HttpResponsePermanentRedirect):

    allowed_schemes = [os.environ.get('APP_SCHEME'), 'http', 'https']
    
        
    



