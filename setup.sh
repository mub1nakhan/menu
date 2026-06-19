#!/bin/bash

# Restaurant OS - Complete Setup Script
# Run this in Git Bash or any bash terminal

echo "🚀 Restaurant OS - Setup Script"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. Check if Docker is installed
echo -e "${BLUE}[1/8] Checking Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker not found. Please install Docker first.${NC}"
    echo "Download from: https://www.docker.com/products/docker-desktop"
    exit 1
fi
echo -e "${GREEN}✓ Docker found${NC}"
echo ""

# 2. Check if Docker Compose is installed
echo -e "${BLUE}[2/8] Checking Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose not found. Please install it.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose found${NC}"
echo ""

# 3. Create .env file from template
echo -e "${BLUE}[3/8] Setting up environment variables...${NC}"
if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env
    echo -e "${GREEN}✓ Created backend/.env from template${NC}"
else
    echo -e "${YELLOW}⚠ backend/.env already exists, skipping${NC}"
fi
echo ""

# 4. Create necessary directories
echo -e "${BLUE}[4/8] Creating directories...${NC}"
mkdir -p backend/app/logs
mkdir -p data/postgres
mkdir -p data/redis
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# 5. Stop existing containers (if any)
echo -e "${BLUE}[5/8] Stopping existing containers...${NC}"
docker-compose down 2>/dev/null || true
echo -e "${GREEN}✓ Containers stopped${NC}"
echo ""

# 6. Build images
echo -e "${BLUE}[6/8] Building Docker images...${NC}"
docker-compose build
if [ $? -ne 0 ]; then
    echo -e "${RED}Error building images${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Images built successfully${NC}"
echo ""

# 7. Start containers
echo -e "${BLUE}[7/8] Starting containers...${NC}"
docker-compose up -d
if [ $? -ne 0 ]; then
    echo -e "${RED}Error starting containers${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Containers started${NC}"
echo ""

# 8. Wait for services to be ready
echo -e "${BLUE}[8/8] Waiting for services to be ready...${NC}"
sleep 10

# Check if backend is running
if docker-compose logs backend | grep -q "Uvicorn running"; then
    echo -e "${GREEN}✓ All services are running${NC}"
else
    echo -e "${YELLOW}⚠ Services starting, may take a moment...${NC}"
fi
echo ""

# Print summary
echo -e "${GREEN}=================================="
echo "🎉 Setup Complete!"
echo "==================================${NC}"
echo ""
echo -e "${BLUE}Services available at:${NC}"
echo "  • API (Swagger UI): http://localhost:8000/docs"
echo "  • PostgreSQL: localhost:5432"
echo "  • Redis: localhost:6379"
echo ""
echo -e "${BLUE}Useful commands:${NC}"
echo "  • View logs: docker-compose logs -f backend"
echo "  • Stop services: docker-compose down"
echo "  • Restart: docker-compose restart"
echo "  • Database shell: docker-compose exec postgres psql -U restaurant"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Open http://localhost:8000/docs to test API"
echo "  2. Read IMPLEMENTATION_GUIDE.md for more details"
echo "  3. Check API_DOCUMENTATION.md for endpoint reference"
echo ""
