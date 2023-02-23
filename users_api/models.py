from django.db import models
from django.conf import settings
from django.contrib.auth.models import(
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import RegexValidator, validate_email

phone_number_regex=RegexValidator(
    regex=r"^\d{10}",message="Phone Number must be 10 number only ."
)
class UserManager(BaseUserManager):
    
    def create_user(self,email,password=None):
        if not email:
            raise ValueError("email is required .")
        user=self.model(email=email)
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
    
    email=models.EmailField(unique=True,null=False,blank=False,max_length=50,validators=[validate_email])
    phone_number=models.CharField(unique=True,null=True,blank=True,max_length=10,validators=[phone_number_regex])
    otp=models.CharField(max_length=4)
    otp_expiration=models.DateTimeField(null=True,blank=True)
    max_otp_try=models.CharField(max_length=2,default=settings.MAX_OTP_TRY)
    max_otp_out=models.DateTimeField(null=True,blank=True)
    is_active=models.BooleanField(default=False)
    is_staff=models.BooleanField(default=False)
    registered_at=models.DateTimeField(auto_now_add=True)
    
    objects=UserManager()
    
    USERNAME_FIELD="email"
    def __str__(self):
        return self.email