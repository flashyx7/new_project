@echo off
echo 🔍 Starting Consul for Service Discovery
echo ============================================================

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Docker is not installed or not in PATH
    echo Please install Docker Desktop from https://docker.com
    pause
    exit /b 1
)

REM Start Consul container
echo Starting Consul container...
docker run -d --name consul-recruitment ^
    -p 8500:8500 ^
    -p 8600:8600/udp ^
    consul:1.15 agent -server -bootstrap-expect=1 -ui -client=0.0.0.0

echo ✅ Consul started successfully!
echo Consul UI is available at: http://localhost:8500
echo Consul API is available at: http://localhost:8500/v1
pause 