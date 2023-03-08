from django.db import models
from django.utils.translation import gettext_lazy as _
# Create your models here.


class Machine(models.Model):
    name = models.CharField(
        max_length=200,
        null = False,
        blank = False,
        verbose_name = _('Machine name'),
        help_text = _('Format: required, max-length:200')
    )
    longitude = models.DecimalField(
        max_digits = 9,
        decimal_places = 6,
        null = True,
        blank = True,
        verbose_name = _('Longitude'),
        help_text = _('Format:required')
    )

    latitdue = models.DecimalField(
        max_digits = 9,
        decimal_places = 6,
        null = True,
        blank = True,
        verbose_name = _('Latitdue'),
        help_text = _('Format:required')
    )

    qr_code = models.CharField(
        max_length = 50,
        null = False,
        blank = False,
        verbose_name = _('Machine Code'),
        help_text = _('Format: required, max-length:50'),
    )

    class Meta:
        verbose_name = _('Machine details')
        verbose_name_plural = _('Machines details')

    def __str__(self):
        return self.name