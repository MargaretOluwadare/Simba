from django.core.management.base import BaseCommand, CommandError
from users.models import User, Profile
from decouple import config


class Command(BaseCommand):
    help = "Seed superuser account"
    
    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help="Superuser email")
        parser.add_argument('--password', type=str, help="Superuser password")

    def handle(self, email=None, password=None, **args):
        superuser_email = email or config("SUPERUSER_EMAIL")
        superuser_password = password or config("SUPERUSER_PASSWORD")

        if not superuser_email or not superuser_password:
            raise CommandError("Super user email/password missing. Check .ENV")

        existing_superuser = User.objects.filter(email=superuser_email).exists()
        if existing_superuser:
            self.stdout.write(self.style.NOTICE("Superuser already exists"))
            return

        User.objects.create_superuser(
            email=superuser_email, password=superuser_password
        )

        self.stdout.write(self.style.SUCCESS("Superuser successfully created"))
