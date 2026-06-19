"""
Multi-tenant middleware
"""

from fastapi import Request
from uuid import UUID
from typing import Optional


class TenantContext:
    """Request context for tenant data"""
    
    def __init__(self):
        self.restaurant_id: Optional[UUID] = None
        self.branch_id: Optional[UUID] = None
        self.user_id: Optional[UUID] = None
        self.user_role: Optional[str] = None


# Request-local storage for tenant context
import contextvars

tenant_context = contextvars.ContextVar("tenant_context", default=None)


async def get_tenant_context() -> Optional[TenantContext]:
    """Get current tenant context"""
    return tenant_context.get()


async def set_tenant_context(context: TenantContext):
    """Set tenant context"""
    tenant_context.set(context)


async def tenant_middleware(request: Request, call_next):
    """Extract tenant information from token and set context"""
    context = TenantContext()
    
    # Extract from token if available
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        from app.core.security import verify_token
        
        token = auth_header[7:]
        payload = verify_token(token)
        
        if payload:
            context.restaurant_id = payload.get("restaurant_id")
            context.branch_id = payload.get("branch_id")
            context.user_id = payload.get("user_id")
            context.user_role = payload.get("role")
    
    await set_tenant_context(context)
    
    response = await call_next(request)
    return response

