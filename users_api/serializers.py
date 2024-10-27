import random
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from fcm_django.models import FCMDevice
from fcm_django.api.rest_framework import FCMDeviceSerializer
from .models import UserModel, LocationModel, Feedback, LanguageChoices, TermsAndCondition, FAQ
from .services import send_otp, unread_notification
from machine_api.utlis import get_total_recycled_items

"""
    SIGN UP SERIALIZERS
"""
class CustomFCMDeviceSerializer(serializers.Serializer):
    type = serializers.CharField(required=False, allow_blank=True)
    registration_id = serializers.CharField(required=False, allow_blank=True)

class UserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, min_length=settings.MIN_PASSWORD_LENGTH, error_messages={"min_length": _("Password must be longer than 8 length")})
    password2 = serializers.CharField(write_only=True, min_length=settings.MIN_PASSWORD_LENGTH, error_messages={"min_length": _("Password must be longer than 8 length")})
    referral_code = serializers.CharField(write_only=True, required=False)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    fcm_device = CustomFCMDeviceSerializer(required=False)


    class Meta:
        model = UserModel
        fields = ["id", "username", "phone_number", "email", "password1", "password2", "referral_code", "country_code", "fcm_device"]

    # to check password validation in sign up form
    def validate(self, data):
        password1 = data.get("password1")
        password2 = data.get("password2")
        if password1 != password2:
            raise serializers.ValidationError(_("Passwords don't match"))
        referral_code = data.get("referral_code")
        if referral_code:
            try:
                UserModel.objects.get(referral_code=referral_code)
            except UserModel.DoesNotExist:
                raise serializers.ValidationError(_("Invalid referral code"))
        return data

    # create and return user with encrybted password
    def create(self, val_data):
        otp = random.randint(1000, 9999)
        otp_expiration = timezone.now() + timedelta(minutes=5)
        if val_data.get("phone_number"):
            user = UserModel(username=val_data["username"], phone_number=val_data["phone_number"], email=val_data["email"], otp=otp, otp_expiration=otp_expiration, max_otp_try=settings.MAX_OTP_TRY, country_code=val_data["country_code"])
        else:
            user = UserModel(username=val_data["username"], email=val_data["email"], otp=otp, otp_expiration=otp_expiration, max_otp_try=settings.MAX_OTP_TRY, country_code=val_data["country_code"])
        user.set_password(val_data["password1"])
        referral_code = val_data.get("referral_code")
        if referral_code:
            referring_user = UserModel.objects.get(referral_code=referral_code)
            referring_user.total_points += int((10*referring_user.total_points)/100)
            referring_user.referral_usage_count += 1
            referring_user.save()
            user.total_points += 10
        user.save()
        send_otp(user)
        return user

"""
    CUSTOM TOKEN OBTAIN PAIR SERIALIZER FROM REST_FRAMEWORK_SIMPLEJWT
"""
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user.is_active:
            otp = random.randint(1000, 9999)
            otp_expiration = timezone.now() + timedelta(minutes=5)
            self.user.otp = otp
            self.user.otp_expiration = otp_expiration
            self.user.save()
            send_otp(self.user)
            return {"is_verified": False, "id": self.user.id}
        fcm_data = self.context['request'].data.get("fcm_device", {})
        fcm_registration_id = fcm_data.get("registration_id")
        fcm_device_type = fcm_data.get("type")
        # Register or update FCM device
        if fcm_registration_id and fcm_device_type:
            fcm_device, created = FCMDevice.objects.get_or_create(user=self.user, defaults={"registration_id": fcm_registration_id, "type": fcm_device_type})
            if not created and fcm_device.registration_id != fcm_registration_id:
                fcm_device.registration_id = fcm_registration_id
                fcm_device.type = fcm_device_type
                fcm_device.save()

        unread_notifications, count = unread_notification(self.user)
        data["username"] = self.user.username
        data["email"] = self.user.email
        data["id"] = self.user.id
        data["phone_number"] = self.user.phone_number
        data["country_code"] = self.user.country_code
        data["profile_photo"] = self.user.profile_photo.url if self.user.profile_photo else None
        data["age"] = self.user.age
        data["gender"] = self.user.gender
        data["address"] = self.user.address.address if self.user.address else None
        data["referral_code"] = self.user.referral_code
        data["referral_usage_count"] = self.user.referral_usage_count
        data["preferred_language"] = self.user.preferred_language
        data["total_points"] = self.user.total_points
        data["total_recycled_items"] = get_total_recycled_items(self.user.id)
        data["unread_notifications"] = unread_notifications
        data["unread_notifications_count"] = count
        data["is_admin"] = self.user.is_staff
        return data

