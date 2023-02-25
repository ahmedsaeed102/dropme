from django.shortcuts import render
from django.contrib.auth import get_user_model
from .serializers import UserSerializer,UserLogSerializer
from rest_framework import  viewsets
from .models import UserModel
from rest_framework.permissions import IsAuthenticated


class UserLogViewSet(viewsets.ModelViewSet):
    permission_classes=(IsAuthenticated,)
    serializer_class=UserLogSerializer
    queryset=get_user_model().objects.all()

class UserViewSet(viewsets.ModelViewSet):
    queryset=UserModel.objects.all()
    serializer_class=UserSerializer
    
        
    



