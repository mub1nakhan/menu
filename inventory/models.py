import uuid
from django.db import models
from tenancy.models import Branch, Restaurant, TimeStampedModel, User
from menu.models import Product


class MeasurementUnit(models.TextChoices):
    G = "g", "Gram"
    KG = "kg", "Kilogram"
    ML = "ml", "Millilitre"
    L = "l", "Litre"
    PCS = "pcs", "Pieces"
    TBSP = "tbsp", "Tablespoon"
    TSP = "tsp", "Teaspoon"


class MovementType(models.TextChoices):
    STOCK_IN = "stock_in", "Stock In"
    STOCK_OUT = "stock_out", "Stock Out"
    ADJUSTMENT = "adjustment", "Adjustment"
    WASTE = "waste", "Waste"
    THEFT_SUSPECTED = "theft_suspected", "Theft Suspected"
    ORDER_CONSUMPTION = "order_consumption", "Order Consumption"
    TRANSFER = "transfer", "Transfer"


class Ingredient(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="ingredients")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=150)
    unit = models.CharField(max_length=10, choices=MeasurementUnit.choices)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    low_stock_threshold = models.DecimalField(max_digits=12, decimal_places=3, default=0)

    class Meta:
        db_table = "ingredients"

    def __str__(self):
        return f"{self.name} ({self.unit})"


class Recipe(models.Model):
    """BOM: one row per (product, ingredient) — how much of each ingredient one serving uses."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="recipe_items")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT, related_name="recipe_items")
    quantity = models.DecimalField(max_digits=12, decimal_places=3)
    unit = models.CharField(max_length=10, choices=MeasurementUnit.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "recipes"
        constraints = [
            models.UniqueConstraint(fields=["product", "ingredient"], name="uq_recipe_product_ingredient")
        ]


class Inventory(models.Model):
    """Current stock level per ingredient per branch — always one row per (branch, ingredient)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity_on_hand = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "inventory"
        constraints = [
            models.UniqueConstraint(fields=["branch", "ingredient"], name="uq_inventory_branch_ingredient")
        ]

    def is_low(self) -> bool:
        return self.quantity_on_hand <= self.ingredient.low_stock_threshold


class InventoryMovement(models.Model):
    """Full audit trail of every stock change."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    movement_type = models.CharField(max_length=25, choices=MovementType.choices)
    quantity = models.DecimalField(max_digits=14, decimal_places=3)  # + = in, - = out
    related_order = models.ForeignKey("orders.Order", on_delete=models.SET_NULL, null=True, blank=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inventory_movements"
        indexes = [
            models.Index(fields=["branch", "-created_at"]),
            models.Index(fields=["ingredient", "-created_at"]),
            models.Index(fields=["movement_type"]),
        ]