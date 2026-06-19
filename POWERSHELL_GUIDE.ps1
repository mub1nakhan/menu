# Restaurant OS - PowerShell Setup Guide for Windows

# ============================================
# SETUP ON WINDOWS 10/11 WITH POWERSHELL
# ============================================

# 1. INSTALL REQUIRED TOOLS
# ============================================

# Install Docker Desktop
# https://www.docker.com/products/docker-desktop
# Make sure it's running before continuing

# Install Node.js (includes npm)
# https://nodejs.org/

# Verify installations
docker --version
docker-compose --version
node --version
npm --version
python --version

# 2. NAVIGATE TO PROJECT
# ============================================

cd "c:\Users\45\Desktop\loyihalar\menu"

# Check project structure
dir

# List all files
ls -Recurse | Select-Object FullName

# 3. START DOCKER SERVICES
# ============================================

# Start all services
docker-compose up -d

# Wait for services to initialize
Start-Sleep -Seconds 10

# Check if services are running
docker-compose ps

# View service logs
docker-compose logs

# 4. VIEW API DOCUMENTATION
# ============================================

# Test health endpoint
curl http://localhost:8000/health

# Or open in browser:
# http://localhost:8000/docs

# 5. DATABASE CONNECTION
# ============================================

# Connect to PostgreSQL
docker-compose exec postgres psql -U restaurant -d restaurant_os

# Common SQL queries:
# SELECT * FROM restaurants;
# SELECT * FROM users;
# SELECT * FROM products;
# \dt                    - List tables
# \q                     - Quit

# Export database
docker-compose exec -T postgres pg_dump -U restaurant restaurant_os | Out-File backup.sql

# 6. BACKEND SETUP (LOCAL DEVELOPMENT)
# ============================================

# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install dependencies
pip install -r requirements-backend.txt

# Run backend locally
uvicorn app.main:app --reload

# Backend will be available at: http://localhost:8000

# 7. FRONTEND SETUP (LOCAL DEVELOPMENT)
# ============================================

# Go back to project root
cd ..

# Install Customer App
cd frontend\customer-app
npm install
npm run dev
# Available at: http://localhost:3000

# In another PowerShell window, install Waiter App
cd frontend\waiter-app
npm install
npm run dev
# Available at: http://localhost:3001

# In another PowerShell window, install Chef App
cd frontend\chef-app
npm install
npm run dev
# Available at: http://localhost:3002

# In another PowerShell window, install Admin App
cd frontend\admin-app
npm install
npm run dev
# Available at: http://localhost:3003

# 8. VIEWING LOGS
# ============================================

# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs postgres
docker-compose logs redis

# Follow logs in real-time (-f flag)
docker-compose logs -f backend

# Show last 50 lines
docker-compose logs --tail=50 backend

# 9. CONTAINER MANAGEMENT
# ============================================

# List running containers
docker-compose ps

# Stop all containers
docker-compose stop

# Start all containers
docker-compose start

# Restart a service
docker-compose restart backend
docker-compose restart postgres

# Stop and remove containers
docker-compose down

# Stop and remove everything (including volumes)
docker-compose down -v

# 10. DATABASE BACKUP & RESTORE
# ============================================

# Create backup
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
docker-compose exec -T postgres pg_dump -U restaurant restaurant_os | Out-File "backup_$timestamp.sql"

# Restore from backup
Get-Content backup.sql | docker-compose exec -T postgres psql -U restaurant restaurant_os

# 11. TESTING
# ============================================

# Run backend tests
docker-compose exec backend pytest app/tests/ -v

# Or run locally (after backend_venv activation)
cd backend
pytest app/tests/ -v

# 12. ENVIRONMENT CONFIGURATION
# ============================================

# Copy environment template
Copy-Item backend\.env.example backend\.env

# Edit .env file (opens in Notepad)
notepad backend\.env

# View .env file
Get-Content backend\.env | Select-String -NotMatch "^#|^$"

# 13. FILE OPERATIONS
# ============================================

# List files in directory
ls

# List files with details
ls -Detail

# Create new directory
mkdir new_folder

