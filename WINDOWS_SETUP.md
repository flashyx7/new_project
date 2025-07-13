# Windows Setup Guide for Recruitment System Python Microservices

This guide will help you set up and run the Python microservices on Windows.

## Prerequisites

### 1. Install Python 3.11+
- Download from: https://python.org/downloads/
- Make sure to check "Add Python to PATH" during installation
- Verify installation: `python --version`

### 2. Install Docker Desktop
- Download from: https://docker.com/products/docker-desktop/
- Install and start Docker Desktop
- Verify installation: `docker --version`

### 3. Install MySQL Client (Optional)
- Download MySQL Workbench or MySQL Command Line Client
- Or use the MySQL client that comes with XAMPP/WAMP

## Quick Start (Recommended)

### Option 1: Using Docker Compose (Easiest)

1. **Open Command Prompt or PowerShell in the project directory**

2. **Start all services:**
   ```cmd
   docker-compose up -d
   ```

3. **Check service status:**
   ```cmd
   docker-compose ps
   ```

4. **View logs:**
   ```cmd
   docker-compose logs -f [service-name]
   ```

### Option 2: Using Batch Scripts

1. **Set up database:**
   ```cmd
   setup_database.bat
   ```

2. **Start Consul:**
   ```cmd
   start_consul.bat
   ```

3. **Start all services:**
   ```cmd
   start_services.bat
   ```

### Option 3: Manual Setup

1. **Install Python dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```

2. **Start MySQL with Docker:**
   ```cmd
   docker run -d --name mysql-recruitment -e MYSQL_ROOT_PASSWORD=rootpassword -e MYSQL_DATABASE=recruitment_system -e MYSQL_USER=recruitment_user -e MYSQL_PASSWORD=recruitment_pass -p 3306:3306 mysql:8.0 --default-authentication-plugin=mysql_native_password
   ```

3. **Wait for MySQL to start (10 seconds), then initialize database:**
   ```cmd
   mysql -h localhost -P 3306 -u recruitment_user -precruitment_pass recruitment_system < docs\db\mysql\schema.sql
   mysql -h localhost -P 3306 -u recruitment_user -precruitment_pass recruitment_system < docs\db\mysql\data.sql
   ```

4. **Start Consul:**
   ```cmd
   docker run -d --name consul-recruitment -p 8500:8500 -p 8600:8600/udp consul:1.15 agent -server -bootstrap-expect=1 -ui -client=0.0.0.0
   ```

5. **Start all services:**
   ```cmd
   python start_services.py
   ```

## Service URLs

Once all services are running, you can access:

- **API Gateway:** http://localhost:8080
- **Discovery Service:** http://localhost:9090
- **Config Service:** http://localhost:9999
- **Auth Service:** http://localhost:8081
- **Registration Service:** http://localhost:8888
- **Job Application Service:** http://localhost:8082
- **Consul UI:** http://localhost:8500

## Testing the System

Run the test script to verify everything is working:

```cmd
python test_system.py
```

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
**Error:** `Port XXXX is already in use`

**Solution:**
```cmd
# Find process using the port
netstat -ano | findstr :8080

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

#### 2. Python Not Found
**Error:** `'python' is not recognized`

**Solution:**
- Make sure Python is installed and added to PATH
- Try using `python3` instead of `python`
- Restart Command Prompt after installing Python

#### 3. Docker Not Running
**Error:** `Cannot connect to the Docker daemon`

**Solution:**
- Start Docker Desktop
- Wait for Docker to fully initialize
- Restart Command Prompt

#### 4. MySQL Connection Issues
**Error:** `Can't connect to MySQL server`

**Solution:**
```cmd
# Check if MySQL container is running
docker ps

# If not running, start it
docker start mysql-recruitment

# Check MySQL logs
docker logs mysql-recruitment
```

#### 5. Permission Denied
**Error:** `Permission denied` when running scripts

**Solution:**
- Run Command Prompt as Administrator
- Or use PowerShell instead

#### 6. Module Import Errors
**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```cmd
# Install dependencies
pip install -r requirements.txt

# If that doesn't work, try:
pip install --user -r requirements.txt
```

#### 7. Consul Package Issues
**Error:** `ERROR: Could not find a version that satisfies the requirement consul==1.1.0`

**Solution:**
```cmd
# Install the correct consul package
pip install python-consul==1.1.0

# Or install all requirements again
pip install -r requirements.txt --force-reinstall
```

### Service-Specific Issues

#### Discovery Service Issues
```cmd
# Check if Consul is running
docker ps | findstr consul

# Restart Consul if needed
docker restart consul-recruitment
```

#### Database Issues
```cmd
# Check MySQL status
docker exec mysql-recruitment mysqladmin -u root -prootpassword ping

# Reset database if needed
docker stop mysql-recruitment
docker rm mysql-recruitment
setup_database.bat
```

#### Authentication Issues
- Make sure JWT_SECRET_KEY is set (default is used if not set)
- Check if user exists in database
- Verify password hashing is working

## Development Commands

### Starting Individual Services

```cmd
# Discovery Service
cd discovery_service
python main.py

# Config Service
cd config_service
python main.py

# Auth Service
cd auth_service
python main.py

# Registration Service
cd registration_service
python main.py

# Job Application Service
cd job_application_service
python main.py

# Edge Service
cd edge_service
python main.py
```

### Database Commands

```cmd
# Connect to MySQL
mysql -h localhost -P 3306 -u recruitment_user -precruitment_pass recruitment_system

# View tables
SHOW TABLES;

# View sample data
SELECT * FROM person LIMIT 5;
```

### Docker Commands

```cmd
# View all containers
docker ps -a

# View logs
docker logs <container-name>

# Stop all containers
docker stop $(docker ps -q)

# Remove all containers
docker rm $(docker ps -aq)

# Clean up volumes
docker volume prune
```

## Environment Variables

You can set these environment variables for customization:

```cmd
# Database
set DATABASE_URL=mysql+pymysql://user:password@host:port/database

# JWT
set JWT_SECRET_KEY=your-secret-key-here

# Consul
set CONSUL_HOST=localhost
set CONSUL_PORT=8500
```

## Stopping Services

### Docker Compose
```cmd
docker-compose down
```

### Individual Services
- Press `Ctrl+C` in each service terminal
- Or use the batch script which handles graceful shutdown

### All Docker Containers
```cmd
docker stop mysql-recruitment consul-recruitment
```

## Performance Tips

1. **Use SSD** for better Docker performance
2. **Allocate more memory** to Docker Desktop (4GB+ recommended)
3. **Use WSL2** backend for Docker Desktop
4. **Close unnecessary applications** to free up resources

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review service logs: `docker-compose logs [service-name]`
3. Verify all prerequisites are installed correctly
4. Try restarting Docker Desktop and Command Prompt
5. Check Windows Event Viewer for system errors

## Next Steps

Once the system is running:

1. **Explore the API:** Visit http://localhost:8080/docs for interactive API documentation
2. **Test user registration:** Use the test script or API endpoints
3. **Monitor services:** Use Consul UI at http://localhost:8500
4. **View logs:** Monitor service logs for debugging
5. **Customize:** Modify configuration and add new features 