"""
core/urls.py — asosiy URL konfiguratsiyasi.

Barcha app'lar /api/v1/ prefiksi ostida.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

API_PREFIX = "api/v1/"

urlpatterns = [
    path("admin/", admin.site.urls),

    # Auth: login, pin-login, refresh, /me
    path(API_PREFIX, include("tenancy.urls")),

    # Menu: categories, products, public QR menu
    path(API_PREFIX, include("menu.urls")),

    # Orders: tables, orders, status updates
    path(API_PREFIX, include("orders.urls")),

    # Inventory: ingredients, recipes, stock, movements
    path(API_PREFIX, include("inventory.urls")),

    # Payments: payments, refunds, commissions
    path(API_PREFIX, include("payments.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)