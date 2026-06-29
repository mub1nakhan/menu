"""
tenancy/models.py

Core multi-tenant models: Restaurant, Branch, Role, User.

Every other app's models (menu, inventory, orders, payments) will have a
ForeignKey to Restaurant (and usually Branch too) — this app is the
foundation everything else builds on.
"""
import uuid

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base: adds created_at / updated_at to any model that inherits it."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SubscriptionPlan(models.TextChoices):
    TRIAL = "trial", "Trial"
    BASIC = "basic", "Basic"
    PRO = "pro", "Pro"
    ENTERPRISE = "enterprise", "Enterprise"


class UserRole(models.TextChoices):
    SUPER_ADMIN = "super_admin", "Super Admin"
    OWNER = "owner", "Owner"
    BRANCH_MANAGER = "branch_manager", "Branch Manager"
    WAITER = "waiter", "Waiter"
    CHEF = "chef", "Chef"
    CASHIER = "cashier", "Cashier"


class Restaurant(TimeStampedModel):
    """A tenant. Everything in the system ultimately belongs to one Restaurant."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)
    legal_name = models.CharField(max_length=200, blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True)
    subscription_plan = models.CharField(
        max_length=20, choices=SubscriptionPlan.choices, default=SubscriptionPlan.TRIAL
    )
    subscription_expires_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    settings = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "restaurants"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Branch(TimeStampedModel):
    """A physical location belonging to a Restaurant."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name="branches"
    )
    name = models.CharField(max_length=150)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    timezone = models.CharField(max_length=50, default="Asia/Tashkent")
    currency = models.CharField(max_length=10, default="UZS")
    phone = models.CharField(max_length=30, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "branches"
        constraints = [
            models.UniqueConstraint(fields=["restaurant", "name"], name="uq_branch_restaurant_name")
        ]
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.restaurant.name})"


class Role(models.Model):
    """
    A role within a restaurant (or a global system role when restaurant is NULL).
    `permissions` holds a JSON list of permission strings consumed by our
    custom DRF permission classes (built in tenancy/permissions.py).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name="roles", blank=True, null=True
    )
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20, choices=UserRole.choices)
    permissions = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "roles"
        constraints = [
            # Per-restaurant roles: one row per (restaurant, code) when restaurant is set.
            models.UniqueConstraint(
                fields=["restaurant", "code"],
                condition=models.Q(restaurant__isnull=False),
                name="uq_role_restaurant_code",
            ),
            # Global/system roles (restaurant IS NULL, e.g. super_admin): only one per code.
            # Without this, Postgres treats every NULL as distinct and silently allows
            # duplicate global roles — caught during testing, see tenancy/tests.py.
            models.UniqueConstraint(
                fields=["code"],
                condition=models.Q(restaurant__isnull=True),
                name="uq_role_global_code",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class UserManager(BaseUserManager):
    """
    Custom manager so users are created by email, not username.
    Every user must belong to a restaurant and have a role — both are
    required even for createsuperuser, so super_admin accounts still carry
    tenant context (use a dedicated "platform" restaurant for those).
    """

    def create_user(self, email, restaurant, role, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        if not restaurant:
            raise ValueError("Users must belong to a restaurant")
        if not role:
            raise ValueError("Users must have a role")

        email = self.normalize_email(email)
        user = self.model(email=email, restaurant=restaurant, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, restaurant, role, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, restaurant, role, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """
    Custom user model, authenticated by email instead of username.

    is_staff / is_superuser come from PermissionsMixin and control access to
    the Django admin only — they are NOT the same as our app-level `role`
    field, which drives RBAC inside the API (see tenancy/permissions.py).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name="users"
    )
    branch = models.ForeignKey(
        Branch, on_delete=models.SET_NULL, related_name="staff", blank=True, null=True,
        help_text="NULL for restaurant-level staff (owner/admin) who aren't tied to one branch.",
    )
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="users")

    
    
    username = None

    # unique per-restaurant enforced by UniqueConstraint below, not globally
    email = models.EmailField()

    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=30, blank=True, null=True)
    pin_code_hash = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Hashed short PIN for waiter/chef quick login on shared devices.",
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    last_login_at = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]  # restaurant/role are required positionally by the manager

    objects = UserManager()

    class Meta:
        db_table = "users"
        constraints = [
            models.UniqueConstraint(fields=["restaurant", "email"], name="uq_user_restaurant_email")
        ]

    # NOTE on Django's auth.E003 check:
    # Django's system check wants USERNAME_FIELD to be globally unique because
    # the default ModelBackend looks users up by that field alone. Our email
    # is only unique *per restaurant* (the same email can belong to a waiter
    # at Restaurant A and an owner at Restaurant B), so this check is silenced
    # globally in settings.py (SILENCED_SYSTEM_CHECKS = ["auth.E003"]) and we
    # provide our own authentication backend (tenancy/backends.py) that looks
    # users up by (restaurant, email) together. Never rely on the default
    # ModelBackend's email-only lookup in this project.

    def __str__(self) -> str:
        return f"{self.full_name} <{self.email}>"