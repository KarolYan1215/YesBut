@echo off
REM YesBut Production Deployment Script for Windows
REM Usage: deploy.bat [start|stop|restart|logs|status]

setlocal enabledelayedexpansion

set COMPOSE_FILE=docker-compose.prod.yml
set PROJECT_NAME=yesbut

REM Check if .env exists
if not exist .env (
    echo [ERROR] .env file not found!
    echo Please copy .env.example to .env and configure it.
    echo   copy .env.example .env
    exit /b 1
)

REM Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed or not running!
    echo Please install Docker Desktop and start it.
    exit /b 1
)

REM Parse command
set CMD=%1
if "%CMD%"=="" set CMD=start

if "%CMD%"=="start" goto :start
if "%CMD%"=="stop" goto :stop
if "%CMD%"=="restart" goto :restart
if "%CMD%"=="logs" goto :logs
if "%CMD%"=="status" goto :status
if "%CMD%"=="build" goto :build
if "%CMD%"=="clean" goto :clean
goto :usage

:start
echo [INFO] Starting YesBut services...
docker-compose -f %COMPOSE_FILE% -p %PROJECT_NAME% up -d
echo.
echo [INFO] Services started! Access:
echo   Frontend: http://localhost:3000
echo   Backend API: http://localhost:8001
echo   API Docs: http://localhost:8001/docs
goto :end

:stop
echo [INFO] Stopping YesBut services...
docker-compose -f %COMPOSE_FILE% -p %PROJECT_NAME% down
goto :end

:restart
echo [INFO] Restarting YesBut services...
docker-compose -f %COMPOSE_FILE% -p %PROJECT_NAME% down
docker-compose -f %COMPOSE_FILE% -p %PROJECT_NAME% up -d
goto :end

:logs
echo [INFO] Showing logs (Ctrl+C to exit)...
docker-compose -f %COMPOSE_FILE% -p %PROJECT_NAME% logs -f
goto :end

:status
echo [INFO] Service status:
docker-compose -f %COMPOSE_FILE% -p %PROJECT_NAME% ps
goto :end

:build
echo [INFO] Building images...
docker-compose -f %COMPOSE_FILE% -p %PROJECT_NAME% build --no-cache
goto :end

:clean
echo [INFO] Cleaning up...
docker-compose -f %COMPOSE_FILE% -p %PROJECT_NAME% down -v --rmi local
goto :end

:usage
echo Usage: deploy.bat [command]
echo.
echo Commands:
echo   start    - Start all services (default)
echo   stop     - Stop all services
echo   restart  - Restart all services
echo   logs     - Show service logs
echo   status   - Show service status
echo   build    - Rebuild images
echo   clean    - Stop and remove all containers, volumes, images
goto :end

:end
endlocal
