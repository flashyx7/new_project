# PowerShell script to start all Recruitment System services
Write-Host "Starting Recruitment System Microservices..." -ForegroundColor Green
Write-Host ""

# Set the Python path to include the project root
$env:PYTHONPATH = Get-Location

# Function to start a service
function Start-Service {
    param(
        [string]$ServiceName,
        [string]$ModulePath
    )
    
    Write-Host "Starting $ServiceName..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$((Get-Location).Path)'; `$env:PYTHONPATH = '$((Get-Location).Path)'; python -m $ModulePath" -WindowStyle Normal
    Start-Sleep -Seconds 2
}

# Start all services
Start-Service "Discovery Service" "discovery_service.main"
Start-Service "Config Service" "config_service.main"
Start-Service "Auth Service" "auth_service.main"
Start-Service "Registration Service" "registration_service.main"
Start-Service "Job Application Service" "job_application_service.main"
Start-Service "Edge Service" "edge_service.main"

Write-Host ""
Write-Host "All services are starting..." -ForegroundColor Green
Write-Host ""
Write-Host "Service URLs:" -ForegroundColor Cyan
Write-Host "- Discovery Service: http://localhost:9090" -ForegroundColor White
Write-Host "- Config Service: http://localhost:9999" -ForegroundColor White
Write-Host "- Auth Service: http://localhost:8081" -ForegroundColor White
Write-Host "- Registration Service: http://localhost:8888" -ForegroundColor White
Write-Host "- Job Application Service: http://localhost:8082" -ForegroundColor White
Write-Host "- Edge Service (API Gateway): http://localhost:8080" -ForegroundColor White
Write-Host "- Consul UI: http://localhost:8500" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 