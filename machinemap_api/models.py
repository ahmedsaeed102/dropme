from django.utils.translation import gettext_lazy as _
from django.contrib.gis.db import models
# Create your models here.
class Machine(models.Model):
    name = models.CharField(
    max_length=200,
    null = False,
    blank = False,
    verbose_name = _('Machine name'),
    help_text=_("Format: required, max = 200 Charachter")
    )
    
    location = models.PointField()
    
    qr_code = models.CharField(
        max_length = 500, 
        null = False,
        blank = False,
        verbose_name = _("Machine Qrcode"),
        help_text = _("Format : uneditable, get get replaced with each transaction")
    )

    class Meta:
        verbose_name = _("Machine")
        verbose_name_plural = _("Machines")

    def __str__(self):
        return self.name