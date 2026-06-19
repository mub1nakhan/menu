"""
Authentication schemas
"""

from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Login request"""
    email: EmailStr
    password: str = Field(..., min_length=6)


class PINLoginRequest(BaseModel):
    """PIN-based quick login"""
    pin: str = Field(..., min_length=4, max_length=6)
    restaurant_id: UUID


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class UserBase(BaseModel):
    """User base schema"""
    email: EmailStr
    full_name: str
    phone: Optional[str] = None


class UserCreate(UserBase):
    """Create user schema"""
    password: str = Field(..., min_length=8)
    restaurant_id: UUID
    branch_id: Optional[UUID] = None
    role_id: UUID


class UserUpdate(BaseModel):
    """Update user schema"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    pin_code: Optional[str] = None


class UserResponse(UserBase):
    """User response schema"""
    id: UUID
    restaurant_id: UUID
    branch_id: Optional[UUID] = None
    role_id: UUID
    is_active: bool
    last_login_at: Optional[str] = None
    
    class Config:
        from_attributes = True

