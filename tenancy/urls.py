from rest_framework.routers import DefaultRouter

from django.urls import include, path

from tenancy.views import (
    BranchViewSet,
    MeView,
    PinLoginView,
    TenantLoginView,
    TenantTokenRefreshView,
)

router = DefaultRouter()
router.register("branches", BranchViewSet, basename="branch")

urlpatterns = [
    path("auth/login/", TenantLoginView.as_view(), name="login"),
    path("auth/login/pin/", PinLoginView.as_view(), name="login-pin"),
    path("auth/refresh/", TenantTokenRefreshView.as_view(), name="token-refresh"),
    path("auth/me/", MeView.as_view(), name="me"),
    path("", include(router.urls)),
]