from datetime import date
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from users_api.models import UserModel
from notification.models import NotificationImage
from notification.services import notification_send_all

class Competition(models.Model):
    name = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(max_length=500, null=True, blank=True)
    description_ar = models.TextField(max_length=500, null=True, blank=True)
    target = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField()
    users = models.ManyToManyField(UserModel, through="CompetitionRanking", related_name="comp_user")

    @property
    def is_ongoing(self) -> bool:
        return self.end_date > date.today()

    @property
    def duration(self):
        return (self.end_date - self.start_date).days

    def __str__(self) -> str:
        return self.name

@receiver(post_save, sender=Competition)
def Competition_created(sender, instance, created, **kwargs):
    if NotificationImage.objects.filter(name="new_competition").exists():
        image = NotificationImage.objects.filter(name="new_competition").first().image
    else:
        image = None
    if created:
        notification_send_all(
            title="New Competition", 
            body="New competition created check it out!",
            title_ar="مسابقة جديدة",
            body_ar="تم إنشاء مسابقة جديدة، تحقق منها!",
            image=image,
            type="competition",
            extra_data={"room_name": None, "id": instance.id, "extra":None}
        )

class CompetitionRanking(models.Model):
    competition = models.ForeignKey(Competition,on_delete=models.CASCADE)
    user = models.ForeignKey(UserModel,on_delete=models.CASCADE, unique=True)
    points = models.PositiveIntegerField(default=0, blank=True)

    @property
    def ranking(self) -> int:
        count = CompetitionRanking.objects.filter(competition=self.competition.pk, points__gt=self.points).count()
        return count + 1

    class Meta:
        ordering = ("-points",)

    def __str__(self) -> str:
        return f"{self.competition.name} | {self.user.username}"

class Resource(models.Model):
    name = models.CharField(max_length=100)
    img = models.ImageField(upload_to="resource", blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    resource_type = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} | {self.resource_type}"
