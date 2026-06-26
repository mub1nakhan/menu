"""
payments/tests.py — Payment yaratish va refund testlari.
"""
from django.test import TestCase
from rest_framework.test import APIClient

from tenancy.models import Restaurant, Branch, Role, User, UserRole
from menu.models import MenuCategory, Product
from orders.models import Order, OrderItem, OrderStatus, Table


def setup_pay(slug="pay-r"):
    r = Restaurant.objects.create(name="Pay R", slug=slug)
    b = Branch.objects.create(restaurant=r, name="Main", city="Toshkent")
    role = Role.objects.create(restaurant=r, code=UserRole.OWNER, name="Owner", permissions=["*"])
    user = User.objects.create_user(
        email=f"owner@{slug}.com", restaurant=r, role=role,
        branch=b, password="Pass1234!", full_name="Owner"
    )
    cat = MenuCategory.objects.create(restaurant=r, name_i18n={"uz": "Test", "en": "Test"})
    product = Product.objects.create(
        restaurant=r, branch=b, category=cat,
        name_i18n={"uz": "Osh", "en": "Plov"},
        price="50000", is_available=True
    )
    return r, b, role, user, product


class PaymentTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.r, self.b, self.role, self.user, self.product = setup_pay()
        login = self.client.post("/api/v1/auth/login/", {
            "restaurant_slug": self.r.slug,
            "email": f"owner@{self.r.slug}.com",
            "password": "Pass1234!",
        }, format="json")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

        # Create order
        order_resp = self.client.post("/api/v1/orders/", {
            "items": [{"product": str(self.product.id), "quantity": 1}],
        }, format="json")
        self.order_id = order_resp.data["id"]
        self.order_total = order_resp.data["total_amount"]

    def test_create_payment(self):
        resp = self.client.post("/api/v1/payments/", {
            "order": self.order_id,
            "method": "cash",
            "amount": self.order_total,
        }, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["status"], "paid")

    def test_payment_completes_order(self):
        self.client.post("/api/v1/payments/", {
            "order": self.order_id,
            "method": "card",
            "amount": self.order_total,
        }, format="json")
        order = Order.objects.get(id=self.order_id)
        self.assertEqual(order.status, OrderStatus.COMPLETED)

    def test_refund(self):
        pay_resp = self.client.post("/api/v1/payments/", {
            "order": self.order_id,
            "method": "cash",
            "amount": self.order_total,
        }, format="json")
        pay_id = pay_resp.data["id"]
        resp = self.client.post(f"/api/v1/payments/{pay_id}/refund/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["status"], "refunded")