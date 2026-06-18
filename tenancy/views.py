"""
tenancy/views.py — auth endpoints (login, PIN login, refresh, me) and
branch CRUD demonstrating the tenant-scoped queryset pattern every other
app's viewsets will follow.
"""
from rest_framework import generics, permissions, serializers, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from tenancy.models import Branch, UserRole
from tenancy.permissions import IsOwnerOrSuperAdmin
from tenancy.serializers import (
    CurrentUserSerializer,
    PinTokenObtainPairSerializer,
    TenantTokenObtainPairSerializer,
)


class TenantLoginView(TokenObtainPairView):
    """POST /api/v1/auth/login/  — email+password login, scoped by restaurant_slug."""
    serializer_class = TenantTokenObtainPairSerializer


class PinLoginView(APIView):
    """POST /api/v1/auth/login/pin/  — PIN login for waiter/chef shared devices."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PinTokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


# Token refresh reuses SimpleJWT's built-in view as-is — it doesn't need our
# custom claims logic since it just re-signs from the existing refresh token.
TenantTokenRefreshView = TokenRefreshView


class MeView(generics.RetrieveAPIView):
    """GET /api/v1/auth/me/ — current authenticated user's profile + tenant context."""
    serializer_class = CurrentUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = [
            "id", "name", "address", "city", "timezone", "currency",
            "phone", "latitude", "longitude", "is_active", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class BranchViewSet(viewsets.ModelViewSet):
    """
    /api/v1/branches/  — full CRUD, tenant-scoped.

    This is the reference pattern for every other app's viewsets:
      1. get_queryset() filters by request.user.restaurant_id — never trust
         a client-supplied restaurant_id for read scoping.
      2. perform_create() forces restaurant onto the new object.
      3. permission_classes restrict *which roles* may call write actions.
    """
    serializer_class = BranchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsOwnerOrSuperAdmin()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        return Branch.objects.filter(restaurant_id=self.request.user.restaurant_id).order_by("name")

    def perform_create(self, serializer):
        serializer.save(restaurant_id=self.request.user.restaurant_id)

    def perform_update(self, serializer):
        user = self.request.user
        instance: Branch = self.get_object()
        # Branch managers may only edit their own assigned branch
        if user.role.code == UserRole.BRANCH_MANAGER and user.branch_id != instance.id:
            raise PermissionDenied("Not your branch")
        serializer.save()