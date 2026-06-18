"""
tenancy/permissions.py

RBAC permission classes for DRF views/viewsets.

Tenant scoping is NOT done here — that happens in each app's queryset
(filter by request.user.restaurant_id). This module only answers
"is this role allowed to call this endpoint at all".

request.user is the authenticated User instance (SimpleJWT resolves the
JWT's user_id claim back to a real User via the DB on every request, so
request.user.role is always fresh — unlike the role *string* embedded in
the token, which is a snapshot from login time and only used for quick
client-side UI decisions, never for server-side authorization).
"""
from rest_framework.permissions import BasePermission

from tenancy.models import UserRole


class HasAnyRole(BasePermission):
    """
    Usage:
        permission_classes = [HasAnyRole.for_roles(UserRole.OWNER, UserRole.BRANCH_MANAGER)]
    """
    allowed_roles: tuple[str, ...] = ()

    def has_permission(self, request, view) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.role.code in self.allowed_roles

    @classmethod
    def for_roles(cls, *roles: str):
        return type("HasAnyRoleScoped", (cls,), {"allowed_roles": tuple(roles)})


class IsOwnerOrSuperAdmin(HasAnyRole):
    allowed_roles = (UserRole.OWNER, UserRole.SUPER_ADMIN)


class IsBranchStaffOrAbove(HasAnyRole):
    """Owner, branch manager, or super_admin — i.e. anyone who manages a branch's operations."""
    allowed_roles = (UserRole.OWNER, UserRole.BRANCH_MANAGER, UserRole.SUPER_ADMIN)


class IsKitchenOrServiceStaff(HasAnyRole):
    """Waiter, chef, cashier — front-of-house and kitchen operational roles."""
    allowed_roles = (UserRole.WAITER, UserRole.CHEF, UserRole.CASHIER)


class SameBranchOnly(BasePermission):
    """
    Object-level check: branch-scoped staff (branch_id is not None) can only
    touch objects belonging to their own branch. Owners/super_admins
    (branch_id is None) pass through — restaurant-level scoping still
    applies via the queryset filter.

    Usage in a viewset:
        permission_classes = [IsAuthenticated, SameBranchOnly]
        # the object must have a `.branch_id` attribute
    """

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        if user.branch_id is None:
            return True
        return getattr(obj, "branch_id", None) == user.branch_id