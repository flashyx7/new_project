#!/usr/bin/env python3
"""
Simple test to debug edge service path handling.
"""

import requests

def test_edge_paths():
    """Test different paths on the edge service."""
    print("Testing edge service path handling...")
    
    # Test the exact path that should work
    path = "/registration/register"
    print(f"\nTesting path: {path}")
    
    try:
        response = requests.post(
            f"http://localhost:8080{path}",
            json={
                "firstname": "Test",
                "lastname": "User",
                "email": "test@example.com",
                "date_of_birth": "1990-01-01",
                "username": "testuser",
                "password": "password123",
                "role_id": 2
            },
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test a simpler path
    print(f"\nTesting simple path: /registration")
    try:
        response = requests.get("http://localhost:8080/registration", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test health endpoint
    print(f"\nTesting health endpoint: /health")
    try:
        response = requests.get("http://localhost:8080/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_edge_paths() 