
#!/usr/bin/env python3
"""
Comprehensive system test to check all functionality.
"""

import requests
import time
import json

BASE_URL = "http://localhost:8080"

def test_basic_endpoints():
    """Test basic endpoints."""
    print("Testing basic endpoints...")
    
    endpoints = [
        "/",
        "/login", 
        "/register",
        "/health",
        "/api/jobs"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✓ {endpoint}: OK")
            else:
                print(f"✗ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"✗ {endpoint}: Error - {e}")

def test_authentication():
    """Test authentication flow."""
    print("\nTesting authentication...")
    
    # Test admin login
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", data=login_data, timeout=5)
        if response.status_code == 200:
            print("✓ Admin login: OK")
            return response.json().get("token")
        else:
            print(f"✗ Admin login: {response.status_code}")
    except Exception as e:
        print(f"✗ Admin login: Error - {e}")
    
    return None

def test_role_based_access():
    """Test role-based dashboard access."""
    print("\nTesting role-based access...")
    
    users = [
        ("admin", "admin123", "Admin"),
        ("jcandidate", "candidate123", "Applicant"), 
        ("jrecruiter", "recruiter123", "Recruiter")
    ]
    
    for username, password, role in users:
        try:
            # Login
            login_data = {"username": username, "password": password}
            session = requests.Session()
            
            response = session.post(f"{BASE_URL}/login", data=login_data, timeout=5)
            if response.status_code == 200:
                # Test dashboard access
                dashboard_response = session.get(f"{BASE_URL}/dashboard", timeout=5)
                if dashboard_response.status_code == 200:
                    print(f"✓ {role} dashboard access: OK")
                else:
                    print(f"✗ {role} dashboard access: {dashboard_response.status_code}")
            else:
                print(f"✗ {role} login: {response.status_code}")
        except Exception as e:
            print(f"✗ {role} test: Error - {e}")

if __name__ == "__main__":
    print("🧪 Running Comprehensive System Test")
    print("=" * 50)
    
    test_basic_endpoints()
    test_authentication()
    test_role_based_access()
    
    print("\n" + "=" * 50)
    print("Test completed!")
