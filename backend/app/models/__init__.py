"""
Models package - export all models
"""

from app.models.base import BaseModel
from app.models.tenancy import Restaurant, Branch, User, Role, Table
from app.models.menu import MenuCategory, Product
from app.models.inventory import Ingredient, Recipe, Inventory, InventoryMovement
from app.models.orders import Order, OrderItem, OrderStatusHistory
from app.models.analytics import (
    Payment,
    DailySales,
    ProductAnalytics,
    StaffCommission,
    WasteTracking,
    AuditLog,
    Notification,
)

__all__ = [
    "BaseModel",
    "Restaurant",
    "Branch",
    "User",
    "Role",
    "Table",
    "MenuCategory",
    "Product",
    "Ingredient",
    "Recipe",
    "Inventory",
    "InventoryMovement",
    "Order",
    "OrderItem",
    "OrderStatusHistory",
    "Payment",
    "DailySales",
    "ProductAnalytics",
    "StaffCommission",
    "WasteTracking",
    "AuditLog",
    "Notification",
]

