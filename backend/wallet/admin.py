from django.contrib import admin
from .models import Wallet, Transaction


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "currency", "balance", "date_created")
    search_fields = ("user__email",)
    list_filter = ("currency",)
    readonly_fields = ("date_created", "date_updated")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "wallet", "amount", "transaction_type", "reference", "date_created")
    search_fields = ("wallet__user__email", "reference")
    list_filter = ("transaction_type", "date_created")
    readonly_fields = ("date_created", "date_updated")