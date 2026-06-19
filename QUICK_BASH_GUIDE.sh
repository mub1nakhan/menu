#!/bin/bash

# Restaurant OS - Quick Start Guide for Windows Git Bash

# ============================================
# QUICK START - Run These First
# ============================================

# 1. Navigate to project folder
cd c:/Users/45/Desktop/loyihalar/menu

# 2. Check Docker is running
docker --version
docker-compose --version

# 3. Start all services with one command
docker-compose up -d

# 4. Wait 10 seconds for services to start
sleep 10

# 5. Check if services are running
docker-compose ps

# ============================================
# VIEW API DOCUMENTATION
# ============================================

# Open in browser:
# http://localhost:8000/docs

# Test API with curl:
curl http://localhost:8000/health

# ============================================
# INSTALL BACKEND LOCALLY (Optional)
# ============================================

# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate it (Git Bash)
source venv/Scripts/activate

# Install dependencies
pip install -r requirements-backend.txt

# Run backend directly
uvicorn app.main:app --reload

# ============================================
# INSTALL FRONTEND LOCALLY (Optional)
# ============================================

# Install all 4 apps
cd frontend/customer-app && npm install && cd ../..
cd frontend/waiter-app && npm install && cd ../..
cd frontend/chef-app && npm install && cd ../..
cd frontend/admin-app && npm install && cd ../..

# Run each app in separate terminal
cd frontend/customer-app && npm run dev   # Port 3000
cd frontend/waiter-app && npm run dev     # Port 3001
cd frontend/chef-app && npm run dev       # Port 3002
cd frontend/admin-app && npm run dev      # Port 3003

# ============================================
# DATABASE ACCESS
# ============================================

# Connect to PostgreSQL
docker-compose exec postgres psql -U restaurant -d restaurant_os

# Inside psql, useful commands:
# \dt                          - List all tables
# SELECT * FROM restaurants;   - View restaurants
# \q                          - Quit

# Export database
docker-compose exec -T postgres pg_dump -U restaurant restaurant_os > backup.sql

# Import database
docker-compose exec -T postgres psql -U restaurant restaurant_os < backup.sql

# ============================================
# BACKEND TESTING
# ============================================

# Run tests in Docker
docker-compose exec backend pytest app/tests/ -v

# Run tests locally
cd backend
pytest app/tests/ -v

# Run specific test
pytest app/tests/test_auth.py -v

# ============================================
# LOGS & DEBUGGING
# ============================================

# View logs from all services
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs postgres
docker-compose logs redis

# Follow logs in real-time
docker-compose logs -f backend

# View last 50 lines
docker-compose logs --tail=50 backend

# ============================================
# CONTAINER MANAGEMENT
# ============================================

# List all containers
docker-compose ps

# Stop all services
docker-compose stop

# Start all services
docker-compose start

# Restart a service
docker-compose restart backend
docker-compose restart postgres

# Stop and remove containers
docker-compose down

# Stop and remove everything including volumes
docker-compose down -v

# View container stats
docker stats

# Execute command in container
docker-compose exec backend ls -la

# View container logs
docker-compose logs backend

# ============================================
# PYTHON / BACKEND MANAGEMENT
# ============================================

# Check Python version
python --version

# Check pip packages
pip list

# Install new package
pip install package_name

# Freeze dependencies
pip freeze > requirements-backend.txt

# Install from requirements
pip install -r requirements-backend.txt

# ============================================
# NPM / FRONTEND MANAGEMENT
# ============================================

# Check Node version
node --version
npm --version

# Install dependencies
npm install

# Update all packages
npm update

# Add new package
npm install package_name

# Remove package
npm uninstall package_name

# ============================================
# GIT OPERATIONS (If Using Git)
# ============================================

# Initialize git
git init

# Add files
git add .

# Commit
git commit -m "Initial commit"

# View status
git status

# View log
git log --oneline

# ============================================
# USEFUL SHORTCUTS
# ============================================

# List directory contents
ls -la

# Change directory
cd /path/to/directory

# Create directory
mkdir new_folder

# Remove file
rm filename

# Remove directory
rm -rf directory_name

# Copy file
cp source destination

# Move file
mv source destination

# Find files
find . -name "*.py"

# Search in files
grep -r "search_term" .

# ============================================
# ENVIRONMENT SETUP
# ============================================

# Create .env file from template
cp backend/.env.example backend/.env

# Edit .env (with nano)
nano backend/.env

# Edit .env (with vi)
vi backend/.env

# View .env (without showing passwords)
grep -v "^#" backend/.env | grep -v "^$"

# ============================================
# SYSTEM INFORMATION
# ============================================

# Current directory
pwd

# Current user
whoami

# System info
uname -a

# Disk space
df -h

# Process list
ps aux

# ============================================
# NETWORKING
# ============================================

# Test port connectivity
netstat -an | grep 8000

# Kill process on port
lsof -ti:8000 | xargs kill -9

# DNS resolution
nslookup localhost

# Ping
ping localhost

# ============================================
# TROUBLESHOOTING
# ============================================

# Docker not found - Install Docker Desktop
# https://www.docker.com/products/docker-desktop

# Port already in use
docker-compose down -v
docker-compose up -d

# Database connection failed
docker-compose logs postgres
docker-compose restart postgres

# Backend errors
docker-compose logs backend
docker-compose logs -f backend

# Reset everything
docker-compose down -v
rm -rf data/
docker-compose up -d

# ============================================
# PERFORMANCE OPTIMIZATION
# ============================================

# Clean Docker system
docker system prune

# Remove unused volumes
docker volume prune

# Remove unused networks
docker network prune

# Check Docker disk usage
docker system df

# ============================================
# BACKUP & RESTORE
# ============================================

# Backup all data
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz data/

# Restore from backup
tar -xzf backup_20240101_120000.tar.gz

# ============================================
# USEFUL ALIASES (Add to ~/.bashrc)
# ============================================

# alias docker_up='docker-compose up -d'
# alias docker_down='docker-compose down'
# alias docker_logs='docker-compose logs -f'
# alias backend_dev='cd backend && uvicorn app.main:app --reload'
# alias db_shell='docker-compose exec postgres psql -U restaurant -d restaurant_os'

# ============================================
# NEXT STEPS
# ============================================

# 1. Run: docker-compose up -d
# 2. Open: http://localhost:8000/docs
# 3. Test API endpoints
# 4. Read: IMPLEMENTATION_GUIDE.md
# 5. Start development!

# ============================================
