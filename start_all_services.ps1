# PowerShell script to start all services for the Recruitment System
# This script checks dependencies, installs requirements, and starts all services

param(
    [switch]$SkipDependencyCheck,
    [switch]$SkipDatabaseSetup,
    [switch]$Verbose
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Function to write colored output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# Function to check if Python is installed
function Test-PythonInstallation {
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✓ Python found: $pythonVersion" "Green"
            return $true
        }
    }
    catch {
        Write-ColorOutput "✗ Python not found or not in PATH" "Red"
        return $false
    }
    return $false
}

# Function to check if pip is available
function Test-PipInstallation {
    try {
        $pipVersion = pip --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✓ pip found: $pipVersion" "Green"
            return $true
        }
    }
    catch {
        Write-ColorOutput "✗ pip not found" "Red"
        return $false
    }
    return $false
}

# Function to install Python dependencies
function Install-Dependencies {
    Write-ColorOutput "Installing Python dependencies..." "Yellow"
    
    try {
        # Upgrade pip first
        Write-ColorOutput "Upgrading pip..." "Cyan"
        python -m pip install --upgrade pip
        
        # Install requirements
        Write-ColorOutput "Installing requirements from requirements.txt..." "Cyan"
        pip install -r requirements.txt
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✓ Dependencies installed successfully" "Green"
            return $true
        } else {
            Write-ColorOutput "✗ Failed to install dependencies" "Red"
            return $false
        }
    }
    catch {
        Write-ColorOutput "✗ Error installing dependencies: $($_.Exception.Message)" "Red"
        return $false
    }
}

# Function to check if MySQL is running
function Test-MySQLConnection {
    Write-ColorOutput "Checking MySQL connection..." "Yellow"
    
    try {
        # Try to connect to MySQL using Python
        $testScript = @"
import pymysql
import os

try:
    connection = pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '3307')),
        user=os.getenv('DB_USER', 'recruitment_user'),
        password=os.getenv('DB_PASSWORD', 'recruitment_pass'),
        database=os.getenv('DB_NAME', 'recruitment_system')
    )
    connection.close()
    print("SUCCESS")
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)
"@
        
        $testScript | python
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✓ MySQL connection successful" "Green"
            return $true
        } else {
            Write-ColorOutput "✗ MySQL connection failed" "Red"
            return $false
        }
    }
    catch {
        Write-ColorOutput "✗ Error testing MySQL connection: $($_.Exception.Message)" "Red"
        return $false
    }
}

# Function to initialize database
function Initialize-Database {
    Write-ColorOutput "Initializing database..." "Yellow"
    
    try {
        python init_database.py
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✓ Database initialized successfully" "Green"
            return $true
        } else {
            Write-ColorOutput "✗ Database initialization failed" "Red"
            return $false
        }
    }
    catch {
        Write-ColorOutput "✗ Error initializing database: $($_.Exception.Message)" "Red"
        return $false
    }
}

# Function to start Consul
function Start-Consul {
    Write-ColorOutput "Starting Consul..." "Yellow"
    
    try {
        # Check if Consul is already running
        $consulProcess = Get-Process -Name "consul" -ErrorAction SilentlyContinue
        if ($consulProcess) {
            Write-ColorOutput "✓ Consul is already running" "Green"
            return $true
        }
        
        # Try to start Consul
        Start-Process -FilePath "consul" -ArgumentList "agent", "-dev" -WindowStyle Hidden
        Start-Sleep -Seconds 3
        
        # Check if Consul started successfully
        $consulProcess = Get-Process -Name "consul" -ErrorAction SilentlyContinue
        if ($consulProcess) {
            Write-ColorOutput "✓ Consul started successfully" "Green"
            return $true
        } else {
            Write-ColorOutput "✗ Failed to start Consul" "Red"
            return $false
        }
    }
    catch {
        Write-ColorOutput "✗ Error starting Consul: $($_.Exception.Message)" "Red"
        Write-ColorOutput "Note: Consul is optional for development. Services will continue without it." "Yellow"
        return $false
    }
}

