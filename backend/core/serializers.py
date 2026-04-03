from rest_framework import serializers
from .models import UserPlan, AdminPlan


class AdminPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminPlan
        fields = "__all__"
        read_only_fields = ("date_created", "date_updated")


class UserPlanSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.id")
    plan = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = UserPlan
        fields = "__all__"
        read_only_fields = (
            "user",
            "plan",
            "date_created",
            "date_updated",
        )