from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from .managers import UserManager
from django.utils import timezone

# Create your models here.
class User(AbstractUser, PermissionsMixin):
    USER_TYPE_CHOICES = (("customer", "Customer"), ("vet", "Vet"))

    MFA_TYPE_CHOICES = (("authenticator", "Authenticator"), ("email", "Email"))

    email = models.EmailField(unique=True)
    user_type = models.CharField(
        max_length=20, choices=USER_TYPE_CHOICES, default="customer"
    )
    mfa = models.BooleanField(default=False)
    mfa_type = models.CharField(
        max_length=20, choices=MFA_TYPE_CHOICES, blank=True, null=True
    )
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    
    permissions = models.ManyToManyField(
        'auth.permission',
        verbose_name='user permissions',
        blank=True,
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    
    objects = UserManager()

    def __str__(self):
        return f"{self.email} - {self.user_type}"
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.URLField(blank=True, null=True)
    first_name = models.CharField(max_length=60, blank=True, null=True)
    last_name = models.CharField(max_length=60, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.email}'s Profile"
    
class EmailOTP(models.Model):
    code_hash = models.CharField(max_length=128, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="email_otp")
    is_active = models.BooleanField(default=True)

    expires_at = models.DateTimeField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def is_valid(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.user.email} - {self.created_at}"


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")

    label = models.CharField(max_length=100)  # home, office
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
class Vet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    is_enabled = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True) # close time
    
    opens_at = models.TimeField()
    closes_at = models.TimeField()
    
    description = models.CharField(max_length=500)
  