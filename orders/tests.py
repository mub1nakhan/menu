"""
orders/tests.py — Table va Order CRUD + status transition testlari.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from tenancy.models import Restaurant, Branch, Role, User, UserRole
from menu.models import MenuCategory, Product
from orders.models import Order, OrderStatus, Table


def setup_full(slug="orders-r"):
    r = Restaurant.objects.create(name="Orders R", slug=slug)
    b = Branch.objects.create(restaurant=r, name="Main", city="Toshkent")
    owner_role = Role.objects.create(restaurant=r, code=UserRole.OWNER, name="Owner", permissions=["*"])
    owner = User.objects.create_user(
        email=f"owner@{slug}.com", restaurant=r, role=owner_role,
        branch=b, password="Pass1234!", full_name="Owner"
    )
    cat = MenuCategory.objects.create(restaurant=r, name_i18n={"uz": "Asosiy", "en": "Main"})
    product = Product.objects.create(
        restaurant=r, branch=b, category=cat,
        name_i18n={"uz": "Osh", "en": "Plov"},
        price="35000", is_available=True
    )
    return r, b, owner_role, owner, cat, product


class TableTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.r, self.b, self.role, self.user, self.cat, self.product = setup_full()
        login = self.client.post("/api/v1/auth/login/", {
            "restaurant_slug": self.r.slug,
            "email": f"owner@{self.r.slug}.com",
            "password": "Pass1234!",
        }, format="json")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    def test_create_table(self):
        resp = self.client.post("/api/v1/tables/", {
            "branch": str(self.b.id),
            "label": "Stol 1",
            "capacity": 4,
        }, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertIn("qr_code_token", resp.data)

    def test_list_tables(self):
        resp = self.client.get("/api/v1/tables/")
        self.assertEqual(resp.status_code, 200)


class OrderTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.r, self.b, self.role, self.user, self.cat, self.product = setup_full("order-r2")
        login = self.client.post("/api/v1/auth/login/", {
            "restaurant_slug": self.r.slug,
            "email": f"owner@{self.r.slug}.com",
            "password": "Pass1234!",
        }, format="json")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    def _create_order(self):
        return self.client.post("/api/v1/orders/", {
            "items": [{"product": str(self.product.id), "quantity": 2}],
            "notes": "Tez tayyorlab bering",
        }, format="json")

    def test_create_order(self):
        resp = self._create_order()
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["status"], OrderStatus.PENDING)
        self.assertEqual(float(resp.data["total_amount"]), 70000.0)

    def test_order_status_transition(self):
        order_resp = self._create_order()
        order_id = order_resp.data["id"]

        # PENDING → CONFIRMED
        resp = self.client.patch(f"/api/v1/orders/{order_id}/status/", {
            "status": "confirmed"
        }, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["status"], "confirmed")

    def test_invalid_status_transition(self):
        order_resp = self._create_order()
        order_id = order_resp.data["id"]

        # PENDING → COMPLETED (noto'g'ri)
        resp = self.client.patch(f"/api/v1/orders/{order_id}/status/", {
            "status": "completed"
        }, format="json")
        self.assertEqual(resp.status_code, 400)

    def test_order_tenant_scoping(self):
        # Boshqa restoran foydalanuvchisi bu orderni ko'ra olmaydi
        r2, b2, role2, user2, _, _ = setup_full("other-r")
        login2 = self.client.post("/api/v1/auth/login/", {
            "restaurant_slug": r2.slug,
            "email": f"owner@{r2.slug}.com",
            "password": "Pass1234!",
        }, format="json")
        other_client = APIClient()
        other_client.credentials(HTTP_AUTHORIZATION=f"Bearer {login2.data['access']}")

        self._create_order()
        resp = other_client.get("/api/v1/orders/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 0)