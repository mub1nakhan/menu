#!/bin/bash

# Restaurant OS - Development Helper Commands
# Use these individual commands as needed

# ============================================
# 1. DOCKER COMMANDS
# ============================================

# Start all services
function start_docker() {
    docker-compose up -d
    echo "✓ Services started"
}

# Stop all services
function stop_docker() {
    docker-compose down
    echo "✓ Services stopped"
}

# View logs
function logs_backend() {
    docker-compose logs -f backend
}

function logs_database() {
    docker-compose logs -f postgres
}

function logs_redis() {
    docker-compose logs -f redis
}

# Restart specific service
function restart_backend() {
    docker-compose restart backend
    echo "✓ Backend restarted"
}

function restart_postgres() {
    docker-compose restart postgres
    echo "✓ PostgreSQL restarted"
}

# ============================================
# 2. DATABASE COMMANDS
# ============================================

# Connect to PostgreSQL database
function db_shell() {
    docker-compose exec postgres psql -U restaurant -d restaurant_os
}

# Create database backup
function db_backup() {
    BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
    docker-compose exec -T postgres pg_dump -U restaurant restaurant_os > "backups/$BACKUP_FILE"
    echo "✓ Database backed up to: backups/$BACKUP_FILE"
}

# Reset database (WARNING: Deletes all data)
function db_reset() {
    read -p "Are you sure? This will delete all data (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose exec -T postgres psql -U restaurant -d restaurant_os -f /docker-entrypoint-initdb.d/init.sql
        echo "✓ Database reset"
    fi
}

# ============================================
# 3. BACKEND COMMANDS
# ============================================

# Install backend dependencies
function backend_install() {
    cd backend
    pip install -r requirements-backend.txt
    cd ..
    echo "✓ Backend dependencies installed"
}

