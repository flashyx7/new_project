#!/usr/bin/env python3
"""
Startup script for the Recruitment System Python microservices.
This script starts all services locally for development purposes.
"""

import asyncio
import subprocess
import sys
import time
import os
from pathlib import Path

# Service configurations
SERVICES = [
    {
        "name": "discovery-service",
        "port": 9090,
        "path": "discovery_service",
        "command": ["python", "main.py"]
    },
    {
        "name": "config-service", 
        "port": 9999,
        "path": "config_service",
        "command": ["python", "main.py"]
    },
    {
        "name": "auth-service",
        "port": 8081,
        "path": "auth_service", 
        "command": ["python", "main.py"]
    },
    {
        "name": "registration-service",
        "port": 8888,
        "path": "registration_service",
        "command": ["python", "main.py"]
    },
    {
        "name": "job-application-service",
        "port": 8082,
        "path": "job_application_service",
        "command": ["python", "main.py"]
    },
    {
        "name": "edge-service",
        "port": 8080,
        "path": "edge_service",
        "command": ["python", "main.py"]
    }
]

def check_port_available(port):
    """Check if a port is available."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

def wait_for_service(service_name, port, timeout=30):
    """Wait for a service to be available."""
    import socket
    import time
    
    print(f"Waiting for {service_name} on port {port}...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                if s.connect_ex(('localhost', port)) == 0:
                    print(f"✓ {service_name} is ready")
                    return True
        except:
            pass
        time.sleep(1)
    
    print(f"✗ {service_name} failed to start within {timeout} seconds")
    return False

def start_service(service_config):
    """Start a single service."""
    name = service_config["name"]
    port = service_config["port"]
    path = service_config["path"]
    command = service_config["command"]
    
    # Check if port is available
    if not check_port_available(port):
        print(f"✗ Port {port} is already in use. {name} may already be running.")
        return None
    
    # Change to service directory
    service_path = Path(path)
    if not service_path.exists():
        print(f"✗ Service directory {path} not found")
        return None
    
    # Start the service
    try:
        print(f"Starting {name}...")
        
        # Set environment variables
        env = os.environ.copy()
        env['PYTHONPATH'] = str(Path.cwd())
        
        # Use shell=False for better cross-platform compatibility
        process = subprocess.Popen(
            command,
            cwd=service_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False,
            env=env
        )
        
        # Wait a bit for the service to start
        time.sleep(2)
        
        # Check if process is still running
        if process.poll() is None:
            print(f"✓ {name} started (PID: {process.pid})")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"✗ {name} failed to start:")
            print(f"  stdout: {stdout}")
            print(f"  stderr: {stderr}")
            return None
            
    except Exception as e:
        print(f"✗ Failed to start {name}: {e}")
        return None

def check_dependencies():
    """Check if required dependencies are installed."""
    required_modules = ["fastapi", "uvicorn", "sqlalchemy"]
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"✗ Missing dependencies: {', '.join(missing_modules)}")
        print("Please install requirements: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main function to start all services."""
    print("🚀 Starting Recruitment System Python Microservices")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("shared").exists():
        print("✗ Please run this script from the project root directory")
        sys.exit(1)
    
    # Check if requirements are installed
    if not check_dependencies():
        sys.exit(1)
    
    processes = []
    
    try:
        # Start services in order
        for service_config in SERVICES:
            process = start_service(service_config)
            if process:
                processes.append((service_config["name"], process))
                
                # Wait for service to be ready before starting next
                if service_config["name"] != "edge-service":  # Don't wait for edge service
                    wait_for_service(service_config["name"], service_config["port"])
            else:
                print(f"✗ Failed to start {service_config['name']}")
                break
        
        if len(processes) == len(SERVICES):
            print("\n🎉 All services started successfully!")
            print("\nService URLs:")
            print("  Edge Service (API Gateway): http://localhost:8080")
            print("  Discovery Service:          http://localhost:9090")
            print("  Config Service:             http://localhost:9999")
            print("  Auth Service:               http://localhost:8081")
            print("  Registration Service:       http://localhost:8888")
            print("  Job Application Service:    http://localhost:8082")
            print("\nPress Ctrl+C to stop all services")
            
            # Keep running until interrupted
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping services...")
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
    
    finally:
        # Stop all processes
        for name, process in processes:
            print(f"Stopping {name}...")
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                print(f"Error stopping {name}: {e}")
        
        print("✅ All services stopped")

if __name__ == "__main__":
    main() 