"""
    FORGOT PASSWORD SERIALIZERS
"""
class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    class Meta:
        fields = ["email"]

class OTPOnlySerializer(serializers.Serializer):
    otp = serializers.CharField(min_length=4, max_length=4, write_only=True)
    class Meta:
        fields = ["otp"]

class OTPSerializer(serializers.Serializer):
    otp = serializers.CharField(min_length=4, max_length=4, write_only=True)
    email = serializers.EmailField()
    class Meta:
        fields = ["email", "otp"]

    def validate(self, data):
        otp = data.get("otp", "")
        email = data.get("email", "")
        user = UserModel.objects.filter(email=email).first()
        if user:
            if not (user.otp == otp and user.otp_expiration > timezone.now()):
                raise ValidationError({"detail": _("Invalid OTP")})
        else:
            raise ValidationError({"detail": _("Invalid Email")})
        return data

class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=settings.MIN_PASSWORD_LENGTH, max_length=68, write_only=True)
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
            if user.otp == otp and user.otp_expiration > timezone.now():
                user.set_password(password)
                user.max_otp_try = settings.MAX_OTP_TRY
                user.save()
            else:
                raise ValidationError({"detail": _("Invalid OTP")})
        else:
            raise ValidationError({"detail": _("Invalid Email")})
        return data

"""
    PROFILE UPDATE SERIALIZERS
"""
class UserProfileSerializer(UserSerializer):
    class Meta:
        model = UserModel
        fields = ["username", "phone_number", "age", "email", "password1", "password2", "profile_photo", "gender", "address", "preferred_language"]

    def update(self, instance, val_data):
        """update profile for User"""
        password = val_data.pop("password1", None)
        user = super().update(instance, val_data)
        if password:
            user.set_password(password)
            user.save()
        return user

class PreferredLanguageSerializer(serializers.ModelSerializer):
    preferred_language = serializers.ChoiceField(choices=LanguageChoices.choices)
    class Meta:
        model = UserModel
        fields = ["preferred_language"]

class LocationModelserializers(serializers.ModelSerializer):
    class Meta:
        model = LocationModel
        fields = "__all__"

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = "__all__"
        read_only_fields = ("user",)

    def create(self, val_data):
        user = self.context["request"].user
        feedback = Feedback.objects.create(title=val_data["title"], description=val_data["description"], user=user,)
        return feedback

class TopUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ["id", "username", "profile_photo", "total_points"]
        read_only_fields = fields

class TermsAndConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermsAndCondition
        fields = ['about_app_en', 'about_app_ar', 'description_en', 'description_ar']

class FAQsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['question_en', 'question_ar', 'terms_en', 'terms_ar', 'privacy_en', 'privacy_ar']

from machine_api.models import RecycleLog
from django.db.models import Sum
from machine_api.utlis import calculate_points
class UserPointsSerializer(serializers.ModelSerializer):
    points = serializers.SerializerMethodField()
    def get_points(self, obj):
        logs = RecycleLog.objects.filter(user=obj)
        if logs:
            total_bottles = logs.aggregate(Sum("bottles"))["bottles__sum"]
            total_cans = logs.aggregate(Sum("cans"))["cans__sum"]
            _, _, total_points = calculate_points(total_bottles, total_cans)
            return total_points
        else:
            return 0
    class Meta:
        model = UserModel
        fields = ["email", "points"]
        read_only_fields = fields