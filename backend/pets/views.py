from rest_framework import viewsets
from .models import Pet, VaccinationRecord
from .serializers import PetSerializer, VaccinationRecordSerializer


class PetViewSet(viewsets.ModelViewSet):
    serializer_class = PetSerializer

    def get_queryset(self):
        return Pet.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class VaccinationRecordViewSet(viewsets.ModelViewSet):
    serializer_class = VaccinationRecordSerializer

    def get_queryset(self):
        return VaccinationRecord.objects.filter(pet__owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(pet_id=self.request.data.get("pet"))