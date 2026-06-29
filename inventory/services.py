"""
inventory/services.py

Buyurtma yaratilganda ingredientlarni avtomatik kamaytirish logikasi.
orders/views.py dan chaqiriladi — orders app inventory'ga bog'liq bo'lmasligi
uchun alohida service modulida.
"""
from django.db import transaction

from inventory.models import Inventory, InventoryMovement, Recipe


@transaction.atomic
def deduct_stock_for_order(order):
    """
    Berilgan order'dagi har bir OrderItem uchun:
    1. Recipe'dan ingredientlar miqdorini oladi
    2. Inventory'dan shu miqdorni kamaytiradi
    3. InventoryMovement yozadi (audit trail)

    Stock yetarli bo'lmasa ham to'xtatmaydi — faqat 0 da qoldiradi
    va 'order_consumption' movement yozadi. Kritik alertlar
    inventory/views.py dagi low_stock endpoint orqali ko'rinadi.
    """
    for item in order.items.select_related("product").all():
        recipes = Recipe.objects.filter(
            product_id=item.product_id,
            restaurant_id=order.restaurant_id,
        ).select_related("ingredient")

        for recipe in recipes:
            needed = recipe.quantity * item.quantity

            # get_or_create: agar inventory row yo'q bo'lsa yaratiladi
            inv, _ = Inventory.objects.get_or_create(
                restaurant_id=order.restaurant_id,
                branch_id=order.branch_id,
                ingredient_id=recipe.ingredient_id,
                defaults={"quantity_on_hand": 0},
            )

            actual_deducted = min(inv.quantity_on_hand, needed)
            inv.quantity_on_hand = max(0, inv.quantity_on_hand - needed)
            inv.save(update_fields=["quantity_on_hand", "updated_at"])

            InventoryMovement.objects.create(
                restaurant_id=order.restaurant_id,
                branch_id=order.branch_id,
                ingredient_id=recipe.ingredient_id,
                movement_type="order_consumption",
                quantity=-actual_deducted,
                related_order=order,
                note=f"Order #{order.order_number} uchun avtomatik chiqim",
            )