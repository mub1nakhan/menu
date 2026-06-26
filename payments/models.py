import uuid
from django.db import models
from tenancy.models import Branch, Restaurant, TimeStampedModel, User
from orders.models import Order


class PaymentMethod(models.TextChoices):
    CASH = "cash", "Cash"
    CARD = "card", "Card"
    ONLINE = "online", "Online"
    WALLET = "wallet", "Wallet"


class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    AUTHORIZED = "authorized", "Authorized"
    PAID = "paid", "Paid"
    FAILED = "failed", "Failed"
    REFUNDED = "refunded", "Refunded"
    PARTIALLY_REFUNDED = "partially_refunded", "Partially Refunded"


class Payment(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    status = models.CharField(max_length=25, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=10, default="UZS")
    provider = models.CharField(max_length=50, blank=True, null=True)
    provider_transaction_id = models.CharField(max_length=150, blank=True, null=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "payments"
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["branch", "status"]),
        ]

    def __str__(self):
        return f"{self.method} — {self.status} — {self.amount}"


class StaffCommission(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commissions")
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    commission_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        db_table = "staff_commissions"