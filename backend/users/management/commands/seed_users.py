from django.core.management.base import BaseCommand
from users.models import User, Profile
from decouple import config

class Command(BaseCommand):
    help = "Seeds the DB with 5 users. Run only on local"
    
    def handle(self, **args):
        USER_PASSWORD = config('USER_PASSWORD')
        
        # run only when user table is empty
        user_count = User.objects.filter(is_superuser=False).count()
        if user_count > 0:
            self.stdout.write(self.style.NOTICE('User table already populated'))
            return
        
        for i in range(5):
            user = User.objects.create_user(email=f'simbauser{i}@gmail.com', password=USER_PASSWORD)
            Profile.objects.create(user=user)
            
        self.stdout.write(self.style.SUCCESS("Users successfully seeded"))