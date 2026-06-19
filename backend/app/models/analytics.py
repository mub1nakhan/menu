"""
Payment and Analytics models
"""

from sqlalchemy import Column, String, ForeignKey, Numeric, DateTime, Date, JSON, Integer, TEXT
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseModel


# ============================================================================
# PAYMENT MODELS
# ============================================================================

class Payment(BaseModel):
    """Payment transaction"""
    __tablename__ = "payments"
    
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False, index=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    payment_method = Column(String(20), nullable=False)  # card, cash, qr_code, mobile
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), default="pending", index=True)  # pending, completed, failed, refunded
    transaction_id = Column(String(100))
    gateway_response = Column(JSON)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="payments")
    order = relationship("Order", back_populates="payments")


# ============================================================================
# ANALYTICS MODELS
# ============================================================================

class DailySales(BaseModel):
    """Daily sales summary"""
    __tablename__ = "daily_sales"
    
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id", ondelete="CASCADE"), nullable=False, index=True)
    sale_date = Column(Date, nullable=False)
    total_orders = Column(Integer, default=0)
    total_sales = Column(Numeric(12, 2), default=0)
    total_cost = Column(Numeric(12, 2), default=0)
    total_tax = Column(Numeric(10, 2), default=0)
    avg_order_value = Column(Numeric(10, 2), default=0)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="daily_sales")
    branch = relationship("Branch", back_populates="daily_sales")


class ProductAnalytics(BaseModel):
    """Daily product sales analytics"""
    __tablename__ = "product_analytics"
    
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    quantity_sold = Column(Integer, default=0)
    revenue = Column(Numeric(10, 2), default=0)
    cost = Column(Numeric(10, 2), default=0)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="product_analytics")
    product = relationship("Product", back_populates="product_analytics")


class StaffCommission(BaseModel):
    """Daily staff commission tracking"""
    __tablename__ = "staff_commission"
    
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    commission_date = Column(Date, nullable=False)
    total_orders = Column(Integer, default=0)
    base_commission = Column(Numeric(10, 2), default=0)
    bonus_commission = Column(Numeric(10, 2), default=0)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="staff_commission")
    user = relationship("User", back_populates="staff_commission")


class WasteTracking(BaseModel):
    """Food waste tracking"""
    __tablename__ = "waste_tracking"
    
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id", ondelete="CASCADE"), nullable=False, index=True)
    ingredient_id = Column(UUID(as_uuid=True), ForeignKey("ingredients.id", ondelete="SET NULL"))
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="SET NULL"))
    quantity = Column(Numeric(10, 2), nullable=False)
    reason = Column(String(100))
    recorded_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="waste_tracking")
    branch = relationship("Branch", back_populates="waste_tracking")
    ingredient = relationship("Ingredient", foreign_keys=[ingredient_id])
    product = relationship("Product", back_populates="waste_tracking", foreign_keys=[product_id])
    recorded_by = relationship("User", back_populates="waste_tracking", foreign_keys=[recorded_by_id])


class AuditLog(BaseModel):
    """System audit log"""
    __tablename__ = "audit_log"
    
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    action = Column(String(50), nullable=False)
    entity_type = Column(String(50))
    entity_id = Column(UUID(as_uuid=True))
    old_values = Column(JSON)
    new_values = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(TEXT)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="audit_log")
    user = relationship("User", back_populates="audit_log")


class Notification(BaseModel):
    """User notifications"""
    __tablename__ = "notifications"
    
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(150))
    message = Column(TEXT)
    notification_type = Column(String(50))
    read = Column(Boolean, default=False, index=True)
    action_url = Column(String(500))
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="notifications")
    user = relationship("User", back_populates="notifications")

