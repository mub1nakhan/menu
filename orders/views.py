from decimal import Decimal
import secrets

from django.db import transaction
from django.db.models import Max
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from menu.models import Product
from orders.models import (
    Order, OrderItem, OrderStatus, OrderStatusHistory,
    Table, TableSession, ORDER_STATUS_TRANSITIONS
)
from orders.serializers import (
    OrderCreateSerializer, OrderSerializer, OrderStatusUpdateSerializer, TableSerializer
)
from tenancy.permissions import IsBranchStaffOrAbove, IsKitchenOrServiceStaff


def _next_order_number(branch_id) -> str:
    """
    Race-condition safe order number generator.
    Uses select_for_update() + Max() aggregation so concurrent requests
    never get the same order number.
    """
    # Max() inside a transaction with the row locked
    result = Order.objects.select_for_update().filter(
        branch_id=branch_id
    ).aggregate(max_num=Max("order_number"))
    
    last_num = result["max_num"]
    try:
        num = int(last_num) + 1 if last_num else 1
    except (ValueError, TypeError):
        num = Order.objects.filter(branch_id=branch_id).count() + 1
    
    return str(num).zfill(4)


class TableViewSet(viewsets.ModelViewSet):
    serializer_class = TableSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Table.objects.filter(
            restaurant_id=self.request.user.restaurant_id
        ).order_by("branch", "label")

    def perform_create(self, serializer):
        token = secrets.token_urlsafe(16)
        serializer.save(restaurant_id=self.request.user.restaurant_id, qr_code_token=token)


class OrderViewSet(viewsets.ModelViewSet):
    # Waiter, chef, cashier + branch staff + owner — barchasi buyurtma ko'ra oladi
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        if self.action == "update_status":
            return OrderStatusUpdateSerializer
        return OrderSerializer

    def get_queryset(self):
        qs = Order.objects.filter(
            restaurant_id=self.request.user.restaurant_id
        ).prefetch_related("items__product").order_by("-created_at")

        user = self.request.user
        # Branch-scoped staff faqat o'z filiali buyurtmalarini ko'radi
        if user.branch_id:
            qs = qs.filter(branch_id=user.branch_id)

        s = self.request.query_params.get("status")
        if s:
            qs = qs.filter(status=s)
        return qs

    @transaction.atomic
    def create(self, request):
        # Waiter ham, owner ham buyurtma yarata oladi
        ser = OrderCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        user = request.user

        # branch_id: foydalanuvchi branch'idan yoki table'dan
        branch_id = user.branch_id
        if not branch_id and data.get("table_id"):
            try:
                branch_id = Table.objects.get(id=data["table_id"]).branch_id
            except Table.DoesNotExist:
                return Response({"detail": "Table not found."}, status=404)

        if not branch_id:
            return Response({"detail": "branch_id talab qilinadi."}, status=400)

        # Buyurtma mahsulotlarini tekshirish va narx hisoblash
        subtotal = Decimal("0")
        item_rows = []
        for item_data in data["items"]:
            try:
                product = Product.objects.get(
                    id=item_data["product"],
                    restaurant_id=user.restaurant_id,
                    is_available=True,
                )
            except Product.DoesNotExist:
                return Response(
                    {"detail": f"Mahsulot topilmadi yoki mavjud emas: {item_data['product']}"},
                    status=400,
                )
            line_total = product.price * item_data["quantity"]
            subtotal += line_total
            item_rows.append((
                product,
                item_data["quantity"],
                line_total,
                item_data.get("special_instructions", ""),
            ))

        order = Order.objects.create(
            restaurant_id=user.restaurant_id,
            branch_id=branch_id,
            table_id=data.get("table_id"),
            order_number=_next_order_number(branch_id),
            source=data.get("source", "waiter"),
            status=OrderStatus.PENDING,
            created_by=user,
            subtotal=subtotal,
            total_amount=subtotal,
            notes=data.get("notes", ""),
        )

        for product, qty, line_total, instructions in item_rows:
            OrderItem.objects.create(
                restaurant_id=user.restaurant_id,
                order=order,
                product=product,
                quantity=qty,
                unit_price=product.price,
                line_total=line_total,
                special_instructions=instructions,
            )

        OrderStatusHistory.objects.create(
            order=order,
            from_status=None,
            to_status=OrderStatus.PENDING,
            changed_by=user,
        )

        # Stol statusini OCCUPIED ga o'zgartir
        if order.table_id:
            Table.objects.filter(id=order.table_id).update(status="occupied")

        # Ingredientlarni avtomatik kamaytir (recipe bo'lsa)
        try:
            from inventory.services import deduct_stock_for_order
            deduct_stock_for_order(order)
        except Exception:
            # Inventory xatosi buyurtmani to'xtatmasin — faqat log qilinadi
            import logging
            logging.getLogger(__name__).exception(
                "Inventory deduction failed for order %s", order.id
            )

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["patch"], url_path="status")
    @transaction.atomic
    def update_status(self, request, pk=None):
        order = self.get_object()
        ser = OrderStatusUpdateSerializer(data=request.data, context={"order": order})
        ser.is_valid(raise_exception=True)

        old_status = order.status
        new_status = ser.validated_data["status"]
        order.status = new_status
        order.save(update_fields=["status", "updated_at"])

        OrderStatusHistory.objects.create(
            order=order,
            from_status=old_status,
            to_status=new_status,
            changed_by=request.user,
            note=ser.validated_data.get("note", ""),
        )

        # Buyurtma yakunlanganda stol FREE ga qaytadi
        if new_status in (OrderStatus.COMPLETED, OrderStatus.CANCELLED):
            if order.table_id:
                # Agar ushbu stolda boshqa faol buyurtma bo'lmasa
                active_count = Order.objects.filter(
                    table_id=order.table_id,
                    status__in=[OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.PREPARING, OrderStatus.READY],
                ).exclude(id=order.id).count()
                if active_count == 0:
                    Table.objects.filter(id=order.table_id).update(status="free")

        return Response(OrderSerializer(order).data)