from django.shortcuts import render
from .serializers import UserSerializer,UserLogSerializer
from rest_framework import  viewsets,status,generics,permissions,authentication
from rest_framework.settings import api_settings
from .models import UserModel
from rest_framework.permissions import IsAuthenticated

# help in otp function

import random
from datetime import datetime 
from django.conf import settings
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response


from django.conf import settings
from django.core.mail import send_mail




# for signup
class UserViewSet(viewsets.ModelViewSet):
    queryset=UserModel.objects.all()
    serializer_class=UserSerializer 
    

class ManageUserProfileView(generics.RetrieveUpdateAPIView):

    serializer_class = UserLogSerializer
    permission_classes=(permissions.IsAuthenticated,)
    
    def get_object(self):
        return self.request.user



    
        
    



