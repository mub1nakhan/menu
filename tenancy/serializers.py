"""
tenancy/serializers.py

Custom JWT login serializer: instead of SimpleJWT's default username+password
pair, we require restaurant_slug + email + password, because our users are
only unique per-restaurant. On success, we embed restaurant_id, branch_id,
and role into the token claims — this is what every other app's permission
classes and viewsets read to scope queries, with zero extra DB lookups per
request.
"""
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from tenancy.models import Restaurant, User


class TenantTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    POST body: { "restaurant_slug": "...", "email": "...", "password": "..." }
    """
    username_field = "email"  # required by the parent class's field setup, unused directly

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Replace SimpleJWT's default fields with our own
        self.fields.pop("email", None)
        self.fields["restaurant_slug"] = serializers.SlugField()
        self.fields["email"] = serializers.EmailField()
        self.fields["password"] = serializers.CharField(write_only=True)

    def validate(self, attrs):
        restaurant_slug = attrs["restaurant_slug"]
        email = attrs["email"]
        password = attrs["password"]

        try:
            restaurant = Restaurant.objects.get(slug=restaurant_slug, is_active=True)
        except Restaurant.DoesNotExist:
            raise serializers.ValidationError({"restaurant_slug": _("Restaurant not found")})

        user = authenticate(
            request=self.context.get("request"),
            email=email,
            password=password,
            restaurant_id=restaurant.id,
        )
        if user is None:
            # Deliberately generic — don't reveal whether the email exists
            raise serializers.ValidationError(_("Invalid email or password"))

        refresh = self.get_token(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    @classmethod
    def get_token(cls, user: User) -> RefreshToken:
        token = super().get_token(user)
        # Custom claims read by tenancy/permissions.py and every other app's
        # viewsets via request.auth — this is the backbone of multi-tenancy.
        token["restaurant_id"] = str(user.restaurant_id)
        token["branch_id"] = str(user.branch_id) if user.branch_id else None
        token["role"] = user.role.code
        return token


class PinTokenObtainPairSerializer(serializers.Serializer):
    """
    PIN login for waiter/chef shared devices.
    POST body: { "restaurant_slug": "...", "branch_id": "...", "pin_code": "..." }
    """
    restaurant_slug = serializers.SlugField()
    branch_id = serializers.UUIDField()
    pin_code = serializers.CharField(min_length=4, max_length=8, write_only=True)

    def validate(self, attrs):
        from django.contrib.auth.hashers import check_password

        try:
            restaurant = Restaurant.objects.get(slug=attrs["restaurant_slug"], is_active=True)
        except Restaurant.DoesNotExist:
            raise serializers.ValidationError({"restaurant_slug": _("Restaurant not found")})

        candidates = User.objects.filter(
            restaurant=restaurant,
            branch_id=attrs["branch_id"],
            is_active=True,
            pin_code_hash__isnull=False,
        )
        matched_user = next(
            (u for u in candidates if check_password(attrs["pin_code"], u.pin_code_hash)), None
        )
        if matched_user is None:
            raise serializers.ValidationError(_("Invalid PIN"))

        refresh = TenantTokenObtainPairSerializer.get_token(matched_user)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}


class CurrentUserSerializer(serializers.ModelSerializer):
    role_code = serializers.CharField(source="role.code", read_only=True)
    restaurant_name = serializers.CharField(source="restaurant.name", read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "full_name", "restaurant_id", "branch_id", "role_code", "restaurant_name"]