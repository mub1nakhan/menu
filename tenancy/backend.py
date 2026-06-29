"""
tenancy/backend.py

Custom Django authentication backend.
Looks up users by (restaurant_id, email) together — not just email globally.
This is required because the same email can exist in multiple restaurants.

Registered in settings.py:
    AUTHENTICATION_BACKENDS = ["tenancy.backend.TenantAuthBackend"]
"""
from django.contrib.auth.backends import ModelBackend

from tenancy.models import User


class TenantAuthBackend(ModelBackend):
    """
    Authenticates by (restaurant_id, email, password).
    
    The `authenticate()` call in TenantTokenObtainPairSerializer passes
    `restaurant_id` as a keyword argument — this backend picks it up.
    
    Falls back to None (not an exception) when credentials don't match,
    so Django can try the next backend in the list if any.
    """

    def authenticate(self, request, email=None, password=None, restaurant_id=None, **kwargs):
        if not email or not password or not restaurant_id:
            return None

        try:
            user = User.objects.select_related("role", "restaurant", "branch").get(
                email=email,
                restaurant_id=restaurant_id,
            )
        except User.DoesNotExist:
            # Run the default password hasher to avoid timing attacks
            User().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None

    def get_user(self, user_id):
        try:
            return User.objects.select_related("role", "restaurant", "branch").get(pk=user_id)
        except User.DoesNotExist:
            return None