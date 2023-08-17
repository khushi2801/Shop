from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class MyUserManager(UserManager):
    """
    Custom manager for the MyUser model that overrides the create_user() and create_superuser() methods
    to accept a name, email, and password, and set up a new user with those details. The email field is
    used as the unique identifier instead of the default username field. The create_superuser() method
    also sets the is_staff and is_superuser flags to True.

    Methods:
        create_user(name, email, password, **kwargs): Creates a new user with the given name, email, and 
            password, and saves it to the database.
        create_superuser(name, email, password, **kwargs): Creates a new superuser with the given name, 
            email, and password, and saves it to the database.
    """
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


class MyUser(AbstractUser):
    """
    A custom user model which uses email as the unique identifier instead of username.

    Attributes:
        user_type (str): The type of user.
        username: None. The username field is removed.
        name (str): The user's full name.
        email (str): The user's email address.
        objects (MyUserManager): The manager class that handles user creation and querying.
        USERNAME_FIELD (str): The field to use for authentication. In this case, it's set to 'email'.
        REQUIRED_FIELDS (list): A list of fields required for user creation. In this case, it's set to 'name'.
    """
    user_type = models.CharField(max_length=20)
    username = None
    name = models.CharField(max_length=50, null=False)
    email = models.EmailField(unique=True, null=False)
    objects = MyUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']


class UserProfile(models.Model):
    """
    A model representing a user's profile.

    Attributes:
        user (MyUser): The user whose profile this is.
        dob (datetime.date): The user's date of birth.
        address (str): The user's street address.
        city (str): The user's city.
        state (str): The user's state or province.
        country (str): The user's country.
        contact (phonenumbers.PhoneNumber): The user's phone number.
        pin (int): The user's postal code or ZIP code.
        image (str): The path to the user's profile image.
    """
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, related_name='profile')
    dob = models.DateField(null=True)
    address = models.CharField(max_length=150, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    contact = PhoneNumberField(unique=True, null=True, blank=True)
    pin = models.PositiveIntegerField(null=True, blank=True)
    image = models.ImageField(upload_to='profile_images/', default='profile.png', null=True, blank=True)