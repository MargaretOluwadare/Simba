from django.core.management.base import BaseCommand
from core.models import AdminPlan


class Command(BaseCommand):
    help = "Seed default plans"

    def handle(self, *args, **kwargs):
         # run only when user table is empty
        plan_count = AdminPlan.objects.filter(is_enabled=True).count()
        if plan_count > 0:
            self.stdout.write(self.style.NOTICE('Admin table already populated'))
            return
        
        plans = [
            {
                "name": "Basic Vet Access",
                "amount": 5000,
                "plan_type": "subscription",
                "model": "consultation",
                "is_enabled": True,
            },
            {
                "name": "Premium Vet Access",
                "amount": 15000,
                "plan_type": "subscription",
                "model": "consultation",
                "is_enabled": True,
            },
            {
                "name": "One-time Emergency Consult",
                "amount": 3000,
                "plan_type": "one_time",
                "model": "consultation",
                "is_enabled": True,
            },
        ]

        created_count = 0

        for plan in plans:
            obj, created = AdminPlan.objects.get_or_create(
                name=plan["name"],
                defaults=plan,
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Successfully seeded {created_count} plans")
        )
