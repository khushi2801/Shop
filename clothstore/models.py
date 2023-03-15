from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager, PermissionsMixin
import datetime

# Create your models here.
class myUserManager(UserManager):
    def create_user(self, name, email, password=None, **kwargs):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(name=name, email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name, email, password, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        
        return self.create_user(name, email, password, **kwargs)

class myUser(AbstractUser):
    user_type = models.CharField(max_length=20)
    username = None # Removing username field as Email is used as unique identifier
    name = models.CharField(max_length=50, null=False)
    email = models.EmailField(unique=True, null=False)

    objects = myUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    
    
class Product(models.Model):
    product_admin = models.ForeignKey(myUser, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, null=False)
    name = models.CharField(max_length=50, null=False)
    brand = models.CharField(max_length=50, null=False)
    size = models.CharField(max_length=5, null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    image = models.ImageField(upload_to='images/', null=False)
    date = models.DateField(default=datetime.date.today)

   
