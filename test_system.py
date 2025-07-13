#!/usr/bin/env python3
"""
Test script for the Recruitment System Python microservices.
This script tests the basic functionality of all services.
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any

# Service URLs
BASE_URL = "http://localhost:8080"  # Edge service
DISCOVERY_URL = "http://localhost:9090"
CONFIG_URL = "http://localhost:9999"
AUTH_URL = "http://localhost:8081"
REGISTRATION_URL = "http://localhost:8888"
JOB_APP_URL = "http://localhost:8082"

class SystemTester:
    """Test the recruitment system microservices."""
    
    def __init__(self):
        self.client = httpx.AsyncClient()
        # Applicant user
        self.test_user = {
            "firstname": "TestNew",
            "lastname": "User",
            "date_of_birth": "1995-05-05",
            "email": f"testuser{int(time.time())}@example.com",
            "username": f"testuser{int(time.time())}",
            "password": "TestPassword123!"
        }
        # Recruiter user
        self.recruiter_user = {
            "firstname": "Recruiter",
            "lastname": "User",
            "date_of_birth": "1980-01-01",
            "email": f"recruiter{int(time.time())}@example.com",
            "username": f"recruiter{int(time.time())}",
            "password": "RecruiterPassword123!",
            "role_id": 1
        }
        self.auth_token = None
        self.recruiter_token = None
    
    async def test_health_checks(self):
        """Test health check endpoints."""
        print("🔍 Testing health checks...")
        
        services = [
            ("Edge Service", f"{BASE_URL}/health"),
            ("Discovery Service", f"{DISCOVERY_URL}/health"),
            ("Config Service", f"{CONFIG_URL}/health"),
            ("Auth Service", f"{AUTH_URL}/health"),
            ("Registration Service", f"{REGISTRATION_URL}/health"),
            ("Job Application Service", f"{JOB_APP_URL}/health")
        ]
        
        for service_name, url in services:
            try:
                response = await self.client.get(url)
                if response.status_code == 200:
                    print(f"  ✓ {service_name}: Healthy")
                else:
                    print(f"  ✗ {service_name}: Unhealthy (Status: {response.status_code})")
            except Exception as e:
                print(f"  ✗ {service_name}: Error - {e}")
    
    async def test_service_discovery(self):
        """Test service discovery functionality."""
        print("\n🔍 Testing service discovery...")
        
        try:
            response = await self.client.get(f"{DISCOVERY_URL}/services")
            if response.status_code == 200:
                services = response.json()
                print(f"  ✓ Discovery service working. Found {len(services.get('services', []))} services")
            else:
                print(f"  ✗ Discovery service error: {response.status_code}")
        except Exception as e:
            print(f"  ✗ Discovery service error: {e}")
    
    async def test_config_service(self):
        """Test configuration service."""
        print("\n🔍 Testing config service...")
        
        try:
            response = await self.client.get(f"{CONFIG_URL}/config")
            if response.status_code == 200:
                configs = response.json()
                print(f"  ✓ Config service working. Found {len(configs.get('configs', {}))} configurations")
            else:
                print(f"  ✗ Config service error: {response.status_code}")
        except Exception as e:
            print(f"  ✗ Config service error: {e}")
    
    async def test_user_registration(self):
        """Test user registration."""
        print("\n🔍 Testing user registration...")
        
        try:
            response = await self.client.post(
                f"{REGISTRATION_URL}/register",
                json=self.test_user
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "CREATED":
                    print("  ✓ User registration successful")
                    return True
                else:
                    print(f"  ✗ User registration failed: {result}")
                    return False
            else:
                print(f"  ✗ User registration error: {response.status_code}")
                return False
        except Exception as e:
            print(f"  ✗ User registration error: {e}")
            return False

    async def test_recruiter_registration(self):
        """Test recruiter registration."""
        print("\n🔍 Testing recruiter registration...")
        try:
            response = await self.client.post(
                f"{REGISTRATION_URL}/register",
                json=self.recruiter_user
            )
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "CREATED":
                    print("  ✓ Recruiter registration successful")
                    return True
                else:
                    print(f"  ✗ Recruiter registration failed: {result}")
                    return False
            else:
                print(f"  ✗ Recruiter registration error: {response.status_code}")
                return False
        except Exception as e:
            print(f"  ✗ Recruiter registration error: {e}")
            return False
    
    async def test_user_login(self):
        """Test user login and get JWT token."""
        print("\n🔍 Testing user login...")
        
        try:
            login_data = {
                "username": self.test_user["username"],
                "password": self.test_user["password"]
            }
            
            response = await self.client.post(
                f"{AUTH_URL}/auth/login",
                json=login_data
            )
            
            if response.status_code == 200:
                result = response.json()
                self.auth_token = result.get("token")
                if self.auth_token:
                    print("  ✓ User login successful")
                    return True
                else:
                    print("  ✗ No token received")
                    return False
            else:
                print(f"  ✗ User login error: {response.status_code}")
                return False
        except Exception as e:
            print(f"  ✗ User login error: {e}")
            return False

    async def test_recruiter_login(self):
        """Test recruiter login and get JWT token."""
        print("\n🔍 Testing recruiter login...")
        try:
            login_data = {
                "username": self.recruiter_user["username"],
                "password": self.recruiter_user["password"]
            }
            response = await self.client.post(
                f"{AUTH_URL}/auth/login",
                json=login_data
            )
            if response.status_code == 200:
                result = response.json()
                self.recruiter_token = result.get("token")
                if self.recruiter_token:
                    print("  ✓ Recruiter login successful")
                    return True
                else:
                    print("  ✗ No recruiter token received")
                    return False
            else:
                print(f"  ✗ Recruiter login error: {response.status_code}")
                return False
        except Exception as e:
            print(f"  ✗ Recruiter login error: {e}")
            return False
    
    async def test_job_application_endpoints(self):
        """Test job application endpoints."""
        print("\n🔍 Testing job application endpoints...")
        
        if not self.recruiter_token:
            print("  ✗ No recruiter token available")
            return False
        
        recruiter_headers = {"Authorization": f"Bearer {self.recruiter_token}"}
        
        # Test getting competences (recruiter)
        try:
            response = await self.client.get(
                f"{JOB_APP_URL}/en/competences",
                headers=recruiter_headers
            )
            
            if response.status_code == 200:
                competences = response.json()
                print(f"  ✓ Competences endpoint working. Found {len(competences)} competences")
            else:
                print(f"  ✗ Competences endpoint error: {response.status_code}")
        except Exception as e:
            print(f"  ✗ Competences endpoint error: {e}")
        
        # Test getting statuses (recruiter)
        try:
            response = await self.client.get(
                f"{JOB_APP_URL}/en/statuses",
                headers=recruiter_headers
            )
            
            if response.status_code == 200:
                statuses = response.json()
                print(f"  ✓ Statuses endpoint working. Found {len(statuses)} statuses")
            else:
                print(f"  ✗ Statuses endpoint error: {response.status_code}")
        except Exception as e:
            print(f"  ✗ Statuses endpoint error: {e}")
    
    async def test_person_endpoints(self):
        """Test person management endpoints."""
        print("\n🔍 Testing person endpoints...")
        
        try:
            # Test getting person by ID (assuming ID 2 exists from sample data)
            response = await self.client.get(f"{REGISTRATION_URL}/en/persons/2")
            
            if response.status_code == 200:
                person = response.json()
                print(f"  ✓ Person endpoint working. Found person: {person.get('firstname')} {person.get('lastname')}")
            else:
                print(f"  ✗ Person endpoint error: {response.status_code}")
        except Exception as e:
            print(f"  ✗ Person endpoint error: {e}")
    
    async def run_all_tests(self):
        """Run all tests."""
        print("🧪 Testing Recruitment System Python Microservices")
        print("=" * 60)
        
        # Wait a bit for services to be ready
        print("Waiting for services to be ready...")
        await asyncio.sleep(5)
        
        # Run tests
        await self.test_health_checks()
        await self.test_service_discovery()
        await self.test_config_service()
        
        # Test user flow
        await self.test_user_registration()
        await self.test_recruiter_registration()
        await self.test_user_login()
        await self.test_recruiter_login()
        await self.test_job_application_endpoints()
        await self.test_person_endpoints()
        
        print("\n" + "=" * 60)
        print("✅ Testing completed!")
        
        # Clean up
        await self.client.aclose()

async def main():
    """Main function."""
    tester = SystemTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 