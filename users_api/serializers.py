import random
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, APIException
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UserModel, LocationModel
from .otp_send_email import send_otp


class UserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(
        write_only=True,
        min_length=settings.MIN_PASSWORD_LENGTH,
        error_messages={
            "min_length": f"Password must be longer than{settings.MIN_PASSWORD_LENGTH} length"
        },
    )
    password2 = serializers.CharField(
        write_only=True,
        min_length=settings.MIN_PASSWORD_LENGTH,
        error_messages={
            "min_length": f"Password must be longer than{settings.MIN_PASSWORD_LENGTH} length"
        },
    )

    class Meta:
        model = UserModel
        fields = ["id", "username", "phone_number", "email", "password1", "password2"]

    # to check password validation in sign up form
    def validate(self, data):
        password1 = data.get("password1")
        password2 = data.get("password2")
        if password1 != password2:
            raise serializers.ValidationError("the two password does not match")
        return data

    # create and return user with encrybted password
    def create(self, val_data):
        otp = random.randint(1000, 9999)
        otp_expiration = datetime.now() + timedelta(minutes=5)

        user = UserModel(
            username=val_data["username"],
            phone_number=val_data["phone_number"],
            email=val_data["email"],
            otp=otp,
            otp_expiration=otp_expiration,
            max_otp_try=settings.MAX_OTP_TRY,
        )
        user.set_password(val_data["password1"])
        user.save()
        send_otp(user)
        return user


class UserProfileSerializer(UserSerializer):
    password1 = serializers.CharField(
        write_only=True,
        min_length=settings.MIN_PASSWORD_LENGTH,
        error_messages={
            "min_length": f"Password must be longer than{settings.MIN_PASSWORD_LENGTH} length"
        },
    )
    password2 = serializers.CharField(
        write_only=True,
        min_length=settings.MIN_PASSWORD_LENGTH,
        error_messages={
            "min_length": f"Password must be longer than{settings.MIN_PASSWORD_LENGTH} length"
        },
    )
    email = serializers.EmailField()
    username = serializers.CharField(max_length=80)

    # address_name = serializers.StringRelatedField()
    class Meta:
        model = UserModel
        fields = [
            "username",
            "phone_number",
            "age",
            "email",
            "password1",
            "password2",
            "profile_photo",
            "gender",
            "address",
        ]

    def update(self, instance, val_data):
        """update profile for User"""
        password = val_data.pop("password1", None)
        user = super().update(instance, val_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        fields = ["email"]


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=settings.MIN_PASSWORD_LENGTH, max_length=68, write_only=True
    )
    otp = serializers.CharField(min_length=4, max_length=4, write_only=True)
    email = serializers.EmailField()

    class Meta:
        fields = ["password", "otp", "email"]

    def validate(self, data):
        password = data.get("password", "")
        otp = data.get("otp", "")
        email = data.get("email", "")

        user = UserModel.objects.filter(email=email).first()

        if user:
            if user.otp == otp and timezone.now() < user.otp_expiration:
                user.otp = ""
                user.set_password(password)
                user.save()
            else:
                raise AuthenticationFailed("Invalid OTP", 401)

        else:
            raise AuthenticationFailed("Invalid Email", 401)

        return data


class LocationModelserializers(serializers.ModelSerializer):
    class Meta:
        model = LocationModel
        fields = "__all__"


# custom serializer from rest_framework_simplejwt.serializers
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        if not self.user.is_active:
            otp = random.randint(1000, 9999)
            otp_expiration = datetime.now() + timedelta(minutes=5)
            self.user.otp = otp
            self.user.otp_expiration = otp_expiration
            self.user.save()

            send_otp(self.user)
            return {"is_verified": False}

        # Add custom claims
        data["username"] = self.user.username
        data["email"] = self.user.email
        data["id"] = self.user.id

        return data
