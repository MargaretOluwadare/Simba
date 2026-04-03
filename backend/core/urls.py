from rest_framework.routers import DefaultRouter
from .views import UserPlanViewSet

router = DefaultRouter()
router.register(r"user-plans", UserPlanViewSet, basename="user-plans")

urlpatterns = router.urls