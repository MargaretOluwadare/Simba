from django.contrib import admin
from .models import Pet, VaccinationRecord


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "breed", "age", "owner", "date_created")
    search_fields = ("name", "breed", "owner__email")
    list_filter = ("breed", "date_created")
    readonly_fields = ("date_created", "date_updated")


@admin.register(VaccinationRecord)
class VaccinationRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "pet", "date_created")
    search_fields = ("pet__name", "pet__owner__email")
    list_filter = ("date_created",)
    readonly_fields = ("date_created", "date_updated")