# Copy file
Copy-Item source.txt destination.txt

# Move file
Move-Item old_path new_path

# Delete file
Remove-Item filename

# Delete directory
Remove-Item -Recurse directory_name

# Search files
Get-ChildItem -Path . -Filter *.py -Recurse

# Search in files
Select-String -Path "*.py" -Pattern "search_term"

# 14. USEFUL POWERSHELL COMMANDS
# ============================================

# Current directory
Get-Location

# Current user
$env:USERNAME

# System info
systeminfo

# Network info
ipconfig

# Process list
Get-Process

# Kill process
Stop-Process -Name ProcessName

# Task Manager
taskmgr

# 15. TROUBLESHOOTING
# ============================================

# Docker not starting
# 1. Ensure Docker Desktop is running
# 2. Check: docker ps

# Port already in use
# Kill process: Get-NetTcpConnection -LocalPort 8000 | Stop-Process -Force

# Database connection failed
docker-compose restart postgres
docker-compose logs postgres

# Backend not starting
docker-compose logs backend
docker-compose logs -f backend

# Reset everything
docker-compose down -v
Remove-Item -Recurse data
docker-compose up -d

# 16. GIT OPERATIONS
# ============================================

# Initialize git repository
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial commit"

# View status
git status

# View log
git log --oneline

# Create branch
git checkout -b feature-name

# Switch branch
git checkout branch-name

# Push to remote
git push origin main

# 17. USEFUL SHORTCUTS FOR POWERSHELL
# ============================================

# Create function in profile
$PROFILE

# Edit profile (create if not exists)
if (!(Test-Path -Path $PROFILE)) {
    New-Item -ItemType File -Path $PROFILE -Force
}
notepad $PROFILE

# Add these to profile for easy access:

# function docker_up { docker-compose up -d }
# function docker_down { docker-compose down -v }
# function docker_logs { docker-compose logs -f }
# function backend_dev { 
#     cd backend
#     .\venv\Scripts\Activate.ps1
#     uvicorn app.main:app --reload
# }
# function db_shell { docker-compose exec postgres psql -U restaurant -d restaurant_os }

# 18. QUICK REFERENCE
# ============================================

# Docker Compose Port Mapping:
# Backend:      http://localhost:8000
# API Docs:     http://localhost:8000/docs
# Customer App: http://localhost:3000
# Waiter App:   http://localhost:3001
# Chef App:     http://localhost:3002
# Admin App:    http://localhost:3003
# PostgreSQL:   localhost:5432
# Redis:        localhost:6379

# Database Credentials:
# Username: restaurant
# Password: restaurant (from .env)
# Database: restaurant_os

# 19. NEXT STEPS
# ============================================

<#
1. Install Docker Desktop
   https://www.docker.com/products/docker-desktop

2. Install Node.js
   https://nodejs.org/

3. Navigate to project:
   cd c:\Users\45\Desktop\loyihalar\menu

4. Start services:
   docker-compose up -d

5. Wait 10 seconds, then:
   docker-compose ps

6. Open browser:
   http://localhost:8000/docs

7. Read documentation:
   - README.md
   - IMPLEMENTATION_GUIDE.md
   - API_DOCUMENTATION.md

8. Start development!
#>

# 20. COMMON ERRORS & SOLUTIONS
# ============================================

<#
ERROR: "Cannot find Docker"
SOLUTION: Install Docker Desktop and restart PowerShell

ERROR: "Port 8000 already in use"
SOLUTION: 
  Get-NetTcpConnection -LocalPort 8000 | Stop-Process -Force
  docker-compose restart

ERROR: "Database connection refused"
SOLUTION: 
  docker-compose restart postgres
  docker-compose logs postgres

ERROR: "Cannot activate venv"
SOLUTION: 
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  Then try: .\venv\Scripts\Activate.ps1

ERROR: "npm command not found"
SOLUTION: 
  Install Node.js from https://nodejs.org/
  Restart PowerShell

ERROR: "git command not found"
SOLUTION: 
  Install Git for Windows
  https://git-scm.com/download/win
#>

