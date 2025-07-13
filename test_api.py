#!/usr/bin/env python3
"""
API test script for the Recruitment System.
"""

import requests
import json

def test_registration():
    """Test user registration."""
    print("Testing user registration...")
    
    registration_data = {
        "firstname": "John",
        "lastname": "Doe", 
        "email": "john@example.com",
        "date_of_birth": "1990-01-01",
        "username": "johndoe",
        "password": "password123",
        "role_id": 2
    }
    
    try:
        response = requests.post(
            "http://localhost:8080/registration/register",
            json=registration_data,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✓ Registration successful")
            return True
        else:
            print("✗ Registration failed")
            return False
            
    except Exception as e:
        print(f"✗ Registration error: {e}")
        return False

def test_login():
    """Test user login."""
    print("\nTesting user login...")
    
    login_data = {
        "username": "johndoe",
        "password": "password123"
    }
    
    try:
        response = requests.post(
            "http://localhost:8080/auth/login",
            json=login_data,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if "token" in result:
                print("✓ Login successful")
                return result["token"]
            else:
                print("✗ Login failed - no token received")
                return None
        else:
            print("✗ Login failed")
            return None
            
    except Exception as e:
        print(f"✗ Login error: {e}")
        return None

def test_health_checks():
    """Test all service health endpoints."""
    print("Testing service health checks...")
    
    services = [
        ("Discovery Service", "http://localhost:9090/health"),
        ("Config Service", "http://localhost:9999/health"),
        ("Auth Service", "http://localhost:8081/health"),
        ("Registration Service", "http://localhost:8888/health"),
        ("Job Application Service", "http://localhost:8082/health"),
        ("Edge Service", "http://localhost:8080/health")
    ]
    
    all_healthy = True
    
    for name, url in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✓ {name}: Healthy")
            else:
                print(f"✗ {name}: Status {response.status_code}")
                all_healthy = False
        except Exception as e:
            print(f"✗ {name}: Error - {e}")
            all_healthy = False
    
    return all_healthy

def main():
    """Main test function."""
    print("=" * 60)
    print("RECRUITMENT SYSTEM API TEST")
    print("=" * 60)
    
    # Test health checks first
    print("\n1. Testing service health...")
    health_ok = test_health_checks()
    
    if not health_ok:
        print("\n❌ Some services are not healthy. Stopping tests.")
        return False
    
    # Test registration
    print("\n2. Testing registration...")
    registration_ok = test_registration()
    
    # Test login
    print("\n3. Testing login...")
    token = test_login()
    
    # Summary
    print("\n" + "=" * 60)
    print("API TEST SUMMARY")
    print("=" * 60)
    print(f"Health Checks: {'✓' if health_ok else '✗'}")
    print(f"Registration: {'✓' if registration_ok else '✗'}")
    print(f"Login: {'✓' if token else '✗'}")
    
    if token:
        print(f"\n🎉 API is working! Token received: {token[:20]}...")
    else:
        print(f"\n⚠️ API has some issues. Check the logs above.")
    
    return health_ok and registration_ok and token is not None

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 