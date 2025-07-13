@echo off
echo Starting Recruitment System Microservices...
echo.

REM Set the Python path to include the project root
set PYTHONPATH=%cd%

echo Starting Discovery Service...
start "Discovery Service" cmd /k "python -m discovery_service.main"

echo Starting Config Service...
start "Config Service" cmd /k "python -m config_service.main"

echo Starting Auth Service...
start "Auth Service" cmd /k "python -m auth_service.main"

echo Starting Registration Service...
start "Registration Service" cmd /k "python -m registration_service.main"

echo Starting Job Application Service...
start "Job Application Service" cmd /k "python -m job_application_service.main"

echo Starting Edge Service...
start "Edge Service" cmd /k "python -m edge_service.main"

echo.
echo All services are starting...
echo.
echo Service URLs:
echo - Discovery Service: http://localhost:9090
echo - Config Service: http://localhost:9999
echo - Auth Service: http://localhost:8081
echo - Registration Service: http://localhost:8888
echo - Job Application Service: http://localhost:8082
echo - Edge Service (API Gateway): http://localhost:8080
echo - Consul UI: http://localhost:8500
echo.
echo Press any key to exit this window...
pause > nul 