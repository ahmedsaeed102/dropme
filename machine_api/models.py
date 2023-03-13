import qrcode
from io import BytesIO
from PIL import Image
from django.core.files import File
from django.urls import reverse
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils import Choices
from users_api.models import UserModel


STATUS = Choices('available', 'break down')


class Machine(models.Model):
    identification_name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name = _('Machine name'),
        help_text = _('Unique identification name for the machine, max-length:200')
    )
    
    longitude = models.DecimalField(
        max_digits = 9,
        decimal_places = 6,
        blank= True,
        help_text = _('Longitude, Format:required')
    )

    latitdue = models.DecimalField(
        max_digits = 9,
        decimal_places = 6,
        blank= True,
        help_text = _('Latitdue, Format:required')
    )

    location = models.CharField(max_length=50)
    place = models.CharField(max_length=50)

    status = models.CharField(choices=STATUS, default=STATUS.available, max_length=20)

    qr_code = models.ImageField(upload_to='qr_codes', blank=True)

    def save(self, *args, **kwargs):
        qrcode_img = qrcode.make("Test")
        canvas = Image.new('RGB', (290, 290), 'white')
        canvas.paste(qrcode_img)
        fname = f'qr_code-{self.identification_name}.png'
        buffer = BytesIO()
        canvas.save(buffer,'PNG')
        self.qr_code.save(fname, File(buffer), save=False)
        canvas.close()
        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        self.qr_code.storage.delete(self.qr_code.name)
        super().delete()

    @property
    def address(self):
        return f'{self.location}, {self.place}'

    def __str__(self):
        return self.identification_name
    

class RecycleLog(models.Model):
    machine_name = models.CharField(max_length=200)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    bottles = models.PositiveSmallIntegerField(default=0, blank=True,)
    cans = models.PositiveSmallIntegerField(default=0, blank=True,)
    points = models.IntegerField(default=0, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username