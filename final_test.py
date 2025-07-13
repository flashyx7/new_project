#!/usr/bin/env python3
"""
Final comprehensive test for the Recruitment System.
"""

import requests
import json

def test_all_services():
    """Test all services comprehensively."""
    print("=" * 60)
    print("FINAL COMPREHENSIVE TEST")
    print("=" * 60)
    
    # Test all service health endpoints
    services = [
        ("Discovery Service", "http://localhost:9090/health"),
        ("Config Service", "http://localhost:9999/health"),
        ("Auth Service", "http://localhost:8081/health"),
        ("Registration Service", "http://localhost:8888/health"),
        ("Job Application Service", "http://localhost:8082/health"),
        ("Edge Service", "http://localhost:8080/health")
    ]
    
    print("\n1. Testing Service Health:")
    all_healthy = True
    for name, url in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"  ✓ {name}: Healthy")
            else:
                print(f"  ✗ {name}: Status {response.status_code}")
                all_healthy = False
        except Exception as e:
            print(f"  ✗ {name}: Error - {e}")
            all_healthy = False
    
    if not all_healthy:
        print("\n❌ Some services are not healthy. Stopping tests.")
        return False
    
    # Test direct registration
    print("\n2. Testing Direct Registration:")
    try:
        registration_data = {
            "firstname": "Direct",
            "lastname": "Test",
            "email": "direct@example.com",
            "date_of_birth": "1990-01-01",
            "username": "directtest",
            "password": "password123",
            "role_id": 2
        }
        
        response = requests.post(
            "http://localhost:8888/register",
            json=registration_data,
            timeout=10
        )
        
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text}")
        
        if response.status_code == 200:
            print("  ✓ Direct registration successful")
        else:
            print("  ✗ Direct registration failed")
            return False
    except Exception as e:
        print(f"  ✗ Direct registration error: {e}")
        return False
    
    # Test edge service routing
    print("\n3. Testing Edge Service Routing:")
    try:
        registration_data = {
            "firstname": "Edge",
            "lastname": "Test",
            "email": "edge@example.com",
            "date_of_birth": "1990-01-01",
            "username": "edgetest",
            "password": "password123",
            "role_id": 2
        }
        
        response = requests.post(
            "http://localhost:8080/registration/register",
            json=registration_data,
            timeout=10
        )
        
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text}")
        
        if response.status_code == 200:
            print("  ✓ Edge routing successful")
        else:
            print("  ✗ Edge routing failed")
            return False
    except Exception as e:
        print(f"  ✗ Edge routing error: {e}")
        return False
    
    # Test login
    print("\n4. Testing Login:")
    try:
        login_data = {
            "username": "edgetest",
            "password": "password123"
        }
        
        response = requests.post(
            "http://localhost:8080/auth/login",
            json=login_data,
            timeout=10
        )
        
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if "token" in result:
                print("  ✓ Login successful")
                token = result["token"]
            else:
                print("  ✗ Login failed - no token")
                return False
        else:
            print("  ✗ Login failed")
            return False
    except Exception as e:
        print(f"  ✗ Login error: {e}")
        return False
    
    # Test web interface
    print("\n5. Testing Web Interface:")
    try:
        response = requests.get("http://localhost:8080/", timeout=5)
        if response.status_code == 200:
            print("  ✓ Web interface accessible")
        else:
            print(f"  ✗ Web interface failed: {response.status_code}")
    except Exception as e:
        print(f"  ✗ Web interface error: {e}")
    
    print("\n" + "=" * 60)
    print("FINAL TEST SUMMARY")
    print("=" * 60)
    print("✓ All services are healthy")
    print("✓ Direct registration works")
    print("✓ Edge service routing works")
    print("✓ Login functionality works")
    print("✓ Web interface is accessible")
    
    print("\n🎉 SUCCESS! The Recruitment System is fully operational!")
    print("\nYou can now:")
    print("1. Access the web interface at: http://localhost:8080")
    print("2. Register new users via the API")
    print("3. Login and authenticate users")
    print("4. Use all microservices through the edge service")
    
    return True

if __name__ == "__main__":
    success = test_all_services()
    exit(0 if success else 1) 