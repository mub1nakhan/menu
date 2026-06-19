"""
Authentication endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.config import get_settings
from app.schemas.auth import LoginRequest, TokenResponse, RefreshTokenRequest, UserResponse, UserCreate
from app.services.auth import AuthService
from app.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()

# Security scheme
security = HTTPBearer()


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login with email and password"""
    # Get restaurant from header - this could be improved with better tenant discovery
    auth_service = AuthService(db)
    
    # For now, try to find the restaurant by email
    from sqlalchemy import select
    from app.models import User
    
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    # Authenticate
    authenticated_user = await auth_service.authenticate_user(
        credentials.email,
        credentials.password,
        user.restaurant_id,
    )
    
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    return await auth_service.create_tokens(authenticated_user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Refresh access token"""
    auth_service = AuthService(db)
    
    tokens = await auth_service.refresh_access_token(request.refresh_token)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    
    return tokens


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register new user"""
    auth_service = AuthService(db)
    
    # Check if user already exists
    from sqlalchemy import select
    result = await db.execute(
        select(User).where(
            (User.email == user_data.email) & 
            (User.restaurant_id == user_data.restaurant_id)
        )
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )
    
    # Create user
    user = await auth_service.create_user(
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        restaurant_id=user_data.restaurant_id,
        role_id=user_data.role_id,
        branch_id=user_data.branch_id,
        phone=user_data.phone,
    )
    
    return UserResponse.from_orm(user)


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """Get current user"""
    auth_service = AuthService(db)
    
    payload = await auth_service.verify_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    user = await db.get(User, UUID(payload["user_id"]))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return UserResponse.from_orm(user)


@router.post("/logout")
async def logout(credentials: HTTPAuthCredentials = Depends(security)):
    """Logout (JWT-based, so just return success)"""
    return {"message": "Successfully logged out"}

