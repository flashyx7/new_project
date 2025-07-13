@echo off
echo 🗄️ Setting up MySQL Database for Recruitment System
echo ============================================================

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Docker is not installed or not in PATH
    echo Please install Docker Desktop from https://docker.com
    pause
    exit /b 1
)

REM Start MySQL container
echo Starting MySQL container...
docker run -d --name mysql-recruitment ^
    -e MYSQL_ROOT_PASSWORD=rootpassword ^
    -e MYSQL_DATABASE=recruitment_system ^
    -e MYSQL_USER=recruitment_user ^
    -e MYSQL_PASSWORD=recruitment_pass ^
    -p 3306:3306 ^
    mysql:8.0 --default-authentication-plugin=mysql_native_password

REM Wait for MySQL to start
echo Waiting for MySQL to start...
timeout /t 10 /nobreak >nul

REM Initialize database schema
echo Initializing database schema...
mysql -h localhost -P 3306 -u recruitment_user -precruitment_pass recruitment_system < docs\db\mysql\schema.sql

REM Load sample data
echo Loading sample data...
mysql -h localhost -P 3306 -u recruitment_user -precruitment_pass recruitment_system < docs\db\mysql\data.sql

echo ✅ Database setup completed!
echo MySQL is running on localhost:3306
echo Database: recruitment_system
echo User: recruitment_user
echo Password: recruitment_pass
pause 