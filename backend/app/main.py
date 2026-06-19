"""
Main FastAPI Application - Restaurant OS
"""

import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.core.database import init_db
from app.middleware.tenant import tenant_middleware
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.orders import router as orders_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


# Lifespan context for app startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    # Startup
    logger.info("🚀 Starting Restaurant OS API...")
    # await init_db()  # Uncomment to auto-create tables on startup
    logger.info("✅ Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Restaurant OS API...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Complete SaaS Platform for Restaurant Management",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tenant middleware for multi-tenant request context
app.middleware("http")(tenant_middleware)

# Register routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(orders_router, prefix="/api/v1")


# Error handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": exc.body,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Health check
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# API v1 routes
@app.get("/api/v1/status", tags=["Status"])
async def api_status():
    """API status"""
    return {
        "status": "ready",
        "version": settings.APP_VERSION,
        "environment": "development" if settings.DEBUG else "production",
    }


logger.info(f"✨ {settings.APP_NAME} v{settings.APP_VERSION} initialized")

