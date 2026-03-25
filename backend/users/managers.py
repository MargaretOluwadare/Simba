from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **args):
        if not email:
            raise ValueError('Email is required')
        
        email = self.normalize_email(email.lower())
        user = self.model(email=email, username=email, **args)
        user.set_password(password)
        user.save(using=self._db)
        
        return user
    
    def create_superuser(self, email, password=None, **args):
        if password is None:
            raise ValueError('Superusers must have a password')
        
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        
        return user