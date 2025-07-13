#!/usr/bin/env python3
"""
Simple startup script for the Recruitment System.
Starts services in order, handling errors gracefully.
"""

import subprocess
import time
import sys
import os
from typing import Dict, List

# Service configurations
SERVICES = [
    {
        "name": "discovery-service",
        "command": ["python", "discovery_service/main.py"],
        "port": 9090,
        "health_url": "http://localhost:9090/health"
    },
    {
        "name": "config-service", 
        "command": ["python", "config_service/main.py"],
        "port": 9999,
        "health_url": "http://localhost:9999/health"
    },
    {
        "name": "edge-service",
        "command": ["python", "edge_service/main.py"],
        "port": 8080,
        "health_url": "http://localhost:8080/health"
    }
]

# Database-dependent services (start these after database is ready)
DB_SERVICES = [
    {
        "name": "auth-service",
        "command": ["python", "auth_service/main.py"],
        "port": 8081,
        "health_url": "http://localhost:8081/health"
    },
    {
        "name": "registration-service",
        "command": ["python", "registration_service/main.py"],
        "port": 8888,
        "health_url": "http://localhost:8888/health"
    },
    {
        "name": "job-application-service",
        "command": ["python", "job_application_service/main.py"],
        "port": 8082,
        "health_url": "http://localhost:8082/health"
    }
]

def check_port_available(port: int) -> bool:
    """Check if a port is available."""
    try:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def start_service(service_config: Dict) -> subprocess.Popen:
    """Start a single service."""
    name = service_config["name"]
    command = service_config["command"]
    port = service_config["port"]
    
    print(f"Starting {name} on port {port}...")
    
    # Check if port is available
    if not check_port_available(port):
        print(f"Warning: Port {port} is already in use for {name}")
    
    try:
        # Start the service
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Wait a bit for the service to start
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print(f"✓ {name} started successfully (PID: {process.pid})")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"✗ {name} failed to start")
            print(f"  Return code: {process.returncode}")
            if stdout:
                print(f"  Stdout: {stdout[:200]}...")
            if stderr:
                print(f"  Stderr: {stderr[:200]}...")
            return None
            
    except Exception as e:
        print(f"✗ Failed to start {name}: {e}")
        return None

def main():
    """Main function."""
    print("=" * 60)
    print("RECRUITMENT SYSTEM - SIMPLE STARTUP")
    print("=" * 60)
    
    processes = []
    
    # Start core services first (no database dependency)
    print("\n1. Starting core services...")
    for service in SERVICES:
        process = start_service(service)
        if process:
            processes.append((service["name"], process))
        else:
            print(f"Failed to start {service['name']}, but continuing...")
        time.sleep(2)
    
    # Start database-dependent services
    print("\n2. Starting database-dependent services...")
    print("Note: These services may fail if database is not available")
    
    for service in DB_SERVICES:
        process = start_service(service)
        if process:
            processes.append((service["name"], process))
        else:
            print(f"Failed to start {service['name']} (likely database issue)")
        time.sleep(2)
    
    # Summary
    print("\n" + "=" * 60)
    print("STARTUP SUMMARY")
    print("=" * 60)
    print(f"Successfully started {len(processes)} services:")
    for name, process in processes:
        print(f"  ✓ {name} (PID: {process.pid})")
    
    if len(processes) > 0:
        print(f"\n🎉 System is running! Access the application at:")
        print(f"   http://localhost:8080")
        print(f"\nPress Ctrl+C to stop all services")
        
        try:
            # Keep the script running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nShutting down services...")
            for name, process in processes:
                print(f"Stopping {name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
            print("All services stopped.")
    else:
        print("No services started successfully.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 