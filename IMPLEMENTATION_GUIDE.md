# Restaurant OS - Complete Implementation & Deployment Guide

## Table of Contents
1. [Quick Start](#quick-start)
2. [System Architecture](#system-architecture)
3. [Installation & Setup](#installation--setup)
4. [Database Setup](#database-setup)
5. [Backend Development](#backend-development)
6. [Frontend Development](#frontend-development)
7. [Docker Deployment](#docker-deployment)
8. [Production Deployment](#production-deployment)
9. [Inventory System Details](#inventory-system-details)
10. [Multi-Tenant Design](#multi-tenant-design)
11. [Security Model & RBAC](#security-model--rbac)
12. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Quick Start

### Prerequisites
- Node.js 18+ & npm 9+
- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Docker & Docker Compose (optional)

### 30-Second Start with Docker
```bash
# Clone the repo
git clone <repo-url>
cd menu

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local

# Start everything
docker-compose up

# Access applications
# Customer App: http://localhost:3000
# Waiter App: http://localhost:3001
# Chef App: http://localhost:3002
# Admin App: http://localhost:3003
# API: http://localhost:8000
```

---

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│           RESTAURANT OS ECOSYSTEM                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │Customer  │  │Waiter    │  │Chef      │         │
│  │App       │  │App       │  │App       │         │
│  │(3000)    │  │(3001)    │  │(3002)    │         │
│  └──────────┘  └──────────┘  └──────────┘         │
│        │              │              │             │
│        └──────────────┼──────────────┘             │
│                       │                            │
│  ┌──────────┐         │                            │
│  │Admin     │◄────────┤                            │
│  │App       │         │                            │
│  │(3003)    │         │                            │
│  └──────────┘         │                            │
│                       │                            │
│  ┌────────────────────┼────────────────┐          │
│  │   FastAPI Backend (8000)           │          │
│  │  - REST API endpoints              │          │
│  │  - WebSocket (KDS)                 │          │
│  │  - Business Logic                  │          │
│  │  - Authentication                  │          │
│  └────────────────────┬────────────────┘          │
│                       │                            │
│  ┌────────────────────┼───────────────┐           │
│  │                    │               │           │
│  │ PostgreSQL    Redis Cache    Stripe│           │
│  │ (5432)        (6379)         API   │           │
│  │                                    │           │
│  └────────────────────┬────────────────┘          │
│                       │                            │
│              ┌────────┴────────┐                  │
│              │   Data Layer    │                  │
│              │   (18 tables)   │                  │
│              └─────────────────┘                  │
│                                                   │
└─────────────────────────────────────────────────────┘
```

---

## Installation & Setup

### 1. Clone & Setup Repository
```bash
# Clone repository
git clone <repository-url>
cd menu

# Create directory structure
mkdir -p frontend/customer-app frontend/waiter-app frontend/chef-app frontend/admin-app
mkdir -p backend logs

# Copy environment templates
cp backend/.env.example backend/.env
cp .env.example .env
```

### 2. Backend Setup

#### Install dependencies
```bash
cd backend
pip install -r requirements-backend.txt
```

#### Configure environment
```bash
# Edit backend/.env
nano .env
```

#### Key variables to set:
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/restaurant_os
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=<generate-strong-secret>
JWT_SECRET=<generate-strong-jwt-secret>
STRIPE_SECRET_KEY=<your-stripe-key>
```

### 3. Frontend Setup

Each frontend app follows the same setup:

```bash
cd frontend/customer-app

# Install dependencies
npm install

# Copy environment
cp .env.local.example .env.local

# Configure API endpoint
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" >> .env.local

# Run development server
npm run dev
```

Repeat for waiter-app, chef-app, and admin-app on ports 3001, 3002, 3003.

---

## Database Setup

### Option 1: PostgreSQL Docker
```bash
docker run -d \
  --name restaurant_db \
  -e POSTGRES_USER=restaurant_user \
  -e POSTGRES_PASSWORD=restaurant_password \
  -e POSTGRES_DB=restaurant_os \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:15-alpine
```

### Option 2: Docker Compose
```bash
docker-compose up -d postgres redis
```

### Initialize Schema
```bash
# Load SQL schema
psql -U restaurant_user -d restaurant_os -h localhost -f DATABASE_SCHEMA.sql

# Or using Docker
docker exec -i restaurant_db psql -U restaurant_user -d restaurant_os < DATABASE_SCHEMA.sql
```

### Verify Installation
```bash
# Connect to PostgreSQL
psql -U restaurant_user -h localhost -d restaurant_os

# Check tables
\dt

# Check views
\dv

# Verify indexes
\di
```

---

## Backend Development

### Run Development Server
```bash
cd backend

# Activate virtual environment (if using venv)
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Start server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Access API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI: http://localhost:8000/openapi.json

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

### Create Migrations (Alembic)
```bash
# Generate new migration
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Frontend Development

### Run All Frontend Apps

```bash
# Terminal 1: Customer App
cd frontend/customer-app
npm run dev

# Terminal 2: Waiter App
cd frontend/waiter-app
npm run dev

# Terminal 3: Chef App
cd frontend/chef-app
npm run dev

# Terminal 4: Admin App
cd frontend/admin-app
npm run dev
```

Or use concurrently:
```bash
npm run dev:all
```

### Development Workflow

#### Customer App
- http://localhost:3000
- Test QR code scanning
- Test cart functionality
- Test real-time order tracking

#### Waiter App
- http://localhost:3001
- Test PIN login
- Test table management
- Test order creation

#### Chef App
- http://localhost:3002
- Test WebSocket connections
- Test order updates
- Test status changes

#### Admin App
- http://localhost:3003
- Test dashboard
- Test menu management
- Test analytics

---

## Docker Deployment

### Build Images
```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build backend
docker-compose build customer_app
```

### Start Services
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### Verify Services
```bash
# Check running containers
docker ps

# Check API health
curl http://localhost:8000/health

# Check PostgreSQL
docker exec restaurant_db psql -U restaurant_user -d restaurant_os -c "SELECT version();"

# Check Redis
docker exec restaurant_cache redis-cli ping
```

### Database Operations in Docker
```bash
# Create backup
docker exec restaurant_db pg_dump -U restaurant_user restaurant_os > backup.sql

# Restore backup
docker exec -i restaurant_db psql -U restaurant_user restaurant_os < backup.sql

# Connect to database
docker exec -it restaurant_db psql -U restaurant_user -d restaurant_os
```

---

## Production Deployment

### Pre-Deployment Checklist

```bash
# 1. Generate strong secrets
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 2. Test all environment variables
# 3. Run full test suite
pytest --cov=app

# 4. Build for production
docker-compose -f docker-compose.prod.yml build

# 5. Check Docker images
docker images | grep restaurant
```

### Deployment Steps

```bash
# 1. Push to production server
git push production main

# 2. SSH into server
ssh user@production-server

# 3. Pull latest code
git pull origin main

# 4. Update environment
nano .env

# 5. Start services
docker-compose -f docker-compose.prod.yml up -d

# 6. Verify services
docker-compose -f docker-compose.prod.yml logs

# 7. Run migrations
docker-compose exec backend alembic upgrade head

# 8. Create backup
docker exec restaurant_db pg_dump -U restaurant_user restaurant_os > backup_prod.sql
```

### SSL/TLS Setup
```bash
# Generate SSL certificates (Let's Encrypt)
certbot certonly --standalone -d api.restaurantos.com

# Update nginx config to use SSL
# Restart nginx
docker-compose restart nginx
```

### Monitoring

```bash
# Check service health
curl https://api.restaurantos.com/health

# View logs
docker-compose logs --tail=100 backend

# Monitor resources
docker stats

# Check disk space
docker exec restaurant_db df -h
```

---

## Inventory System Details

### How It Works

**1. Bill of Materials (BOM) - Recipes**
```
Burger (Product)
  ├─ Meat: 100g
  ├─ Bread: 1 piece
  ├─ Cheese: 20g
  ├─ Sauce: 15g
  └─ Lettuce: 50g
```

**2. Stock Tracking**
- Each branch has independent stock levels
- Tracks available + reserved quantities
- Automatic deduction on order placement
- Manual adjustments for waste/corrections

**3. Deduction Flow**
```
Order Created
  ↓
Check Recipe Ingredients
  ↓
Reserve Inventory
  ↓
Order Confirmed
  ↓
Mark Reserved as "Out"
  ↓
Update Stock
```

**4. Waste Tracking**
```
INSERT INTO inventory_movements
VALUES (
  ingredient_id,
  'waste',
  quantity,
  'spoilage',
  recorded_by_user,
  'Expired products'
);
```

**5. Alerts**
```sql
-- Low stock alert
SELECT * FROM v_inventory_alerts
WHERE alert_status IN ('reorder', 'out_of_stock');
```

### Implementation Examples

**Create Recipe**
```python
# API call to set recipe
POST /inventory/recipes
{
  "product_id": "burger-001",
  "ingredients": [
    {"ingredient_id": "meat-001", "quantity": 0.1},
    {"ingredient_id": "bread-001", "quantity": 1},
    {"ingredient_id": "cheese-001", "quantity": 0.02}
  ]
}
```

**Deduct Inventory on Order**
```python
async def create_order(order_items):
    for item in order_items:
        # Get recipe
        recipe = await get_recipe(item.product_id)
        
        # Deduct each ingredient
        for ingredient in recipe.ingredients:
            inventory = await get_inventory(
                item.restaurant_id,
                item.branch_id,
                ingredient.ingredient_id
            )
            
            # Calculate needed quantity
            needed = ingredient.quantity * item.quantity
            
            # Update inventory
            inventory.reserved += needed
            
            # Log movement
            await log_movement(
                ingredient_id=ingredient.ingredient_id,
                type='out',
                quantity=needed,
                reference_id=order.id
            )
```

---

## Multi-Tenant Design

### Tenant Isolation Strategy

**1. Database Level**
- All tables have `restaurant_id` foreign key
- All queries filter by `restaurant_id`
- No shared data between restaurants

**2. API Level**
```python
# Middleware checks tenant context
async def tenant_middleware(request, call_next):
    token = extract_jwt(request)
    restaurant_id = token.get('restaurant_id')
    
    # Set context for entire request
    set_tenant_context(restaurant_id)
    
    # All queries use this context
    response = await call_next(request)
    return response
```

**3. Query Example**
```python
# Every query includes restaurant_id filter
orders = await db.execute(
    select(Order)
    .where(Order.restaurant_id == current_user.restaurant_id)
    .where(Order.branch_id == current_user.branch_id)
)
```

**4. Data Isolation Tests**
```python
# Test that data from Restaurant A cannot be seen by Restaurant B
async def test_tenant_isolation():
    user_a = await create_user(restaurant_id=A)
    user_b = await create_user(restaurant_id=B)
    
    # User A creates order
    order_a = await create_order(user_a)
    
    # User B should not see order_a
    orders_b = await get_orders(user_b)
    assert order_a not in orders_b
```

---

## Security Model & RBAC

### Role Definitions

```
1. SUPER_ADMIN
   - Permissions: ["*"]
   - Can: Manage all restaurants, users, settings

2. OWNER (Per Restaurant)
   - Permissions: ["orders:create", "orders:read", "menu:manage", "staff:manage"]
   - Can: Manage everything in their restaurant

3. BRANCH_MANAGER
   - Permissions: ["orders:read", "inventory:read", "staff:read"]
   - Can: Manage branch operations

4. WAITER
   - Permissions: ["orders:create", "orders:read"]
   - Can: Create and view orders

5. CHEF
   - Permissions: ["orders:read", "orders:update"]
   - Can: View and update order status

6. CASHIER
   - Permissions: ["orders:read", "payments:create"]
   - Can: Process payments
```

### Permission Checking

```python
# Decorator for permission checking
@require_permission("orders:create")
async def create_order(order_data, current_user):
    # Check permission
    if "orders:create" not in current_user.role.permissions:
        raise HTTPException(403, "Insufficient permissions")
    
    # Process order
    return await order_service.create(order_data)
```

### Password Security

```python
# Passwords are hashed with bcrypt
password_hash = hash_password("user_password")

# PIN codes for quick login
pin_hash = hash_password("1234")

# Verify during login
if verify_password(input_password, stored_hash):
    # Grant access
    pass
```

---

## Monitoring & Maintenance

### Daily Maintenance Tasks

```bash
# 1. Check service health
curl http://localhost:8000/health

# 2. Review error logs
docker-compose logs --since 24h backend | grep ERROR

# 3. Check database size
docker exec restaurant_db psql -U restaurant_user -d restaurant_os -c \
  "SELECT pg_size_pretty(pg_database_size('restaurant_os'));"

# 4. Backup database
docker exec restaurant_db pg_dump -U restaurant_user restaurant_os | \
  gzip > backups/daily_$(date +%Y%m%d).sql.gz

# 5. Check disk usage
df -h

# 6. Monitor memory/CPU
docker stats
```

### Weekly Tasks

```bash
# 1. Review analytics data
# 2. Check waste tracking report
# 3. Verify inventory accuracy
# 4. Review staff performance
# 5. Check for failed payments
# 6. Generate sales reports
```

### Monthly Tasks

```bash
# 1. Analyze sales trends
# 2. Optimize slow queries
# 3. Review and update database indexes
# 4. Audit access logs
# 5. Update dependencies
# 6. Plan capacity upgrades
```

### Performance Optimization

```sql
-- Analyze slow queries
EXPLAIN ANALYZE SELECT * FROM orders WHERE created_at > NOW() - INTERVAL '1 day';

-- Vacuum and analyze
VACUUM ANALYZE;

-- Check index usage
SELECT * FROM pg_stat_user_indexes;

-- Find missing indexes
SELECT * FROM pg_stat_user_tables WHERE seq_scan > 100;
```

### Scaling Strategies

**Horizontal Scaling**
- Multiple backend instances behind load balancer
- Database read replicas
- Separate WebSocket servers

**Vertical Scaling**
- Increase server resources
- Optimize database queries
- Cache frequently accessed data

**Database Optimization**
- Partitioning by date for analytics tables
- Connection pooling (PgBouncer)
- Query optimization

---

## Support & Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Check connection string
echo $DATABASE_URL

# Test connection
psql -U restaurant_user -h localhost -d restaurant_os
```

**WebSocket Connection Failed**
```bash
# Check WebSocket URL
echo $NEXT_PUBLIC_WS_URL

# Check firewall
sudo ufw allow 8000

# Check CORS headers
curl -i http://localhost:8000/health
```

**Out of Memory**
```bash
# Check memory usage
docker stats

# Increase Redis memory limit
redis-cli CONFIG SET maxmemory 2gb

# Clear Redis cache
redis-cli FLUSHALL
```

---

## Scaling to 10,000+ Restaurants

### Architecture for Scale

1. **Database Clustering**
   - Multi-node PostgreSQL cluster
   - Read replicas in different regions

2. **Caching Layer**
   - Redis cluster for session management
   - CDN for static assets

3. **API Server Pool**
   - Kubernetes cluster
   - Auto-scaling based on load

4. **Message Queue**
   - Use RabbitMQ/Kafka for async tasks
   - Background job processing

5. **Analytics**
   - Time-series database (InfluxDB)
   - Separate analytics replica

---

