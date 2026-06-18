"""
tenancy/admin.py — Django admin registration for tenancy models.

This gives restaurant/branch/role/user management for free via /admin,
useful for super-admin operations and debugging during development.
For production, restaurant owners use the Admin app (Next.js) via the API,
not this Django admin.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from tenancy.models import Branch, Restaurant, Role, User


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "subscription_plan", "is_active", "created_at")
    list_filter = ("subscription_plan", "is_active")
    search_fields = ("name", "slug", "legal_name")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name", "restaurant", "city", "is_active", "created_at")
    list_filter = ("is_active", "city")
    search_fields = ("name", "restaurant__name")
    autocomplete_fields = ("restaurant",)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "restaurant")
    list_filter = ("code",)
    search_fields = ("name",)
    autocomplete_fields = ("restaurant",)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Extends Django's built-in UserAdmin but swaps out username-based fields
    for our email/restaurant/branch/role based model.
    """
    model = User
    list_display = ("email", "full_name", "restaurant", "branch", "role", "is_active", "is_staff")
    list_filter = ("is_active", "is_staff", "role__code", "restaurant")
    search_fields = ("email", "full_name")
    ordering = ("restaurant", "email")
    autocomplete_fields = ("restaurant", "branch", "role")

    # BaseUserAdmin defines fieldsets/add_fieldsets around `username` — override fully.
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("full_name", "phone")}),
        ("Tenant", {"fields": ("restaurant", "branch", "role")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "last_login_at")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "restaurant", "role", "full_name"),
        }),
    )
    readonly_fields = ("last_login", "last_login_at")