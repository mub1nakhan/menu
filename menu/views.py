"""
menu/views.py

MenuCategory va Product uchun CRUD ViewSetlar.
Barcha so'rovlar tenant-scoped: faqat o'z restaurant'ingizga tegishli
ma'lumotlarni ko'rasiz va o'zgartira olasiz.

Patterns:
  - get_queryset()     → restaurant_id bilan filter
  - perform_create()   → restaurant_id avtomatik qo'yiladi
  - PublicMenuView     → JWT talab qilmaydi, QR scanner uchun
"""
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from menu.models import MenuCategory, Product
from menu.serializers import MenuCategorySerializer, ProductSerializer, PublicProductSerializer
from tenancy.models import Branch
from tenancy.permissions import IsBranchStaffOrAbove, IsOwnerOrSuperAdmin


class MenuCategoryViewSet(viewsets.ModelViewSet):
    """
    /api/v1/categories/
    GET    — barcha kategoriyalar (authenticated)
    POST   — yangi kategoriya (owner/manager/super_admin)
    PATCH  — tahrirlash       (owner/manager/super_admin)
    DELETE — o'chirish        (owner/super_admin)
    """
    serializer_class = MenuCategorySerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsBranchStaffOrAbove()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        qs = MenuCategory.objects.filter(
            restaurant_id=self.request.user.restaurant_id
        ).order_by("sort_order", "id")

        # branch filter (optional query param)
        branch_id = self.request.query_params.get("branch")
        if branch_id:
            qs = qs.filter(branch_id=branch_id)

        # active only filter
        active = self.request.query_params.get("active")
        if active is not None:
            qs = qs.filter(is_active=active.lower() in ("true", "1", "yes"))

        return qs

    def perform_create(self, serializer):
        serializer.save(restaurant_id=self.request.user.restaurant_id)


class ProductViewSet(viewsets.ModelViewSet):
    """
    /api/v1/products/
    GET    — barcha mahsulotlar (authenticated)
    POST   — yangi mahsulot    (owner/manager/super_admin)
    PATCH  — tahrirlash        (owner/manager/super_admin)
    DELETE — o'chirish         (owner/super_admin)

    Query params:
      ?category=<uuid>   — kategoriya bo'yicha filter
      ?branch=<uuid>     — filial bo'yicha filter
      ?available=true    — faqat mavjud mahsulotlar
    """
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsBranchStaffOrAbove()]
        return [permissions.IsAuthenticated()]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def get_queryset(self):
        qs = Product.objects.filter(
            restaurant_id=self.request.user.restaurant_id
        ).select_related("category").order_by("sort_order", "id")

        category_id = self.request.query_params.get("category")
        if category_id:
            qs = qs.filter(category_id=category_id)

        branch_id = self.request.query_params.get("branch")
        if branch_id:
            qs = qs.filter(branch_id=branch_id)

        available = self.request.query_params.get("available")
        if available is not None:
            qs = qs.filter(is_available=available.lower() in ("true", "1", "yes"))

        return qs

    def perform_create(self, serializer):
        serializer.save(restaurant_id=self.request.user.restaurant_id)

    @action(detail=True, methods=["patch"], url_path="toggle-availability")
    def toggle_availability(self, request, pk=None):
        """PATCH /api/v1/products/<id>/toggle-availability/ — tez on/off"""
        product = self.get_object()
        product.is_available = not product.is_available
        product.save(update_fields=["is_available", "updated_at"])
        return Response({"id": str(product.id), "is_available": product.is_available})


class PublicMenuView(viewsets.ReadOnlyModelViewSet):
    """
    /api/v1/public/menu/<branch_id>/
    JWT talab qilmaydi — QR kod orqali kirgan mijoz uchun.
    Faqat is_available=True mahsulotlar, tanlangan tilda.

    Query param:
      ?lang=uz|ru|en  (default: uz)
    """
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        branch_id = self.kwargs.get("branch_id")
        return Product.objects.filter(
            branch_id=branch_id,
            is_available=True,
        ).select_related("category").order_by("category__sort_order", "sort_order")

    def get_serializer_class(self):
        return PublicProductSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["lang"] = self.request.query_params.get("lang", "uz")
        return ctx

    def list(self, request, *args, **kwargs):
        """Mahsulotlarni kategoriyalar bo'yicha guruhlaydi."""
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        data = serializer.data

        # Kategoriyalar bo'yicha guruhlash
        lang = request.query_params.get("lang", "uz")
        grouped = {}
        for item in data:
            cat_id = str(item["category"])
            if cat_id not in grouped:
                try:
                    cat = MenuCategory.objects.get(id=cat_id)
                    cat_name = cat.name_i18n.get(lang) or cat.name_i18n.get("uz") or cat_id
                except MenuCategory.DoesNotExist:
                    cat_name = cat_id
                grouped[cat_id] = {"category_id": cat_id, "category_name": cat_name, "products": []}
            grouped[cat_id]["products"].append(item)

        return Response(list(grouped.values()))