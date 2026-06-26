from rest_framework.routers import DefaultRouter
from django.urls import include, path
from orders.views import OrderViewSet, TableViewSet

router = DefaultRouter()
router.register("tables", TableViewSet, basename="table")
router.register("orders", OrderViewSet, basename="order")

urlpatterns = [path("", include(router.urls))]