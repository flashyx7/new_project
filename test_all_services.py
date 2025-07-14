
#!/usr/bin/env python3
"""
Test all microservices to ensure they're working properly.
"""

import requests
import json
import time

def test_service(name, url, timeout=5):
    """Test a service health endpoint."""
    try:
        response = requests.get(f"{url}/health", timeout=timeout)
        if response.status_code == 200:
            print(f"✓ {name} - HEALTHY")
            return True
        else:
            print(f"⚠ {name} - UNHEALTHY (Status: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {name} - FAILED ({str(e)})")
        return False

def test_edge_service_functionality():
    """Test edge service functionality."""
    print("\n🔍 Testing Edge Service functionality...")
    
    # Test main page
    try:
        response = requests.get("http://localhost:8080/", timeout=5)
        if response.status_code == 200:
            print("✓ Main page accessible")
        else:
            print(f"⚠ Main page failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Main page failed: {e}")
    
    # Test jobs API
    try:
        response = requests.get("http://localhost:8080/api/jobs", timeout=5)
        if response.status_code == 200:
            jobs = response.json()
            print(f"✓ Jobs API working ({len(jobs.get('jobs', []))} jobs available)")
        else:
            print(f"⚠ Jobs API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Jobs API failed: {e}")

def main():
    """Main test function."""
    print("🧪 Testing Recruitment System Microservices")
    print("=" * 50)
    
    services = [
        ("Discovery Service", "http://localhost:9090"),
        ("Config Service", "http://localhost:9999"),
        ("Auth Service", "http://localhost:8081"),
        ("Registration Service", "http://localhost:8888"),
        ("Job Application Service", "http://localhost:8082"),
        ("Edge Service", "http://localhost:8080"),
    ]
    
    healthy_services = 0
    
    for name, url in services:
        if test_service(name, url):
            healthy_services += 1
        time.sleep(0.5)
    
    print(f"\n📊 Service Health Summary: {healthy_services}/{len(services)} services healthy")
    
    # Test edge service functionality
    if healthy_services > 0:
        test_edge_service_functionality()
    
    print("\n🎯 Test Results:")
    if healthy_services == len(services):
        print("🎉 ALL SERVICES ARE HEALTHY!")
    elif healthy_services >= len(services) // 2:
        print("⚠️  MOST SERVICES ARE WORKING")
    else:
        print("❌ SYSTEM HAS ISSUES")
    
    print("\n🌐 Access the application at: http://localhost:8080")

if __name__ == "__main__":
    main()
