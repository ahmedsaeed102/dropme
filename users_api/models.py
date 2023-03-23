from django.db import models
from django.conf import settings
from django.contrib.auth.models import(
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from model_utils import Choices
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, validate_email

class LocationModel(models.Model):
    address=models.CharField(max_length=50, default='Egypt')
    def __str__(self) :
        return self.address

def upload_to(instance,filename):
    return 'users_api/{filename}'.format(filename=filename)

phone_number_regex=RegexValidator(
    regex=r"^\d{10}",message="Phone Number must be 10 number only ."
)
class UserManager(BaseUserManager):
    
    def create_user(self,email,password=None,**extra_fields):
        if not email:
            raise ValueError("email is required .")
        user=self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self,email,password):
        user=self.create_user(email,password)
        user.is_active=True
        user.is_staff=True
        user.is_superuser=True
        user.save(using=self._db)
        return user
    
class UserModel(AbstractBaseUser,PermissionsMixin):
    username=models.CharField(max_length=50)
    email=models.EmailField(unique=True,null=False,blank=False,max_length=50,validators=[validate_email])
    phone_number=models.CharField(unique=True,null=True,blank=True,max_length=10,validators=[phone_number_regex])

    otp=models.CharField(max_length=4)
    otp_expiration=models.DateTimeField(null=True,blank=True)
    max_otp_try=models.CharField(max_length=2,default=settings.MAX_OTP_TRY)
    max_otp_out=models.DateTimeField(null=True,blank=True)

    is_active=models.BooleanField(default=False)
    is_staff=models.BooleanField(default=False)
    registered_at=models.DateTimeField(auto_now_add=True)

    profile_photo=models.ImageField(upload_to='upload_to', default='upload_to/default.jpg')

    GENDER = Choices('male', 'female')
    gender=models.CharField(choices=GENDER,default=GENDER.male, max_length=20) 

    total_points=models.PositiveIntegerField(
        default=0, 
        help_text = _('User total earned points')
    )

    address = models.ForeignKey(LocationModel, on_delete=models.CASCADE, null=True, default=1)
    
    objects=UserManager()
    
    USERNAME_FIELD="email"
    
    def __str__(self):
        return self.email
    
    
    def get_image_url(self):
        return f"/media/{self.profile_photo}"
    
    @property
    def ranking(self):
        count = UserModel.objects.filter(total_points__gt=self.total_points).count()
        return count + 1

    class Meta:
        ordering = ('-total_points',)
    
    
# class ResetPasswordModel(models.Model):
#     user=models.ForeignKey(UserModel, on_delete=models.CASCADE)
#     reset_pass_token=models.CharField(null=True,blank=True,max_length=200)
#     created_at=models.DateTimeField(auto_now_add=True)
#     updated_at=models.DateTimeField(auto_now=True)
    
        
#     def __str__(self):
#         return self.user.email



