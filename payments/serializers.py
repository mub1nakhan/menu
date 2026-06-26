from rest_framework import serializers
from payments.models import Payment, StaffCommission


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id", "order", "method", "status", "amount", "currency",
            "provider", "provider_transaction_id", "paid_at", "created_at",
        ]
        read_only_fields = ["id", "created_at", "paid_at"]


class PaymentCreateSerializer(serializers.Serializer):
    order = serializers.UUIDField()
    method = serializers.ChoiceField(choices=Payment.method.field.choices)
    amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    currency = serializers.CharField(default="UZS")
    provider = serializers.CharField(required=False, allow_blank=True)


class StaffCommissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffCommission
        fields = ["id", "user", "order", "commission_rate", "commission_amount", "created_at"]
        read_only_fields = ["id", "created_at"]