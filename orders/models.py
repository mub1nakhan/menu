import uuid
from django.db import models
from tenancy.models import Branch, Restaurant, TimeStampedModel, User
from menu.models import Product


class TableStatus(models.TextChoices):
    FREE = "free", "Free"
    OCCUPIED = "occupied", "Occupied"
    RESERVED = "reserved", "Reserved"
    CLEANING = "cleaning", "Cleaning"


class OrderSource(models.TextChoices):
    QR_CUSTOMER = "qr_customer", "QR Customer"
    WAITER = "waiter", "Waiter"
    POS = "pos", "POS"


class OrderStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    PREPARING = "preparing", "Preparing"
    READY = "ready", "Ready"
    SERVED = "served", "Served"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class OrderItemStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PREPARING = "preparing", "Preparing"
    READY = "ready", "Ready"
    SERVED = "served", "Served"
    CANCELLED = "cancelled", "Cancelled"


# Valid status transitions — used in service layer to validate changes
ORDER_STATUS_TRANSITIONS = {
    OrderStatus.PENDING:    {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
    OrderStatus.CONFIRMED:  {OrderStatus.PREPARING, OrderStatus.CANCELLED},
    OrderStatus.PREPARING:  {OrderStatus.READY, OrderStatus.CANCELLED},
    OrderStatus.READY:      {OrderStatus.SERVED},
    OrderStatus.SERVED:     {OrderStatus.COMPLETED},
    OrderStatus.COMPLETED:  set(),
    OrderStatus.CANCELLED:  set(),
}


class Table(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="tables")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="tables")
    label = models.CharField(max_length=50)
    capacity = models.PositiveSmallIntegerField(default=4)
    qr_code_token = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=TableStatus.choices, default=TableStatus.FREE)

    class Meta:
        db_table = "tables"
        constraints = [
            models.UniqueConstraint(fields=["branch", "label"], name="uq_table_branch_label")
        ]

    def __str__(self):
        return f"{self.label} — {self.branch.name}"


class TableSession(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name="sessions")
    session_token = models.CharField(max_length=100, unique=True)
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "table_sessions"


class Order(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="orders")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="orders")
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    table_session = models.ForeignKey(TableSession, on_delete=models.SET_NULL, null=True, blank=True)
    order_number = models.CharField(max_length=30)
    source = models.CharField(max_length=20, choices=OrderSource.choices, default=OrderSource.QR_CUSTOMER)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "orders"
        constraints = [
            models.UniqueConstraint(fields=["branch", "order_number"], name="uq_order_branch_number")
        ]
        indexes = [
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["branch", "-created_at"]),
        ]

    def __str__(self):
        return f"Order #{self.order_number} — {self.status}"


class OrderItem(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    line_total = models.DecimalField(max_digits=14, decimal_places=2)
    status = models.CharField(max_length=20, choices=OrderItemStatus.choices, default=OrderItemStatus.PENDING)
    special_instructions = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "order_items"
        indexes = [models.Index(fields=["order"]), models.Index(fields=["status"])]

    def save(self, *args, **kwargs):
        self.line_total = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class OrderStatusHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="status_history")
    from_status = models.CharField(max_length=20, choices=OrderStatus.choices, null=True, blank=True)
    to_status = models.CharField(max_length=20, choices=OrderStatus.choices)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "order_status_history"
        ordering = ["-changed_at"]