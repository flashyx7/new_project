#!/usr/bin/env python3
"""
Simple system test for the Recruitment System.
"""

import requests
import json
import time

def test_edge_service():
    """Test the edge service."""
    print("Testing Edge Service...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8080/health", timeout=5)
        if response.status_code == 200:
            print("✓ Edge service health check passed")
            print(f"  Response: {response.json()}")
        else:
            print(f"✗ Edge service health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Edge service health check failed: {e}")
        return False
    
    try:
        # Test main page
        response = requests.get("http://localhost:8080/", timeout=5)
        if response.status_code == 200:
            print("✓ Edge service main page accessible")
        else:
            print(f"✗ Edge service main page failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Edge service main page failed: {e}")
        return False
    
    return True

def test_other_services():
    """Test other services if they're running."""
    services = [
        ("Discovery Service", "http://localhost:9090/health"),
        ("Config Service", "http://localhost:9999/health"),
        ("Auth Service", "http://localhost:8081/health"),
        ("Registration Service", "http://localhost:8888/health"),
        ("Job Application Service", "http://localhost:8082/health"),
    ]
    
    print("\nTesting Other Services...")
    running_services = []
    
    for service_name, url in services:
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                print(f"✓ {service_name} is running")
                running_services.append(service_name)
            else:
                print(f"✗ {service_name} returned status {response.status_code}")
        except requests.exceptions.RequestException:
            print(f"✗ {service_name} is not responding")
    
    return running_services

def test_basic_functionality():
    """Test basic application functionality."""
    print("\nTesting Basic Functionality...")
    
    try:
        # Test registration page
        response = requests.get("http://localhost:8080/register", timeout=5)
        if response.status_code == 200:
            print("✓ Registration page accessible")
        else:
            print(f"✗ Registration page failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Registration page failed: {e}")
    
    try:
        # Test login page
        response = requests.get("http://localhost:8080/login", timeout=5)
        if response.status_code == 200:
            print("✓ Login page accessible")
        else:
            print(f"✗ Login page failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Login page failed: {e}")
    
    try:
        # Test job applications page
        response = requests.get("http://localhost:8080/applications", timeout=5)
        if response.status_code == 200:
            print("✓ Job applications page accessible")
        else:
            print(f"✗ Job applications page failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Job applications page failed: {e}")

def main():
    """Main test function."""
    print("=" * 50)
    print("RECRUITMENT SYSTEM TEST")
    print("=" * 50)
    
    # Test edge service
    if not test_edge_service():
        print("\n❌ Edge service test failed. System may not be running properly.")
        return
    
    # Test other services
    running_services = test_other_services()
    
    # Test basic functionality
    test_basic_functionality()
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"✓ Edge Service: Running")
    print(f"✓ Other Services Running: {len(running_services)}")
    if running_services:
        print(f"  - {', '.join(running_services)}")
    
    print("\n🎉 System is running! You can access the application at:")
    print("   http://localhost:8080")
    print("\nNote: Some backend services may not be running, but the edge service")
    print("is functional and can serve the frontend interface.")

if __name__ == "__main__":
    main() 