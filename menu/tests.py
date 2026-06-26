"""
menu/tests.py — MenuCategory va Product CRUD testlari.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from tenancy.models import Restaurant, Branch, Role, User, UserRole
from menu.models import MenuCategory, Product


def setup_restaurant():
    r = Restaurant.objects.create(name="Menu Test R", slug="menu-test-r")
    b = Branch.objects.create(restaurant=r, name="Main", city="Toshkent")
    role = Role.objects.create(restaurant=r, code=UserRole.OWNER, name="Owner", permissions=["*"])
    user = User.objects.create_user(
        email="owner@menu.com", restaurant=r, role=role,
        password="Pass1234!", full_name="Owner"
    )
    return r, b, role, user


class MenuCategoryTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.r, self.b, self.role, self.user = setup_restaurant()
        login = self.client.post("/api/v1/auth/login/", {
            "restaurant_slug": self.r.slug,
            "email": "owner@menu.com",
            "password": "Pass1234!",
        }, format="json")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    def test_create_category(self):
        resp = self.client.post("/api/v1/categories/", {
            "name_i18n": {"uz": "Salatlar", "ru": "Салаты", "en": "Salads"},
            "sort_order": 1,
            "is_active": True,
        }, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["name_i18n"]["uz"], "Salatlar")

    def test_list_categories(self):
        MenuCategory.objects.create(
            restaurant=self.r,
            name_i18n={"uz": "Birinchi taomlar", "en": "Starters"}
        )
        resp = self.client.get("/api/v1/categories/")
        self.assertEqual(resp.status_code, 200)
        self.assertGreater(resp.data["count"], 0)

    def test_category_invalid_name_i18n(self):
        resp = self.client.post("/api/v1/categories/", {
            "name_i18n": "not a dict",
        }, format="json")
        self.assertEqual(resp.status_code, 400)


class ProductTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.r, self.b, self.role, self.user = setup_restaurant()
        self.cat = MenuCategory.objects.create(
            restaurant=self.r,
            name_i18n={"uz": "Burgerlar", "en": "Burgers"}
        )
        login = self.client.post("/api/v1/auth/login/", {
            "restaurant_slug": self.r.slug,
            "email": "owner@menu.com",
            "password": "Pass1234!",
        }, format="json")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    def test_create_product(self):
        resp = self.client.post("/api/v1/products/", {
            "category": str(self.cat.id),
            "name_i18n": {"uz": "Classic Burger", "en": "Classic Burger"},
            "price": "45000.00",
            "is_available": True,
        }, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["name_i18n"]["uz"], "Classic Burger")

    def test_toggle_availability(self):
        resp = self.client.post("/api/v1/products/", {
            "category": str(self.cat.id),
            "name_i18n": {"uz": "Burger", "en": "Burger"},
            "price": "40000.00",
        }, format="json")
        product_id = resp.data["id"]
        resp2 = self.client.patch(f"/api/v1/products/{product_id}/toggle-availability/")
        self.assertEqual(resp2.status_code, 200)
        self.assertFalse(resp2.data["is_available"])

    def test_public_menu(self):
        Product.objects.create(
            restaurant=self.r, branch=self.b, category=self.cat,
            name_i18n={"uz": "Lavash", "en": "Lavash"},
            price="25000", is_available=True
        )
        # JWT yo'q
        anon_client = APIClient()
        resp = anon_client.get(f"/api/v1/public/menu/{self.b.id}/?lang=uz")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.data, list)