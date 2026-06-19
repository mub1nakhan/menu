"""
Multi-tenant models: Restaurant, Branch, User, Role, Table
"""

from sqlalchemy import Column, String, Boolean, ForeignKey, JSON, Numeric, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4

from app.models.base import BaseModel


class Restaurant(BaseModel):
    """Tenant - A restaurant"""
    __tablename__ = "restaurants"
    
    name = Column(String(150), nullable=False)
    slug = Column(String(150), unique=True, nullable=False, index=True)
    legal_name = Column(String(200))
    tax_id = Column(String(50))
    subscription_plan = Column(String(20), default="trial")
    subscription_expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True, index=True)
    settings = Column(JSON, default=dict)
    
    # Relationships
    branches = relationship("Branch", back_populates="restaurant", cascade="all, delete-orphan")
    users = relationship("User", back_populates="restaurant", cascade="all, delete-orphan")
    roles = relationship("Role", back_populates="restaurant", cascade="all, delete-orphan")
    menu_categories = relationship("MenuCategory", back_populates="restaurant", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="restaurant", cascade="all, delete-orphan")
    ingredients = relationship("Ingredient", back_populates="restaurant", cascade="all, delete-orphan")
    recipes = relationship("Recipe", back_populates="restaurant", cascade="all, delete-orphan")
    inventory = relationship("Inventory", back_populates="restaurant", cascade="all, delete-orphan")
    inventory_movements = relationship("InventoryMovement", back_populates="restaurant", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="restaurant", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="restaurant", cascade="all, delete-orphan")
    daily_sales = relationship("DailySales", back_populates="restaurant", cascade="all, delete-orphan")
    product_analytics = relationship("ProductAnalytics", back_populates="restaurant", cascade="all, delete-orphan")
    staff_commission = relationship("StaffCommission", back_populates="restaurant", cascade="all, delete-orphan")
    waste_tracking = relationship("WasteTracking", back_populates="restaurant", cascade="all, delete-orphan")
    audit_log = relationship("AuditLog", back_populates="restaurant", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="restaurant", cascade="all, delete-orphan")


class Branch(BaseModel):
    """Physical location of a restaurant"""
    __tablename__ = "branches"
    
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    address = Column(String(500))
    city = Column(String(100))
    timezone = Column(String(50), default="Asia/Tashkent")
    currency = Column(String(10), default="UZS")
    phone = Column(String(30))
    latitude = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))
    is_active = Column(Boolean, default=True, index=True)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="branches")
    tables = relationship("Table", back_populates="branch", cascade="all, delete-orphan")
    staff = relationship("User", back_populates="branch")
    menu_categories = relationship("MenuCategory", back_populates="branch", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="branch", cascade="all, delete-orphan")
    inventory = relationship("Inventory", back_populates="branch", cascade="all, delete-orphan")
    inventory_movements = relationship("InventoryMovement", back_populates="branch", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="branch", cascade="all, delete-orphan")
    daily_sales = relationship("DailySales", back_populates="branch", cascade="all, delete-orphan")
    waste_tracking = relationship("WasteTracking", back_populates="branch", cascade="all, delete-orphan")


class Table(BaseModel):
    """Physical table in a branch"""
    __tablename__ = "tables"
    
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id", ondelete="CASCADE"), nullable=False, index=True)
    table_number = Column(String(10), nullable=False)
    seats = Column(String, default=4)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    branch = relationship("Branch", back_populates="tables")
    orders = relationship("Order", back_populates="table")


class Role(BaseModel):
    """Role with permissions"""
    __tablename__ = "roles"
    
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), index=True)
    name = Column(String(50), nullable=False)
    code = Column(String(50), nullable=False)
    permissions = Column(JSON, default=list)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="roles")
    users = relationship("User", back_populates="role")


class User(BaseModel):
    """User account"""
    __tablename__ = "users"
    
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False, index=True)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id", ondelete="SET NULL"))
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="PROTECT"), nullable=False)
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=False)
    phone = Column(String(30))
    pin_code_hash = Column(String(255))
    is_active = Column(Boolean, default=True, index=True)
    is_staff = Column(Boolean, default=False)
    last_login_at = Column(DateTime)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="users")
    branch = relationship("Branch", back_populates="staff")
    role = relationship("Role", back_populates="users")
    orders = relationship("Order", back_populates="created_by", foreign_keys="Order.created_by_id")
    inventory_movements = relationship("InventoryMovement", back_populates="created_by")
    order_status_history = relationship("OrderStatusHistory", back_populates="changed_by")
    waste_tracking = relationship("WasteTracking", back_populates="recorded_by")
    staff_commission = relationship("StaffCommission", back_populates="user")
    audit_log = relationship("AuditLog", back_populates="user")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

