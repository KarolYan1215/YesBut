# YesBut Quick Start Guide - Windows + Docker Desktop

## Prerequisites

1. **Docker Desktop for Windows**
   - Download: https://www.docker.com/products/docker-desktop/
   - Install and start Docker Desktop
   - Ensure WSL 2 backend is enabled (recommended)

2. **Anthropic API Key**
   - Get your key at: https://console.anthropic.com/
   - Required for AI agent functionality

## Quick Start (5 minutes)

### Step 1: Configure Environment

```powershell
# Open PowerShell in project directory
cd C:\Users\28129\Desktop\YesBut\yesbut

# Copy environment template
copy .env.production.example .env

# Edit .env file - REQUIRED changes:
# 1. Set POSTGRES_PASSWORD (any secure password)
# 2. Set REDIS_PASSWORD (any secure password)
# 3. Set SECRET_KEY (generate random string)
# 4. Set ANTHROPIC_API_KEY (your API key)
notepad .env
```

### Step 2: Start Services

```powershell
# Start all services
.\deploy.bat start

# Wait 1-2 minutes for first build
```

### Step 3: Access Application

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

## Common Commands

```powershell
# View logs
.\deploy.bat logs

# Check status
.\deploy.bat status

# Stop services
.\deploy.bat stop

# Restart services
.\deploy.bat restart

# Rebuild after code changes
.\deploy.bat build
.\deploy.bat start
```

## Troubleshooting

### Docker not starting
```powershell
# Check Docker status
docker info

# If error, restart Docker Desktop
```

### Port already in use
```powershell
# Check what's using port 3000
netstat -ano | findstr :3000

# Kill process (replace PID)
taskkill /PID <PID> /F
```

### Database connection error
```powershell
# Check if postgres is running
docker ps | findstr postgres

# View postgres logs
docker logs yesbut-postgres
```

### Build fails
```powershell
# Clean rebuild
.\deploy.bat clean
.\deploy.bat build
.\deploy.bat start
```

## Production Deployment Checklist

- [ ] Change all default passwords in .env
- [ ] Generate secure SECRET_KEY
- [ ] Set valid ANTHROPIC_API_KEY
- [ ] Configure CORS_ORIGINS for your domain
- [ ] Update NEXT_PUBLIC_API_URL for production domain
- [ ] Enable HTTPS (use reverse proxy like nginx)
- [ ] Set up database backups
- [ ] Configure monitoring/logging

## Architecture

```
                    ┌─────────────────┐
                    │   User Browser  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │    Frontend     │
                    │   (Next.js)     │
                    │   Port: 3000    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │    Backend      │
                    │   (FastAPI)     │
                    │   Port: 8001    │
                    └────────┬────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
    ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐
    │  PostgreSQL │   │    Redis    │   │  Anthropic  │
    │  Port: 5432 │   │  Port: 6379 │   │   Claude    │
    └─────────────┘   └─────────────┘   └─────────────┘
```

## Support

For issues, check:
1. Docker Desktop is running
2. All containers are healthy: `.\deploy.bat status`
3. Logs for errors: `.\deploy.bat logs`
