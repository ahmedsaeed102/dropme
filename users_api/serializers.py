# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from rest_framework import  serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model
        fields = ['username', 'password', 'email', 'phone_number']
        
        
        
