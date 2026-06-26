"""
Management command: seed initial demo data so you can log in and explore
the API right after migrating, without manually creating UUIDs by hand.

Usage:
    python manage.py seed_demo_data
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from tenancy.models import Branch, Restaurant, Role, User, UserRole


class Command(BaseCommand):
    help = "Creates a demo restaurant, branch, roles, and an owner user for local testing."

    def add_arguments(self, parser):
        parser.add_argument("--email", default="owner@demo.uz")
        parser.add_argument("--password", default="DemoPass123")

    @transaction.atomic
    def handle(self, *args, **options):
        email = options["email"]
        password = options["password"]

        restaurant, created = Restaurant.objects.get_or_create(
            slug="demo-restaurant", defaults={"name": "Demo Restaurant"}
        )
        self.stdout.write(self.style.SUCCESS(f"Restaurant: {restaurant.name} ({'created' if created else 'exists'})"))

        branch, created = Branch.objects.get_or_create(
            restaurant=restaurant, name="Main Branch", defaults={"city": "Tashkent"}
        )
        self.stdout.write(self.style.SUCCESS(f"Branch: {branch.name} ({'created' if created else 'exists'})"))

        owner_role, created = Role.objects.get_or_create(
            restaurant=restaurant, code=UserRole.OWNER, defaults={"name": "Owner", "permissions": ["*"]}
        )
        waiter_role, _ = Role.objects.get_or_create(
            restaurant=restaurant, code=UserRole.WAITER, defaults={"name": "Waiter", "permissions": ["orders:create"]}
        )
        chef_role, _ = Role.objects.get_or_create(
            restaurant=restaurant, code=UserRole.CHEF, defaults={"name": "Chef", "permissions": ["orders:update_status"]}
        )
        self.stdout.write(self.style.SUCCESS("Roles: owner, waiter, chef ready"))

        if User.objects.filter(restaurant=restaurant, email=email).exists():
            self.stdout.write(self.style.WARNING(f"User {email} already exists, skipping creation."))
        else:
            User.objects.create_user(
                email=email,
                restaurant=restaurant,
                role=owner_role,
                password=password,
                full_name="Demo Owner",
            )
            self.stdout.write(self.style.SUCCESS(f"Owner user created: {email} / {password}"))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Seed complete. Login payload for POST /api/v1/auth/login/:"))
        self.stdout.write(f'  {{"restaurant_slug": "demo-restaurant", "email": "{email}", "password": "{password}"}}')