# Run backend locally (without Docker)
function backend_dev() {
    cd backend
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

# Run backend tests
function backend_test() {
    docker-compose exec backend pytest app/tests/ -v
    echo "✓ Tests completed"
}

# ============================================
# 4. FRONTEND COMMANDS
# ============================================

# Install all frontend dependencies
function frontend_install() {
    if [ ! -d "frontend/customer-app" ]; then
        echo "⚠ No frontend projects found. Skipping frontend install."
        return
    fi
    echo "Installing Customer App..."
    cd frontend/customer-app && npm install && cd ../..
    if [ -d "frontend/waiter-app" ]; then
        echo "Installing Waiter App..."
        cd frontend/waiter-app && npm install && cd ../..
    fi
    if [ -d "frontend/chef-app" ]; then
        echo "Installing Chef App..."
        cd frontend/chef-app && npm install && cd ../..
    fi
    if [ -d "frontend/admin-app" ]; then
        echo "Installing Admin App..."
        cd frontend/admin-app && npm install && cd ../..
    fi
    echo "✓ Frontend install complete"
}

# Start all frontend apps
function frontend_dev() {
    if [ ! -d "frontend/customer-app" ]; then
        echo "⚠ No frontend projects found. Skipping frontend dev startup."
        return
    fi
    echo "Starting Customer App on port 3000..."
    cd frontend/customer-app && npm run dev &
    if [ -d "../waiter-app" ]; then
        echo "Starting Waiter App on port 3001..."
        cd ../waiter-app && npm run dev &
    fi
    if [ -d "../chef-app" ]; then
        echo "Starting Chef App on port 3002..."
        cd ../chef-app && npm run dev &
    fi
    if [ -d "../admin-app" ]; then
        echo "Starting Admin App on port 3003..."
        cd ../admin-app && npm run dev &
    fi
    cd ../../..
    echo "✓ Frontend dev startup complete"
}

# Build frontend for production
function frontend_build() {
    if [ ! -d "frontend/customer-app" ]; then
        echo "⚠ No frontend projects found. Skipping frontend build."
        return
    fi
    echo "Building Customer App..."
    cd frontend/customer-app && npm run build && cd ../..
    if [ -d "frontend/waiter-app" ]; then
        echo "Building Waiter App..."
        cd frontend/waiter-app && npm run build && cd ../..
    fi
    if [ -d "frontend/chef-app" ]; then
        echo "Building Chef App..."
        cd frontend/chef-app && npm run build && cd ../..
    fi
    if [ -d "frontend/admin-app" ]; then
        echo "Building Admin App..."
        cd frontend/admin-app && npm run build && cd ../..
    fi
    echo "✓ Frontend build complete"
}

# ============================================
# 5. FULL SETUP COMMANDS
# ============================================

# Setup everything from scratch
function setup_all() {
    echo "🚀 Setting up Restaurant OS..."
    echo ""
    
    # Backend
    echo "1. Setting up backend..."
    backend_install
    
    # Frontend (optional)
    echo ""
    echo "2. Setting up frontend (if available)..."
    frontend_install
    
    # Docker
    echo ""
    echo "3. Starting Docker services..."
    start_docker
    
    sleep 5
    
    echo ""
    echo "✓ Setup complete!"
    echo ""
    echo "Available endpoints:"
    echo "  • API: http://localhost:8000/docs"
    echo "  • Customer: http://localhost:3000"
    echo "  • Waiter: http://localhost:3001"
    echo "  • Chef: http://localhost:3002"
    echo "  • Admin: http://localhost:3003"
}

# Clean everything
function clean_all() {
    read -p "Delete all containers, volumes, and data? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v
        rm -rf data/postgres data/redis
        rm -rf backend/app/logs
        echo "✓ Cleaned"
    fi
}

# ============================================
# 6. UTILITY COMMANDS
# ============================================

# Show service status
function status() {
    docker-compose ps
}

# Show system stats
function stats() {
    docker stats
}

# View environment
function show_env() {
    echo "Backend environment:"
    grep -v '^#' backend/.env | grep -v '^$'
}

# ============================================
# 7. DEVELOPMENT HELPERS
# ============================================

# Create new API endpoint template
function create_endpoint() {
    if [ -z "$1" ]; then
        echo "Usage: create_endpoint <name>"
        echo "Example: create_endpoint menu"
        return 1
    fi
    
    ENDPOINT_FILE="backend/app/api/v1/endpoints/${1}.py"
    
    cat > "$ENDPOINT_FILE" << 'EOF'
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.tenancy import User

router = APIRouter(prefix="/REPLACE_ME", tags=["REPLACE_ME"])

@router.get("/")
async def list_items(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all items"""
    # TODO: Implement
    return {"items": []}

@router.post("/")
async def create_item(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new item"""
    # TODO: Implement
    return {"status": "ok"}

@router.get("/{item_id}")
async def get_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get item by ID"""
    # TODO: Implement
    return {"id": item_id}

@router.put("/{item_id}")
async def update_item(
    item_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update item"""
    # TODO: Implement
    return {"id": item_id}

@router.delete("/{item_id}")
async def delete_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete item"""
    # TODO: Implement
    return {"status": "deleted"}
EOF
    
    echo "✓ Created: $ENDPOINT_FILE"
    echo "TODO: Update the endpoint name and implementation"
}

# ============================================
# 8. PRINT HELP
# ============================================

function help() {
    cat << 'EOF'
Restaurant OS - Development Commands

DOCKER:
  start_docker              Start all services
  stop_docker               Stop all services
  logs_backend              View backend logs
  logs_database             View database logs
  restart_backend           Restart backend
  status                    Show service status
  stats                     Show resource usage

DATABASE:
  db_shell                  Connect to PostgreSQL
  db_backup                 Backup database
  db_reset                  Reset database (WARNING!)

BACKEND:
  backend_install           Install dependencies
  backend_dev               Run backend locally
  backend_test              Run tests

FRONTEND:
  frontend_install          Install all frontend apps
  frontend_dev              Start all frontend apps
  frontend_build            Build for production

SETUP & CLEANUP:
  setup_all                 Setup everything
  clean_all                 Remove everything

UTILITIES:
  show_env                  Show environment variables
  create_endpoint <name>    Create new endpoint template

HELP:
  help                      Show this message

USAGE:
  source helpers.sh
  start_docker
  backend_dev

EOF
}

# Auto-run help if sourced with no arguments
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    help
fi
