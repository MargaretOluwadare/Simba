from django.db import models

from users.models import User
import uuid

# Create your models here.


class ActivityLog(models.Model):
    CATEGORY_CHOICES = (
        ("login", "LOGIN"),
        ("logout", "LOGOUT"),
        ("password_reset", "PASSWORD RESET"),
        ("mix_order", "MIX ORDER"),
        ("inventory_order", "INVENTORY_ORDER"),
        ("drink_created", "DRINKCREATED"),
        
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activity")
    category = models.CharField(choices=CATEGORY_CHOICES)
    description = models.CharField(max_length=200, blank=True)
    metadata = models.JSONField(null=True, blank=True) # extra context

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return f"{self.user.email} {self.category}"


# Reusable Token model
class Token(models.Model):
    CATEGORY_CHOICES = (
        ("password_reset", "Password Reset"),
        ("email_verification", "Email Verification"),
        ("api_key", "API Key"),
    )

    token = models.UUIDField(unique=True, default=uuid.uuid4)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tokens")

    used = models.BooleanField(default=False)
    metadata = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    expires_at = models.DateTimeField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.category} token for {self.user_id} ({self.token})"


class AdminPlan(models.Model):
    PLAN_TYPE_CHOICES = (
        ("subscription", "Subscription"),
        ("one_time", "One Time"),
    )

    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES)
    model = models.CharField(max_length=100)  # e.g. "subscription", "consultation"

    is_enabled = models.BooleanField(default=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.amount}"


class UserPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="plans")
    plan = models.ForeignKey(AdminPlan, on_delete=models.CASCADE, related_name="subscribers")

    is_active = models.BooleanField(default=True)
    expiry_date = models.DateTimeField()
    date_renewed = models.DateTimeField(blank=True, null=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.plan.name}"