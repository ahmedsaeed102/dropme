from django.db import models
from core.validators import validate_phone_number
from django.contrib.gis.db.models import PointField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import FileExtensionValidator

from notification.services import notification_send_all
from notification.models import NotificationImage
from users_api.models import UserModel

def upload_to_videos(instance, filename):
    return f"machine/videos/{filename}"

STATUS = (
    ("available", "available"),
    ("breakdown", "breakdown"),
)
STATUS_AR = (
    ("متاح", "متاح"),
    ("لا تعمل", "لا تعمل"),
)

class Machine(models.Model):
    identification_name = models.CharField(max_length=200,unique=True,)
    name_en = models.CharField(max_length=200, blank=True, null=True)
    name_ar = models.CharField(max_length=200, blank=True, null=True)
    location = PointField(null=True, srid=4326, blank=True)
    city = models.CharField(max_length=50, null=True)
    city_ar = models.CharField(max_length=50, blank=True, null=True)
    place = models.CharField(max_length=200,null=True)
    place_ar = models.CharField(max_length=200,blank=True,null=True)
    status = models.CharField(choices=STATUS, default="available", max_length=20)
    status_ar = models.CharField(choices=STATUS_AR, default="متاح", max_length=20)
    qr_code = models.ImageField(upload_to="qr_codes", blank=True)
    ordering = models.IntegerField(null=True, blank=True, unique=True)

    def delete(self, using=None, keep_parents=False):
        self.qr_code.storage.delete(self.qr_code.name)
        super().delete()

    @property
    def address(self):
        return f"{self.city}, {self.place}"

    def __str__(self):
        return self.identification_name

@receiver(post_save, sender=Machine)
def machine_created(sender, instance, created, **kwargs):
    if NotificationImage.objects.filter(name="new_machine").exists():
        image = NotificationImage.objects.filter(name="new_machine").first().image
    else:
        image = None
    if created:
        notification_send_all(
            title="New Machine", 
            body="New Machine has been added",
            title_ar="ماكينة جديدة",
            body_ar="تم أضافة ماكينة جديدة.",
            image=image
        )

class RecycleLog(models.Model):
    machine_name = models.CharField(max_length=200)
    user = models.ForeignKey(UserModel,null=True,blank=True,on_delete=models.CASCADE,related_name="user_logs")
    phone = models.ForeignKey("PhoneNumber", null=True, blank=True, on_delete=models.CASCADE)
    bottles = models.IntegerField(default=0,blank=True)
    cans = models.IntegerField(default=0,blank=True)
    points = models.IntegerField(default=0, blank=True)
    channel_name = models.CharField(max_length=300, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    in_progess = models.BooleanField(default=False)
    is_complete = models.BooleanField(default=False)

    def __str__(self):
        if not self.user:
            return self.machine_name + " " + str(self.phone.phone_number)
        return self.machine_name + " " + str(self.user.username)

class PhoneNumber(models.Model):
    phone_number = models.CharField(unique=True,max_length=11,validators=[validate_phone_number],)
    points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.phone_number

class MachineVideo(models.Model):
    name = models.CharField(max_length=200)
    video = models.FileField(upload_to=upload_to_videos, validators=[FileExtensionValidator(allowed_extensions=["MOV", "avi", "mp4", "webm", "mkv"])])

    def delete(self, using=None, keep_parents=False):
        self.video.storage.delete(self.video.name)
        super().delete()

    def __str__(self):
        return self.name