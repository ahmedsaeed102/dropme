from django.db import models
from core.validators import validate_phone_number
from users_api.models import UserModel
from django.contrib.gis.db.models import PointField


STATUS = (
    ("available", "available"),
    ("breakdown", "breakdown"),
)
STATUS_AR = (
    ("متاح", "متاح"),
    ("لا تعمل", "لا تعمل"),
)


class Machine(models.Model):
    identification_name = models.CharField(
        max_length=200,
        unique=True,
    )
    name_ar = models.CharField(max_length=200, blank=True, null=True)

    location = PointField(null=True, srid=4326, blank=True)

    city = models.CharField(max_length=50, null=True)
    city_ar = models.CharField(max_length=50, blank=True, null=True)

    place = models.CharField(
        max_length=200,
        null=True,
    )
    place_ar = models.CharField(
        max_length=200,
        blank=True,
        null=True,
    )

    status = models.CharField(choices=STATUS, default="available", max_length=20)
    status_ar = models.CharField(choices=STATUS_AR, default="متاح", max_length=20)

    qr_code = models.ImageField(upload_to="qr_codes", blank=True)

    def delete(self, using=None, keep_parents=False):
        self.qr_code.storage.delete(self.qr_code.name)
        super().delete()

    @property
    def address(self):
        return f"{self.city}, {self.place}"

    def __str__(self):
        return self.identification_name


class RecycleLog(models.Model):
    machine_name = models.CharField(max_length=200)
    user = models.ForeignKey(
        UserModel,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="user_logs",
    )

    phone = models.ForeignKey(
        "PhoneNumber", null=True, blank=True, on_delete=models.CASCADE
    )

    bottles = models.IntegerField(
        default=0,
        blank=True,
    )
    cans = models.IntegerField(
        default=0,
        blank=True,
    )
    points = models.IntegerField(default=0, blank=True)
    channel_name = models.CharField(max_length=300, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    in_progess = models.BooleanField(default=False)
    is_complete = models.BooleanField(default=False)


# for using the machine without creating account
class PhoneNumber(models.Model):
    phone_number = models.CharField(
        unique=True,
        max_length=11,
        validators=[validate_phone_number],
    )

    points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.phone_number
