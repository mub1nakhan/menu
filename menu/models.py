"""
menu/models.py

MenuCategory and Product. Both are tenant-scoped (restaurant_id always;
branch_id optional — NULL means the item is shared across all branches of
that restaurant, set means it's branch-specific, e.g. a seasonal item only
sold at one location).

Multilingual fields use JSONField storing {"uz": "...", "ru": "...", "en": "..."}
so adding a new language never requires a schema migration.
"""
import uuid

from django.core.validators import MinValueValidator
from django.db import models

from tenancy.models import Branch, Restaurant, TimeStampedModel


class MenuCategory(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="menu_categories")
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name="menu_categories", blank=True, null=True,
        help_text="NULL = shared across all branches of this restaurant.",
    )
    name_i18n = models.JSONField(help_text='e.g. {"uz": "Birinchi taomlar", "ru": "Супы", "en": "Soups"}')
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "menu_categories"
        ordering = ["sort_order", "id"]
        indexes = [models.Index(fields=["restaurant", "branch"])]
        verbose_name_plural = "menu categories"

    def __str__(self) -> str:
        return self.name_i18n.get("en") or self.name_i18n.get("uz") or str(self.id)


class Product(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="products")
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name="products", blank=True, null=True,
        help_text="NULL = shared across all branches of this restaurant.",
    )
    category = models.ForeignKey(MenuCategory, on_delete=models.PROTECT, related_name="products")

    name_i18n = models.JSONField(help_text='e.g. {"uz": "Burger", "ru": "Бургер", "en": "Burger"}')
    description_i18n = models.JSONField(default=dict, blank=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)

    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    # Cached from the recipe's ingredient costs (see inventory app) — recalculated
    # whenever the recipe changes, so reads don't need to join through recipes.
    cost_price = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], blank=True, null=True
    )

    is_available = models.BooleanField(default=True)
    prep_time_minutes = models.PositiveSmallIntegerField(blank=True, null=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        db_table = "products"
        ordering = ["sort_order", "id"]
        indexes = [
            models.Index(fields=["restaurant", "branch"]),
            models.Index(fields=["branch", "is_available"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self) -> str:
        return self.name_i18n.get("en") or self.name_i18n.get("uz") or str(self.id)

    @property
    def margin(self) -> float | None:
        """Quick profitability signal for the admin/analytics app: price minus cost."""
        if self.cost_price is None:
            return None
        return float(self.price - self.cost_price)