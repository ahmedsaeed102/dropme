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
from machine_api.models import PhoneNumber
from machine_api.utlis import get_total_recycled_items
from utils.AkedlyClient import create_otp_transaction, activate_otp_transaction, verify_otp

"""
    SIGN UP SERIALIZERS
"""
class CustomFCMDeviceSerializer(serializers.Serializer):
    type = serializers.CharField(required=False, allow_blank=True)
    registration_id = serializers.CharField(required=False, allow_blank=True)

class UserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    referral_code = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = UserModel
        fields = (
            "username", "email", "phone_number", "country_code",
            "password1", "referral_code","akedly_transaction_id", "akedly_request_id"
        )

    def create(self, val_data):
        user = UserModel(
            username=val_data["username"],
            email=val_data["email"],
            phone_number=val_data.get("phone_number"),
            country_code=val_data.get("country_code", "+20"),
        )
        user.set_password(val_data["password1"])

        # Handle referral
        referral_code = val_data.get("referral_code")
        if referral_code:
            try:
                referring_user = UserModel.objects.get(referral_code=referral_code)
                reward = int((10 * referring_user.total_points) / 100) if referring_user.total_points > 0 else 5
                referring_user.total_points += reward
                referring_user.referral_usage_count += 1
                referring_user.save()
                user.total_points += 5
            except UserModel.DoesNotExist:
                raise serializers.ValidationError(_("Invalid referral code."))

        user.save()

        # Send OTP via Akedly
        try:
            full_phone = f"{user.country_code}{user.phone_number}"
            transaction_id = create_otp_transaction(full_phone, user.email)
            request_id = activate_otp_transaction(transaction_id)
            user.akedly_transaction_id = transaction_id
            user.akedly_request_id = request_id
            user.save()
        except Exception as e:
            user.delete()
            raise serializers.ValidationError({"otp": _(f"Akedly OTP failed: {str(e)}")})

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
            fcm_device, created = FCMDevice.objects.get_or_create(user=self.user, defaults={"registration_id": fcm_registration_id, "type": fcm_device_type, "name": self.user.username})
            if not created and fcm_device.registration_id != fcm_registration_id:
                fcm_device.registration_id = fcm_registration_id
                fcm_device.type = fcm_device_type
                fcm_device.name = self.user.username
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
        data["address"] = self.user.address
        data["referral_code"] = self.user.referral_code
        data["referral_usage_count"] = self.user.referral_usage_count
        data["preferred_language"] = self.user.preferred_language
        data["total_points"] = self.user.total_points
        data["total_recycled_items"] = get_total_recycled_items(self.user.id)
        data["unread_notifications"] = unread_notifications
        data["unread_notifications_count"] = count
        data["is_admin"] = self.user.is_staff
        data["password_set"] = self.user.password_set
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
    old_password = serializers.CharField(required=False)
    password2 = serializers.CharField(required=False)

    class Meta:
        model = UserModel
        fields = ["username", "phone_number", "age", "email", "password1", "password2", "profile_photo", "gender", "address", "preferred_language", "country_code", 'old_password']

    def update(self, instance, val_data):
        """update profile for User"""
        old_password = val_data.pop("old_password", None)
        password = val_data.pop("password1", None)
        confirm_password = val_data.pop("password2", None)
        phone_number = val_data.get("phone_number", None)
        user = super().update(instance, val_data)
        if phone_number:
            print("phone_number", phone_number)
            phone = PhoneNumber.objects.filter(phone_number=phone_number).first()
            print(phone)
            if phone:
                instance.total_points += phone.points
                RecycleLog.objects.filter(phone=phone).update(user=instance)
                phone.delete()
            instance.save()
        if user.password_set and password:
            if not old_password:
                raise ValidationError({"detail": _("old_password, password1 are required")})
            if not user.check_password(old_password):
                raise ValidationError({"detail": _("Invalid password")})
            user.set_password(password)
            user.save()
        elif not user.password_set and password:
            if not confirm_password:
               raise ValidationError({"detail": _("password1, password2 are required")})
            if password != confirm_password:
                raise ValidationError({"detail": _("Passwords don't match")})
            user.set_password(password) 
            user.password_set = True
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
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    type = serializers.CharField(required=True)
    name = serializers.CharField(required=False)

    class Meta:
        model = Feedback
        fields = "__all__"
        read_only_fields = ("user",)

    def create(self, val_data):
        user = self.context["request"].user
        if val_data.get("name"):
            feedback = Feedback.objects.create(title=val_data["title"], description=val_data["description"], user=user, type=val_data["type"], name=val_data['name'])
        else:
            feedback = Feedback.objects.create(title=val_data["title"], description=val_data["description"], user=user, type=val_data["type"])
        return feedback

class TopUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ["id", "username", "profile_photo", "total_points"]
        read_only_fields = fields

class SocialLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField()
    unique_id = serializers.CharField()
    medium = serializers.ChoiceField(choices=['google', 'apple', 'facebook'])
    phone_number = serializers.CharField(required=False, allow_blank=True)
    fcm_device = CustomFCMDeviceSerializer(required=False)

class TermsAndConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermsAndCondition
        fields = "__all__"

class FAQsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['question_en', 'question_ar', 'answer_en', 'answer_ar']

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