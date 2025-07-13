#!/usr/bin/env python3
"""
Test script to check each service individually and identify errors.
"""

import requests
import subprocess
import time
import sys
import os

def test_service_health(service_name, port, health_url):
    """Test a service's health endpoint."""
    try:
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            print(f"✓ {service_name} is healthy")
            return True
        else:
            print(f"✗ {service_name} returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ {service_name} is not responding: {e}")
        return False

def start_service_and_test(service_name, command, port, health_url):
    """Start a service and test it."""
    print(f"\n{'='*50}")
    print(f"Testing {service_name}")
    print(f"{'='*50}")
    
    # Start the service
    print(f"Starting {service_name}...")
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for service to start
    time.sleep(5)
    
    # Check if process is still running
    if process.poll() is not None:
        stdout, stderr = process.communicate()
        print(f"✗ {service_name} failed to start")
        print(f"Return code: {process.returncode}")
        if stdout:
            print(f"Stdout: {stdout}")
        if stderr:
            print(f"Stderr: {stderr}")
        return False
    
    print(f"✓ {service_name} process started (PID: {process.pid})")
    
    # Test health endpoint
    time.sleep(2)
    health_ok = test_service_health(service_name, port, health_url)
    
    # Stop the service
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
    
    return health_ok

def main():
    """Main test function."""
    services = [
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
        },
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
    
    results = []
    
    for service in services:
        success = start_service_and_test(
            service["name"],
            service["command"],
            service["port"],
            service["health_url"]
        )
        results.append((service["name"], success))
        time.sleep(2)  # Wait between services
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    
    working_services = []
    failed_services = []
    
    for name, success in results:
        if success:
            working_services.append(name)
            print(f"✓ {name}: Working")
        else:
            failed_services.append(name)
            print(f"✗ {name}: Failed")
    
    print(f"\nWorking services: {len(working_services)}")
    print(f"Failed services: {len(failed_services)}")
    
    if failed_services:
        print(f"\nFailed services: {', '.join(failed_services)}")
        print("\nCommon issues:")
        print("1. Database connection problems")
        print("2. Missing dependencies")
        print("3. Port conflicts")
        print("4. Configuration errors")
    
    return len(failed_services) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 