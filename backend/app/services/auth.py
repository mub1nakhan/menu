"""
Authentication service
"""

from typing import Optional, Tuple
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import User, Restaurant, Role
from app.core.security import (
    hash_password, 
    verify_password, 
    create_access_token, 
    create_refresh_token,
    verify_token,
    create_pin_hash,
    verify_pin,
)
from app.core.config import ACCESS_TOKEN_EXPIRE_TIMEDELTA, REFRESH_TOKEN_EXPIRE_TIMEDELTA
from app.schemas.auth import LoginRequest, TokenResponse


class AuthService:
    """Authentication service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def authenticate_user(self, email: str, password: str, restaurant_id: UUID) -> Optional[User]:
        """Authenticate user with email and password"""
        result = await self.db.execute(
            select(User).where(
                (User.email == email) & 
                (User.restaurant_id == restaurant_id) &
                (User.is_active == True)
            )
        )
        user = result.scalars().first()
        
        if not user or not verify_password(password, user.password_hash):
            return None
        
        # Update last login
        user.last_login_at = datetime.utcnow()
        await self.db.commit()
        
        return user
    
    async def authenticate_by_pin(self, pin: str, restaurant_id: UUID) -> Optional[User]:
        """Authenticate user with PIN code"""
        result = await self.db.execute(
            select(User).where(
                (User.restaurant_id == restaurant_id) &
                (User.pin_code_hash.isnot(None)) &
                (User.is_active == True)
            )
        )
        users = result.scalars().all()
        
        for user in users:
            if user.pin_code_hash and verify_pin(pin, user.pin_code_hash):
                user.last_login_at = datetime.utcnow()
                await self.db.commit()
                return user
        
        return None
    
    async def create_tokens(self, user: User) -> TokenResponse:
        """Create JWT tokens"""
        # Get user's role
        await self.db.refresh(user, ["role"])
        
        token_data = {
            "sub": str(user.id),
            "user_id": str(user.id),
            "email": user.email,
            "restaurant_id": str(user.restaurant_id),
            "branch_id": str(user.branch_id) if user.branch_id else None,
            "role": user.role.code if user.role else None,
        }
        
        access_token = create_access_token(
            token_data,
            expires_delta=ACCESS_TOKEN_EXPIRE_TIMEDELTA
        )
        refresh_token = create_refresh_token(token_data)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
    
    async def verify_access_token(self, token: str) -> Optional[dict]:
        """Verify and decode access token"""
        payload = verify_token(token)
        if not payload or payload.get("type") != "access":
            return None
        return payload
    
    async def refresh_access_token(self, refresh_token: str) -> Optional[TokenResponse]:
        """Create new access token from refresh token"""
        payload = verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None
        
        # Remove type and exp from payload
        del payload["type"]
        del payload["exp"]
        
        access_token = create_access_token(payload, expires_delta=ACCESS_TOKEN_EXPIRE_TIMEDELTA)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
    
    async def create_user(
        self,
        email: str,
        password: str,
        full_name: str,
        restaurant_id: UUID,
        role_id: UUID,
        branch_id: Optional[UUID] = None,
        phone: Optional[str] = None,
    ) -> User:
        """Create new user"""
        user = User(
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            restaurant_id=restaurant_id,
            branch_id=branch_id,
            role_id=role_id,
            phone=phone,
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def set_user_pin(self, user_id: UUID, pin: str) -> bool:
        """Set user's PIN code"""
        user = await self.db.get(User, user_id)
        if not user:
            return False
        
        user.pin_code_hash = create_pin_hash(pin)
        await self.db.commit()
        return True
    
    async def change_password(self, user_id: UUID, old_password: str, new_password: str) -> bool:
        """Change user password"""
        user = await self.db.get(User, user_id)
        if not user or not verify_password(old_password, user.password_hash):
            return False
        
        user.password_hash = hash_password(new_password)
        await self.db.commit()
        return True

