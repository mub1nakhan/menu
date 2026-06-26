import secrets
from rest_framework import serializers
from orders.models import Order, OrderItem, OrderStatus, ORDER_STATUS_TRANSITIONS, Table, TableSession


class OrderItemCreateSerializer(serializers.Serializer):
    product = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)
    special_instructions = serializers.CharField(required=False, allow_blank=True)


class OrderCreateSerializer(serializers.Serializer):
    table_id = serializers.UUIDField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True)
    source = serializers.ChoiceField(choices=Order.source.field.choices, default="waiter")
    items = OrderItemCreateSerializer(many=True, min_length=1)


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "quantity", "unit_price", "line_total", "status", "special_instructions"]

    def get_product_name(self, obj):
        return obj.product.name_i18n.get("en") or obj.product.name_i18n.get("uz", "")


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "order_number", "table", "source", "status",
            "subtotal", "discount_amount", "tax_amount", "total_amount",
            "notes", "items", "created_at",
        ]
        read_only_fields = fields


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=OrderStatus.choices)
    note = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        order: Order = self.context["order"]
        new_status = attrs["status"]
        allowed = ORDER_STATUS_TRANSITIONS.get(order.status, set())
        if new_status not in allowed:
            raise serializers.ValidationError(
                f"Cannot transition from '{order.status}' to '{new_status}'. "
                f"Allowed: {[s for s in allowed] or 'none'}"
            )
        return attrs


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ["id", "label", "capacity", "qr_code_token", "status", "branch"]
        read_only_fields = ["id", "qr_code_token"]