from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _
from model_utils import Choices
from core.validators import validate_phone_number
import random
from .managers import UserManager

class LanguageChoices(models.TextChoices):
    ARABIC = 'ARABIC', 'Arabic'
    ENGLISH = 'ENGLISH', 'English'

def upload_to(instance, filename):
    return f"upload_to/{instance.username}/{filename}"


class LocationModel(models.Model):
    address = models.CharField(max_length=50, default="Egypt")

    def __str__(self):
        return self.address

def generate_referral_code(user):
        prefix = user.username[:3].lower()
        date_str = random.randint(10000000, 99999999)
        while UserModel.objects.filter(referral_code=f"{prefix}{date_str}").exists():
            date_str = random.randint(10000000, 99999999)
        return f"{prefix}{date_str}"

class UserModel(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50)
    email = models.EmailField(unique=True, null=False, blank=False, max_length=50, validators=[validate_email], verbose_name=_("Email"))
    phone_number = models.CharField(null=True, blank=True, max_length=11, validators=[validate_phone_number])
    country_code = models.CharField(max_length=50, default="+20")

    #otp = models.CharField(max_length=4)
    #otp_expiration = models.DateTimeField(null=True, blank=True)
    #max_otp_try = models.CharField(max_length=2, default=settings.MAX_OTP_TRY)
    #max_otp_out = models.DateTimeField(null=True, blank=True)

    akedly_transaction_id = models.CharField(max_length=255, null=True, blank=True)
    akedly_request_id = models.CharField(max_length=255, null=True, blank=True)

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    registered_at = models.DateTimeField(auto_now_add=True)

    profile_photo = models.ImageField(upload_to=upload_to, default="upload_to/default.png")
    age = models.IntegerField(null=True, blank=True)
    GENDER = Choices("male", "female")
    gender = models.CharField(choices=GENDER, null=True, blank=True, max_length=20)
    total_points = models.PositiveIntegerField(default=0)
    address = models.CharField(max_length=225, null=True, blank=True)
    referral_code = models.CharField(max_length=15, unique=True, null=True, blank=True)
    referral_usage_count = models.PositiveIntegerField(default=0)
    preferred_language = models.CharField(max_length=10, choices=LanguageChoices.choices, default=LanguageChoices.ENGLISH)
    oauth_medium = models.CharField(max_length=50, null=True, blank=True)
    password_set = models.BooleanField(default=True)

    objects = UserManager()
    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = generate_referral_code(self)
        super().save(*args, **kwargs)

    @property
    def ranking(self):
        count = UserModel.objects.filter(total_points__gt=self.total_points).count()
        return count + 1

    class Meta:
        ordering = ("-total_points",)
        verbose_name = _("User")

class Feedback(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name="feedbacks")
    name = models.CharField(max_length=50, default="app")
    type = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.title

class TermsAndCondition(models.Model):
    about_app_en = models.TextField(null=True, blank=True)
    about_app_ar = models.TextField(null=True, blank=True)
    terms_en = models.TextField(null=True, blank=True)
    terms_ar = models.TextField(null=True, blank=True)
    privacy_en = models.TextField(null=True, blank=True)
    privacy_ar = models.TextField(null=True, blank=True)


    def __str__(self):
        return f"{self.id}"

class FAQ(models.Model):
    question_en = models.TextField(null=True, blank=True)
    question_ar = models.TextField(null=True, blank=True)
    answer_en = models.TextField(null=True, blank=True)
    answer_ar = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.question_en