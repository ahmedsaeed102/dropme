import random
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from .models import UserModel, LocationModel
from .otp_send_email import send_otp, send_mail_pass


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
        send_otp(val_data["email"], otp)
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

    # def create(self, val_data):
    #     return UserModel.objects.create_user(**val_data)
    def update(self, instance, val_data):
        """update profile for User"""
        password = val_data.pop("password1", None)
        user = super().update(instance, val_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ["email"]

        def update(self):
            otp = random.randint(1000, 9999)
            otp_expiration = datetime.now() + timedelta(minutes=5)

            user = UserModel(
                otp=otp,
                otp_expiration=otp_expiration,
                max_otp_try=settings.MAX_OTP_TRY,
            )

            user.save()
            send_mail_pass(self.email, otp)

            return user


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6, max_length=68, write_only=True)
    otp = serializers.CharField(max_length=4, write_only=True)
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ["password", "otp", "email"]

    def validate(self, data):
        try:
            password = data.get("password")
            otp = data.get("otp")
            email = data.get("email")

            user = UserModel.objects.get(email=data["email"])

            if UserModel.objects.filter(email=email).exists():
                if (
                    user.otp_expiration
                    and user.otp == otp
                    and timezone.now() < user.otp_expiration
                ):
                    user.otp_expiration = None
                    user.max_otp_try = settings.MAX_OTP_TRY
                    user.max_otp_out = None
            user.set_password(password)
            user.save()
            # return (user)
            return super().validate(data)
        except Exception as e:
            raise AuthenticationFailed("The reset otp is invalid", 401)


class LocationModelserializers(serializers.ModelSerializer):
    class Meta:
        model = LocationModel
        fields = "__all__"

    # queryset=LocationModel.objects.all()
    # serializ
