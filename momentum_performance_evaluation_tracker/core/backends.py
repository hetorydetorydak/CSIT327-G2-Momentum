from django.contrib.auth.backends import BaseBackend
from .models import UserAccount

class CustomUserBackend(BaseBackend): # Custom authentication backend
    def authenticate(self, request, username=None, password=None, **kwargs): # Authenticate user
        try:
            user = UserAccount.objects.get(username=username)
            if user.check_password(password):
                return user
        except UserAccount.DoesNotExist:
            return None

    def get_user(self, user_id): # Retrieve user by ID
        try:
            return UserAccount.objects.get(pk=user_id)
        except UserAccount.DoesNotExist:
            return None


