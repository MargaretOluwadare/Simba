from django.contrib import admin
from .models import Token, ActivityLog, AdminPlan, UserPlan

# Register your models here.
admin.site.register(Token)
admin.site.register(ActivityLog)


@admin.register(AdminPlan)
class AdminPlanAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "amount", "plan_type", "model", "is_enabled")
    search_fields = ("name", "model")
    list_filter = ("plan_type", "is_enabled")
    readonly_fields = ("date_created", "date_updated")


@admin.register(UserPlan)
class UserPlanAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "plan", "is_active", "expiry_date")
    search_fields = ("user__email", "plan__name")
    list_filter = ("is_active", "expiry_date")
    readonly_fields = ("date_created", "date_updated", "date_renewed")