# Function to start all services
function Start-Services {
    Write-ColorOutput "Starting all microservices..." "Yellow"
    
    try {
        # Start services using Python script
        python start_services.py
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✓ All services started successfully" "Green"
            return $true
        } else {
            Write-ColorOutput "✗ Failed to start all services" "Red"
            return $false
        }
    }
    catch {
        Write-ColorOutput "✗ Error starting services: $($_.Exception.Message)" "Red"
        return $false
    }
}

# Function to run system tests
function Test-System {
    Write-ColorOutput "Running system tests..." "Yellow"
    
    try {
        # Wait a bit for services to be ready
        Start-Sleep -Seconds 10
        
        python test_system.py
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✓ System tests passed" "Green"
            return $true
        } else {
            Write-ColorOutput "✗ System tests failed" "Red"
            return $false
        }
    }
    catch {
        Write-ColorOutput "✗ Error running system tests: $($_.Exception.Message)" "Red"
        return $false
    }
}

# Main execution
Write-ColorOutput "🚀 Starting Recruitment System" "Cyan"
Write-ColorOutput "==========================================" "Cyan"

# Check if we're in the right directory
if (-not (Test-Path "requirements.txt")) {
    Write-ColorOutput "✗ Please run this script from the project root directory" "Red"
    exit 1
}

# Check Python installation
if (-not $SkipDependencyCheck) {
    Write-ColorOutput "Checking Python installation..." "Yellow"
    if (-not (Test-PythonInstallation)) {
        Write-ColorOutput "Please install Python 3.8+ and add it to your PATH" "Red"
        exit 1
    }
    
    if (-not (Test-PipInstallation)) {
        Write-ColorOutput "Please install pip and add it to your PATH" "Red"
        exit 1
    }
    
    # Install dependencies
    if (-not (Install-Dependencies)) {
        Write-ColorOutput "Failed to install dependencies. Please check the error messages above." "Red"
        exit 1
    }
}

# Check MySQL connection
if (-not $SkipDatabaseSetup) {
    if (-not (Test-MySQLConnection)) {
        Write-ColorOutput "MySQL connection failed. Please ensure MySQL is running and accessible." "Red"
        Write-ColorOutput "You can skip this check with -SkipDatabaseSetup" "Yellow"
        exit 1
    }
    
    # Initialize database
    if (-not (Initialize-Database)) {
        Write-ColorOutput "Database initialization failed. Please check the error messages above." "Red"
        exit 1
    }
}

# Start Consul (optional)
Start-Consul

# Start all services
if (-not (Start-Services)) {
    Write-ColorOutput "Failed to start services. Please check the error messages above." "Red"
    exit 1
}

# Run system tests
if (-not (Test-System)) {
    Write-ColorOutput "System tests failed. Some services may not be working correctly." "Yellow"
}

Write-ColorOutput "==========================================" "Cyan"
Write-ColorOutput "🎉 Recruitment System is now running!" "Green"
Write-ColorOutput "" "White"
Write-ColorOutput "Service URLs:" "Cyan"
Write-ColorOutput "  Edge Service (API Gateway): http://localhost:8080" "White"
Write-ColorOutput "  Discovery Service:          http://localhost:9090" "White"
Write-ColorOutput "  Config Service:             http://localhost:9999" "White"
Write-ColorOutput "  Auth Service:               http://localhost:8081" "White"
Write-ColorOutput "  Registration Service:       http://localhost:8888" "White"
Write-ColorOutput "  Job Application Service:    http://localhost:8082" "White"
Write-ColorOutput "" "White"
Write-ColorOutput "Press Ctrl+C to stop all services" "Yellow"
Write-ColorOutput "==========================================" "Cyan"

# Keep the script running
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
}
catch {
    Write-ColorOutput "" "White"
    Write-ColorOutput "Shutting down services..." "Yellow"
    # The Python script will handle graceful shutdown
} 