from rest_framework import serializers
from inventory.models import Ingredient, Inventory, InventoryMovement, Recipe


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ["id", "branch", "name", "unit", "unit_cost", "low_stock_threshold", "created_at"]
        read_only_fields = ["id", "created_at"]


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ["id", "product", "ingredient", "quantity", "unit"]
        read_only_fields = ["id"]


class InventorySerializer(serializers.ModelSerializer):
    ingredient_name = serializers.CharField(source="ingredient.name", read_only=True)
    unit = serializers.CharField(source="ingredient.unit", read_only=True)
    is_low = serializers.BooleanField(read_only=True)

    class Meta:
        model = Inventory
        fields = ["id", "branch", "ingredient", "ingredient_name", "unit", "quantity_on_hand", "is_low", "updated_at"]
        read_only_fields = ["id", "updated_at", "is_low"]


class InventoryMovementSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.CharField(source="ingredient.name", read_only=True)

    class Meta:
        model = InventoryMovement
        fields = ["id", "ingredient", "ingredient_name", "movement_type", "quantity", "related_order", "note", "created_at"]
        read_only_fields = ["id", "created_at"]


class StockAdjustmentSerializer(serializers.Serializer):
    ingredient = serializers.UUIDField()
    quantity = serializers.DecimalField(max_digits=14, decimal_places=3)
    movement_type = serializers.ChoiceField(choices=["stock_in", "adjustment", "waste", "theft_suspected"])
    note = serializers.CharField(required=False, allow_blank=True)