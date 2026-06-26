from rest_framework.routers import DefaultRouter
from django.urls import include, path

from menu.views import MenuCategoryViewSet, ProductViewSet, PublicMenuView

router = DefaultRouter()
router.register("categories", MenuCategoryViewSet, basename="category")
router.register("products", ProductViewSet, basename="product")

urlpatterns = [
    path("", include(router.urls)),
    # QR menu — mijozlar uchun (JWT yo'q)
    path(
        "public/menu/<uuid:branch_id>/",
        PublicMenuView.as_view({"get": "list"}),
        name="public-menu",
    ),
]