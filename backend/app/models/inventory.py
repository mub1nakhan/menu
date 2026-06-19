"""
Inventory models: Ingredient, Recipe, Inventory, InventoryMovement
"""

from sqlalchemy import Column, String, ForeignKey, Numeric, DateTime, TEXT, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseModel


class Ingredient(BaseModel):
    """Raw ingredient for recipes"""
    __tablename__ = "ingredients"
    
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    unit = Column(String(20), nullable=False)  # kg, liter, piece, etc
    cost_per_unit = Column(Numeric(10, 4))
    reorder_level = Column(Numeric(10, 2))
    is_active = Column(Boolean, default=True, index=True)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="ingredients")
    recipes = relationship("Recipe", back_populates="ingredient", cascade="all, delete-orphan")
    inventory = relationship("Inventory", back_populates="ingredient", cascade="all, delete-orphan")
    inventory_movements = relationship("InventoryMovement", back_populates="ingredient", cascade="all, delete-orphan")


class Recipe(BaseModel):
    """Bill of Materials - ingredient requirements for a product"""
    __tablename__ = "recipes"
    
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    ingredient_id = Column(UUID(as_uuid=True), ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="recipes")
    product = relationship("Product", back_populates="recipes")
    ingredient = relationship("Ingredient", back_populates="recipes")


class Inventory(BaseModel):
    """Stock level per ingredient per branch"""
    __tablename__ = "inventory"
    
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id", ondelete="CASCADE"), nullable=False, index=True)
    ingredient_id = Column(UUID(as_uuid=True), ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Numeric(10, 2), default=0)
    reserved = Column(Numeric(10, 2), default=0)
    last_counted_at = Column(DateTime)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="inventory")
    branch = relationship("Branch", back_populates="inventory")
    ingredient = relationship("Ingredient", back_populates="inventory")


class InventoryMovement(BaseModel):
    """Audit trail for inventory changes"""
    __tablename__ = "inventory_movements"
    
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False, index=True)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id", ondelete="CASCADE"), nullable=False, index=True)
    ingredient_id = Column(UUID(as_uuid=True), ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False)
    movement_type = Column(String(20), nullable=False, index=True)  # in, out, adjustment, waste, count
    quantity = Column(Numeric(10, 2), nullable=False)
    reference_type = Column(String(50))  # order, waste, adjustment
    reference_id = Column(UUID(as_uuid=True))
    notes = Column(TEXT)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="inventory_movements")
    branch = relationship("Branch", back_populates="inventory_movements")
    ingredient = relationship("Ingredient", back_populates="inventory_movements")
    created_by_user = relationship("User", back_populates="inventory_movements", foreign_keys=[created_by])

