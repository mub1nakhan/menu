"""
Menu models: Category, Product
"""

from sqlalchemy import Column, String, Boolean, ForeignKey, JSON, Numeric, Integer, TEXT
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseModel


class MenuCategory(BaseModel):
    """Menu category"""
    __tablename__ = "menu_categories"
    
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False, index=True)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id", ondelete="CASCADE"), index=True)
    name_i18n = Column(JSON, nullable=False)
    description_i18n = Column(JSON)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, index=True)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="menu_categories")
    branch = relationship("Branch", back_populates="menu_categories")
    products = relationship("Product", back_populates="category")


class Product(BaseModel):
    """Product/menu item"""
    __tablename__ = "products"
    
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False, index=True)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id", ondelete="CASCADE"), index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("menu_categories.id", ondelete="PROTECT"), nullable=False)
    name_i18n = Column(JSON, nullable=False)
    description_i18n = Column(JSON)
    sku = Column(String(50))
    price = Column(Numeric(10, 2), nullable=False)
    cost = Column(Numeric(10, 2))
    image_url = Column(String(500))
    is_available = Column(Boolean, default=True, index=True)
    is_active = Column(Boolean, default=True, index=True)
    prep_time_minutes = Column(Integer, default=15)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="products")
    branch = relationship("Branch", back_populates="products")
    category = relationship("MenuCategory", back_populates="products")
    recipes = relationship("Recipe", back_populates="product", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product")
    product_analytics = relationship("ProductAnalytics", back_populates="product", cascade="all, delete-orphan")
    waste_tracking = relationship("WasteTracking", back_populates="product", cascade="all, delete-orphan")

