from datetime import date
from django.db import models
from users_api.models import UserModel


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


class CompetitionRanking(models.Model):
    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
    )
    points = models.PositiveIntegerField(default=0, blank=True)

    @property
    def ranking(self) -> int:
        count = CompetitionRanking.objects.filter(
            competition=self.competition.pk, points__gt=self.points
        ).count()
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
