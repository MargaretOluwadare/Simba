from django.contrib import admin
from .models import User, Profile, EmailOTP, Address, Vet


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "user_type", "is_active", "is_staff", "date_created")
    search_fields = ("email",)
    list_filter = ("user_type", "is_active", "is_staff")
    readonly_fields = ("date_created", "date_updated")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user")
    search_fields = ("user__email",)


@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "is_active", "expires_at", "created_at")
    search_fields = ("user__email",)
    list_filter = ("is_active",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "label", "city", "country", "is_default")
    search_fields = ("user__email", "city", "country")
    list_filter = ("is_default", "country")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Vet)
class VetAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "is_enabled", "is_available")
    search_fields = ("user__email",)
    list_filter = ("is_enabled", "is_available")


admin.site.site_header = "Simba Admin"
admin.site.site_title = "Simba"
admin.site.index_title = "Welcome to Simba"

