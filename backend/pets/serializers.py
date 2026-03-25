from rest_framework import serializers
from .models import Pet, VaccinationRecord


class PetSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.id")

    class Meta:
        model = Pet
        fields = "__all__"
        read_only_fields = ("owner", "date_created", "date_updated")


class VaccinationRecordSerializer(serializers.ModelSerializer):
    pet = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = VaccinationRecord
        fields = "__all__"
        read_only_fields = ("pet", "date_created", "date_updated")