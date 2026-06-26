from rest_framework.routers import DefaultRouter
from django.urls import include, path
from inventory.views import IngredientViewSet, RecipeViewSet, InventoryViewSet, InventoryMovementViewSet

router = DefaultRouter()
router.register("inventory/ingredients", IngredientViewSet, basename="ingredient")
router.register("inventory/recipes", RecipeViewSet, basename="recipe")
router.register("inventory/stock", InventoryViewSet, basename="inventory")
router.register("inventory/movements", InventoryMovementViewSet, basename="inventory-movement")

urlpatterns = [path("", include(router.urls))]