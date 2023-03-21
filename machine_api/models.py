from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils import Choices
from users_api.models import UserModel
from django.contrib.gis.db.models import PointField


STATUS = Choices('available', 'breakdown')


class Machine(models.Model):
    identification_name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name = _('Machine name'),
        help_text = _('[required] Unique identification name for the machine, max-length:200')
    )
    
    location = PointField(null=True, srid=4326)

    # gives error when trying to remove longitude and latitdue
    longitude = models.DecimalField(
        max_digits = 9,
        decimal_places = 6,
        blank= True,
        null=True, 
    ) 

    latitdue = models.DecimalField(
        max_digits = 9,
        decimal_places = 6,
        blank= True,
        null=True,
    )

    city = models.CharField(max_length=50, null=True, help_text = _('Machine city'))
    place = models.CharField(max_length=50, null=True, help_text = _('machin place inside city'))

    status = models.CharField(choices=STATUS, default=STATUS.available, max_length=20)

    qr_code = models.ImageField(upload_to='qr_codes', blank=True)

    # def save(self, *args, **kwargs):
    #     path = reverse("start_recycle", kwargs={'name':self.identification_name})
    #     domain = Site.objects.get_current().domain
    #     qrcode_img = qrcode.make('http://{domain}{path}'.format(domain=domain, path=path))
    #     # canvas = Image.new('RGB', (400, 400), 'white')
    #     # canvas.paste(qrcode_img)
    #     fname = f'qr_code-{self.identification_name}.png'
    #     buffer = BytesIO()
    #     # canvas.save(buffer,'PNG')
    #     qrcode_img.save(buffer,'PNG')
    #     self.qr_code.save(fname, File(buffer), save=False)
    #     # canvas.close()
    #     super().save(*args, **kwargs)
    

    def delete(self, using=None, keep_parents=False):
        self.qr_code.storage.delete(self.qr_code.name)
        super().delete()

    @property
    def address(self):
        return f'{self.city}, {self.place}'

    def __str__(self):
        return self.identification_name
    

class RecycleLog(models.Model):
    machine_name = models.CharField(max_length=200)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    bottles = models.PositiveSmallIntegerField(default=0, blank=True,)
    cans = models.PositiveSmallIntegerField(default=0, blank=True,)
    points = models.IntegerField(default=0, blank=True) 
    channel_name = models.CharField(max_length=300, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    in_progess = models.BooleanField(default=False)
    is_complete = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username