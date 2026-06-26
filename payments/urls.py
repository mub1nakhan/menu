from rest_framework.routers import DefaultRouter
from django.urls import include, path
from payments.views import PaymentViewSet, StaffCommissionViewSet

router = DefaultRouter()
router.register("payments", PaymentViewSet, basename="payment")
router.register("commissions", StaffCommissionViewSet, basename="commission")

urlpatterns = [path("", include(router.urls))]