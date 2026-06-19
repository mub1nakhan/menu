"""
Order models: Order, OrderItem, OrderStatusHistory
"""

from sqlalchemy import Column, String, ForeignKey, Numeric, DateTime, Integer, TEXT, Boolean, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseModel


class Order(BaseModel):
    """Customer order"""
    __tablename__ = "orders"
    
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False, index=True)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id", ondelete="CASCADE"), nullable=False, index=True)
    table_id = Column(UUID(as_uuid=True), ForeignKey("tables.id", ondelete="SET NULL"), index=True)
    customer_name = Column(String(150))
    order_type = Column(String(20), nullable=False)  # dine_in, takeout, delivery
    status = Column(String(20), default="pending", index=True)  # pending, confirmed, preparing, ready, served, cancelled
    total_amount = Column(Numeric(10, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    discount_amount = Column(Numeric(10, 2), default=0)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    served_at = Column(DateTime)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="orders")
    branch = relationship("Branch", back_populates="orders")
    table = relationship("Table", back_populates="orders")
    created_by = relationship("User", back_populates="orders", foreign_keys=[created_by_id])
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")
    status_history = relationship("OrderStatusHistory", back_populates="order", cascade="all, delete-orphan")


class OrderItem(BaseModel):
    """Individual item in an order"""
    __tablename__ = "order_items"
    
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    notes = Column(TEXT)
    status = Column(String(20), default="pending", index=True)  # pending, preparing, ready, served, cancelled
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


class OrderStatusHistory(BaseModel):
    """Audit trail for order status changes"""
    __tablename__ = "order_status_history"
    
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    order_item_id = Column(UUID(as_uuid=True), ForeignKey("order_items.id", ondelete="CASCADE"))
    from_status = Column(String(20))
    to_status = Column(String(20), nullable=False)
    changed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    notes = Column(TEXT)
    
    # Relationships
    order = relationship("Order", back_populates="status_history")
    order_item = relationship("OrderItem")
    changed_by = relationship("User", back_populates="order_status_history", foreign_keys=[changed_by_id])

