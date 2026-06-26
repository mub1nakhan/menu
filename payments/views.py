from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from orders.models import Order, OrderStatus
from payments.models import Payment, PaymentStatus, StaffCommission
from payments.serializers import PaymentSerializer, PaymentCreateSerializer, StaffCommissionSerializer
from tenancy.permissions import IsBranchStaffOrAbove


class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return PaymentCreateSerializer
        return PaymentSerializer

    def get_queryset(self):
        qs = Payment.objects.filter(
            restaurant_id=self.request.user.restaurant_id
        ).select_related("order").order_by("-created_at")
        if self.request.user.branch_id:
            qs = qs.filter(branch_id=self.request.user.branch_id)
        return qs

    def create(self, request):
        ser = PaymentCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        user = request.user

        try:
            order = Order.objects.get(id=data["order"], restaurant_id=user.restaurant_id)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=404)

        payment = Payment.objects.create(
            restaurant_id=user.restaurant_id,
            branch_id=order.branch_id,
            order=order,
            method=data["method"],
            status=PaymentStatus.PAID,
            amount=data["amount"],
            currency=data.get("currency", "UZS"),
            provider=data.get("provider", ""),
            paid_at=timezone.now(),
        )

        # Mark order as completed if fully paid
        if float(data["amount"]) >= float(order.total_amount):
            order.status = OrderStatus.COMPLETED
            order.save(update_fields=["status", "updated_at"])

        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="refund", permission_classes=[IsBranchStaffOrAbove])
    def refund(self, request, pk=None):
        payment = self.get_object()
        if payment.status != PaymentStatus.PAID:
            return Response({"detail": "Only PAID payments can be refunded."}, status=400)
        payment.status = PaymentStatus.REFUNDED
        payment.save(update_fields=["status", "updated_at"])
        return Response(PaymentSerializer(payment).data)


class StaffCommissionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StaffCommissionSerializer
    permission_classes = [IsBranchStaffOrAbove]

    def get_queryset(self):
        return StaffCommission.objects.filter(
            restaurant_id=self.request.user.restaurant_id
        ).order_by("-created_at")