"""
inventory/tests.py — Ingredient, Recipe, Stock adjustment testlari.
"""
from django.test import TestCase
from rest_framework.test import APIClient

from tenancy.models import Restaurant, Branch, Role, User, UserRole
from menu.models import MenuCategory, Product
from inventory.models import Ingredient, MeasurementUnit


def setup_inv(slug="inv-r"):
    r = Restaurant.objects.create(name="Inv R", slug=slug)
    b = Branch.objects.create(restaurant=r, name="Main", city="Toshkent")
    role = Role.objects.create(restaurant=r, code=UserRole.OWNER, name="Owner", permissions=["*"])
    user = User.objects.create_user(
        email=f"owner@{slug}.com", restaurant=r, role=role,
        branch=b, password="Pass1234!", full_name="Owner"
    )
    return r, b, role, user


class IngredientTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.r, self.b, self.role, self.user = setup_inv()
        login = self.client.post("/api/v1/auth/login/", {
            "restaurant_slug": self.r.slug,
            "email": f"owner@{self.r.slug}.com",
            "password": "Pass1234!",
        }, format="json")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    def test_create_ingredient(self):
        resp = self.client.post("/api/v1/inventory/ingredients/", {
            "name": "Un",
            "unit": "kg",
            "unit_cost": "5000.00",
            "low_stock_threshold": "2.000",
        }, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["name"], "Un")

    def test_stock_adjustment(self):
        ing = Ingredient.objects.create(
            restaurant=self.r, branch=self.b,
            name="Tuz", unit=MeasurementUnit.KG, unit_cost=1000
        )
        resp = self.client.post("/api/v1/inventory/stock/adjust/", {
            "ingredient": str(ing.id),
            "movement_type": "stock_in",
            "quantity": "10.000",
            "note": "Yangi keldi",
        }, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(float(resp.data["quantity_on_hand"]), 10.0)

    def test_low_stock_endpoint(self):
        ing = Ingredient.objects.create(
            restaurant=self.r, branch=self.b,
            name="Yog", unit=MeasurementUnit.L,
            unit_cost=8000, low_stock_threshold=5
        )
        resp = self.client.get("/api/v1/inventory/stock/low-stock/")
        self.assertEqual(resp.status_code, 200)