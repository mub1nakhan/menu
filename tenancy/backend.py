"""
tenancy/backends.py

Custom Django auth backend.

Why this exists: our User.email is unique per-restaurant, not globally
(the UniqueConstraint is on (restaurant, email)). Django's default
ModelBackend authenticates by USERNAME_FIELD alone and would call
User.objects.get(email=...) — which can raise MultipleObjectsReturned once
two restaurants have staff sharing an email address.

This backend requires the caller to pass restaurant_id explicitly (our
login serializer does this — see tenancy/serializers.py), so the lookup is
always scoped correctly: (restaurant_id, email) together identify exactly
one user.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

User = get_user_model()


class TenantEmailBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, restaurant_id=None, **kwargs):
        if not email or not password or not restaurant_id:
            return None

        try:
            user = User.objects.select_related("role", "restaurant").get(
                restaurant_id=restaurant_id, email=email, is_active=True
            )
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.select_related("role", "restaurant").get(pk=user_id)
        except User.DoesNotExist:
            return None