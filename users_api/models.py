from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import validate_email
from model_utils import Choices
from core.validators import validate_phone_number
from .managers import UserManager


def upload_to(instance, filename):
    return f"upload_to/{instance.username}/{filename}"


class LocationModel(models.Model):
    address = models.CharField(max_length=50, default="Egypt")

    def __str__(self):
        return self.address


class UserModel(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50)
    email = models.EmailField(
        unique=True, null=False, blank=False, max_length=50, validators=[validate_email]
    )
    phone_number = models.CharField(
        unique=True,
        null=True,
        blank=True,
        max_length=11,
        validators=[validate_phone_number],
    )

    otp = models.CharField(max_length=4)
    otp_expiration = models.DateTimeField(null=True, blank=True)
    max_otp_try = models.CharField(max_length=2, default=settings.MAX_OTP_TRY)
    max_otp_out = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    registered_at = models.DateTimeField(auto_now_add=True)

    profile_photo = models.ImageField(
        upload_to=upload_to, default="upload_to/default.png"
    )

    age = models.IntegerField(null=True, blank=True)

    GENDER = Choices("male", "female")
    gender = models.CharField(choices=GENDER, default=GENDER.male, max_length=20)

    total_points = models.PositiveIntegerField(default=0)

    address = models.ForeignKey(
        LocationModel,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="address_name",
    )

    objects = UserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email

    @property
    def ranking(self):
        count = UserModel.objects.filter(total_points__gt=self.total_points).count()
        return count + 1

    class Meta:
        ordering = ("-total_points",)


class Feedback(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    user = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, related_name="feedbacks"
    )

    def __str__(self):
        return self.title
