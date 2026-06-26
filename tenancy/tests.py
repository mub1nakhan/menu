"""
tenancy/tests.py — Auth va tenant scoping testlari.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from tenancy.models import Restaurant, Branch, Role, User, UserRole


def make_restaurant(slug="r1", name="Test R1"):
    r = Restaurant.objects.create(name=name, slug=slug)
    b = Branch.objects.create(restaurant=r, name="Main", city="Toshkent")
    role = Role.objects.create(restaurant=r, code=UserRole.OWNER, name="Owner", permissions=["*"])
    user = User.objects.create_user(
        email="admin@r1.com", restaurant=r, role=role,
        password="Pass1234!", full_name="Admin"
    )
    return r, b, role, user


class LoginTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.r, self.b, self.role, self.user = make_restaurant()

    def test_login_success(self):
        resp = self.client.post("/api/v1/auth/login/", {
            "restaurant_slug": self.r.slug,
            "email": "admin@r1.com",
            "password": "Pass1234!",
        }, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data)
        self.assertIn("refresh", resp.data)

    def test_login_wrong_password(self):
        resp = self.client.post("/api/v1/auth/login/", {
            "restaurant_slug": self.r.slug,
            "email": "admin@r1.com",
            "password": "WrongPass!",
        }, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_wrong_slug(self):
        resp = self.client.post("/api/v1/auth/login/", {
            "restaurant_slug": "nonexistent",
            "email": "admin@r1.com",
            "password": "Pass1234!",
        }, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_me_returns_current_user(self):
        login = self.client.post("/api/v1/auth/login/", {
            "restaurant_slug": self.r.slug,
            "email": "admin@r1.com",
            "password": "Pass1234!",
        }, format="json")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        resp = self.client.get("/api/v1/auth/me/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["email"], "admin@r1.com")

    def test_unauthenticated_me(self):
        resp = self.client.get("/api/v1/auth/me/")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class TenantScopingTests(TestCase):
    """Restaurant A foydalanuvchisi Restaurant B ma'lumotlarini ko'ra olmasligi kerak."""

    def setUp(self):
        self.client = APIClient()
        self.r1, self.b1, self.role1, self.user1 = make_restaurant("r1", "Restaurant 1")
        self.r2, self.b2, self.role2, self.user2 = make_restaurant("r2", "Restaurant 2")

    def _login(self, slug, email, password="Pass1234!"):
        resp = self.client.post("/api/v1/auth/login/", {
            "restaurant_slug": slug, "email": email, "password": password,
        }, format="json")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")

    def test_branch_scoping(self):
        # r1 user faqat o'z branch'ini ko'radi
        self._login("r1", "admin@r1.com")
        resp = self.client.get("/api/v1/branches/")
        self.assertEqual(resp.status_code, 200)
        ids = [b["id"] for b in resp.data["results"]]
        self.assertIn(str(self.b1.id), ids)
        self.assertNotIn(str(self.b2.id), ids)


class BranchCRUDTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.r, self.b, self.role, self.user = make_restaurant()
        login = self.client.post("/api/v1/auth/login/", {
            "restaurant_slug": self.r.slug,
            "email": "admin@r1.com",
            "password": "Pass1234!",
        }, format="json")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    def test_list_branches(self):
        resp = self.client.get("/api/v1/branches/")
        self.assertEqual(resp.status_code, 200)

    def test_create_branch(self):
        resp = self.client.post("/api/v1/branches/", {
            "name": "Chilonzor filiali",
            "city": "Toshkent",
            "currency": "UZS",
        }, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["name"], "Chilonzor filiali")

    def test_delete_branch(self):
        resp = self.client.delete(f"/api/v1/branches/{self.b.id}/")
        self.assertEqual(resp.status_code, 204)