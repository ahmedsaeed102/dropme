from django.shortcuts import render
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .serializers import UserSerializer
from rest_framework import  serializers,viewsets
from rest_framework.permissions import IsAuthenticated


class UserViewSet(viewsets.ModelViewSet):
    permission_classes=(IsAuthenticated,)
    serializer_class=UserSerializer
    queryset=get_user_model().objects.all()
        
    



