from decimal import Decimal
import secrets

from django.db import transaction
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from menu.models import Product
from orders.models import Order, OrderItem, OrderStatus, OrderStatusHistory, Table, TableSession, ORDER_STATUS_TRANSITIONS
from orders.serializers import (
    OrderCreateSerializer, OrderSerializer, OrderStatusUpdateSerializer, TableSerializer
)
from tenancy.permissions import IsBranchStaffOrAbove, IsKitchenOrServiceStaff


def _next_order_number(branch_id) -> str:
    last = Order.objects.filter(branch_id=branch_id).order_by("-created_at").first()
    num = 1
    if last and last.order_number.isdigit():
        num = int(last.order_number) + 1
    return str(num).zfill(4)


class TableViewSet(viewsets.ModelViewSet):
    serializer_class = TableSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Table.objects.filter(restaurant_id=self.request.user.restaurant_id).order_by("branch", "label")

    def perform_create(self, serializer):
        token = secrets.token_urlsafe(16)
        serializer.save(restaurant_id=self.request.user.restaurant_id, qr_code_token=token)


class OrderViewSet(viewsets.ModelViewSet):
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

        # Chef/waiter: only their branch's orders
        user = self.request.user
        if user.branch_id:
            qs = qs.filter(branch_id=user.branch_id)

        # Filter by status if provided
        s = self.request.query_params.get("status")
        if s:
            qs = qs.filter(status=s)
        return qs

    @transaction.atomic
    def create(self, request):
        ser = OrderCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        user = request.user

        branch_id = user.branch_id or (
            Table.objects.get(id=data["table_id"]).branch_id if data.get("table_id") else None
        )
        if not branch_id:
            return Response({"detail": "branch_id required"}, status=400)

        # Build items, calculate totals
        subtotal = Decimal("0")
        item_rows = []
        for item_data in data["items"]:
            product = Product.objects.get(id=item_data["product"], restaurant_id=user.restaurant_id)
            line_total = product.price * item_data["quantity"]
            subtotal += line_total
            item_rows.append((product, item_data["quantity"], line_total, item_data.get("special_instructions", "")))

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
            order=order, from_status=None, to_status=OrderStatus.PENDING, changed_by=user
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

        return Response(OrderSerializer(order).data)