from django.db import transaction
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from inventory.models import Ingredient, Inventory, InventoryMovement, Recipe
from inventory.serializers import (
    IngredientSerializer, InventorySerializer, InventoryMovementSerializer,
    RecipeSerializer, StockAdjustmentSerializer
)
from tenancy.permissions import IsBranchStaffOrAbove


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    permission_classes = [IsBranchStaffOrAbove]

    def get_queryset(self):
        return Ingredient.objects.filter(restaurant_id=self.request.user.restaurant_id)

    def perform_create(self, serializer):
        serializer.save(restaurant_id=self.request.user.restaurant_id)


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = [IsBranchStaffOrAbove]

    def get_queryset(self):
        return Recipe.objects.filter(restaurant_id=self.request.user.restaurant_id).select_related("product", "ingredient")

    def perform_create(self, serializer):
        serializer.save(restaurant_id=self.request.user.restaurant_id)


class InventoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InventorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Inventory.objects.filter(
            restaurant_id=self.request.user.restaurant_id
        ).select_related("ingredient")
        if self.request.user.branch_id:
            qs = qs.filter(branch_id=self.request.user.branch_id)
        return qs

    @action(detail=False, methods=["get"], url_path="low-stock")
    def low_stock(self, request):
        """Returns only ingredients below their low_stock_threshold — used by AI insights."""
        items = [i for i in self.get_queryset() if i.is_low()]
        return Response(InventorySerializer(items, many=True).data)

    @action(detail=False, methods=["post"], url_path="adjust",
            permission_classes=[IsBranchStaffOrAbove])
    @transaction.atomic
    def adjust(self, request):
        ser = StockAdjustmentSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        user = request.user
        branch_id = user.branch_id

        if not branch_id:
            return Response({"detail": "Branch-scoped user required for stock adjustments."}, status=400)

        inv, _ = Inventory.objects.get_or_create(
            restaurant_id=user.restaurant_id,
            branch_id=branch_id,
            ingredient_id=data["ingredient"],
            defaults={"quantity_on_hand": 0},
        )

        qty = data["quantity"]
        if data["movement_type"] in ("adjustment", "stock_in"):
            inv.quantity_on_hand += qty
        else:  # waste, theft_suspected
            inv.quantity_on_hand = max(0, inv.quantity_on_hand - abs(qty))
        inv.save()

        InventoryMovement.objects.create(
            restaurant_id=user.restaurant_id,
            branch_id=branch_id,
            ingredient_id=data["ingredient"],
            movement_type=data["movement_type"],
            quantity=qty if data["movement_type"] == "stock_in" else -abs(qty),
            performed_by=user,
            note=data.get("note", ""),
        )

        return Response(InventorySerializer(inv).data, status=status.HTTP_200_OK)


class InventoryMovementViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InventoryMovementSerializer
    permission_classes = [IsBranchStaffOrAbove]

    def get_queryset(self):
        qs = InventoryMovement.objects.filter(
            restaurant_id=self.request.user.restaurant_id
        ).select_related("ingredient").order_by("-created_at")
        if self.request.user.branch_id:
            qs = qs.filter(branch_id=self.request.user.branch_id)
        return qs