"""
Base Pydantic schemas
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class BaseSchema(BaseModel):
    """Base schema with common fields"""
    id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TimestampSchema(BaseModel):
    """Schema with just timestamps"""
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

