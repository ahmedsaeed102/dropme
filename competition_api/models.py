from datetime import date
from django.db import models
from django.utils.translation import gettext_lazy as _
from users_api.models import UserModel


class Competition(models.Model):
    name = models.CharField(
        max_length=100,
        help_text = _('Format: required, max-length:100')
    )
    description = models.TextField(
        max_length=500,
        null = True,
        blank = True,
        help_text = _('Format: optional, max-length:500')
    )
    target = models.PositiveIntegerField(
        default = 0,
        help_text = _('Competition target points'),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField(
        help_text = _('Competition start date'),
    )
    end_date = models.DateField(
        help_text = _('Competition end date'),
    )

    users = models.ManyToManyField(UserModel, through="CompetitionRanking", related_name="comp_user")

    @property
    def is_ongoing(self):
        return self.end_date > date.today()

    def __str__(self):
        return self.name

class CompetitionRanking(models.Model):
    competition = models.ForeignKey(
        Competition,
        on_delete = models.CASCADE,
    )
    user = models.ForeignKey(
        UserModel,
        on_delete = models.CASCADE,
    )
    points = models.PositiveIntegerField(
        default = 0,
        blank = True,
        help_text = _('user points in competition'),
    )

    @property
    def ranking(self):
        count = CompetitionRanking.objects.filter(competition=self.competition.pk, points__gt=self.points).count()
        return count + 1

    class Meta:
        ordering = ('-points',)

    def __str__(self):
        return f'{self.competition.name} | {self.user.username}'