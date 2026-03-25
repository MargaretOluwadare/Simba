from rest_framework import viewsets
from .models import UserPlan
from .serializers import UserPlanSerializer


class UserPlanViewSet(viewsets.ModelViewSet):
    serializer_class = UserPlanSerializer

    def get_queryset(self):
        return UserPlan.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            plan_id=self.request.data.get("plan"),
        )