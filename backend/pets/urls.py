from rest_framework.routers import DefaultRouter
from .views import PetViewSet, VaccinationRecordViewSet

router = DefaultRouter()
router.register(r"pets", PetViewSet, basename="pets")
router.register(r"vaccinations", VaccinationRecordViewSet, basename="vaccinations")

urlpatterns = router.urls