from django.db import models
from users.models import User


# Create your models here.
class Wallet(models.Model):
    CURRENCY_CHOICES = (("usd", "USD"), ("ngn", "NGN"))
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wallet")

    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default="ngn")
    balance = models.DecimalField(max_digits=12, decimal_places=2)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        first = self.user.first_name or ""
        last = self.user.last_name or ""

        full_name = f"{first} {last}".strip()

        return f"{full_name if full_name else self.user.email}'s Wallet - {self.currency}{self.balance}"


class Transaction(models.Model):
    TYPE_CHOICES = (("debit", "Debit"), ("credit", "Credit"))

    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name="transactions"
    )
    reference = models.CharField(max_length=255, unique=True)

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    reference = models.CharField(max_length=255)  # paystack ref id
    metadata = models.JSONField(blank=True, null=True, default=dict)
    # need to store paystack reference

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        full_name = (
            f"{self.wallet.user.first_name or ""} {self.wallet.user.last_name or ""}".strip()
        )
        return f"{self.transaction_type} - {self.wallet.currency} {self.amount} - {full_name if full_name else self.wallet.user.email} Wallet"
