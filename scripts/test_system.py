#!/usr/bin/env python3
"""
Test script for the Recruitment System Python microservices.
This script tests the basic functionality of all services.
"""

import asyncio
import httpx
import json
import time
import structlog
from typing import Dict, Any

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

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
        self.client = httpx.AsyncClient(timeout=30.0)
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
        logger.info("Testing health checks...")
        
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
                    logger.info(f"{service_name} is healthy")
                else:
                    logger.error(f"{service_name} is unhealthy", status_code=response.status_code)
            except Exception as e:
                logger.error(f"{service_name} health check failed", error=str(e))
    
    async def test_service_discovery(self):
        """Test service discovery functionality."""
        logger.info("Testing service discovery...")
        
        try:
            response = await self.client.get(f"{DISCOVERY_URL}/services")
            if response.status_code == 200:
                services = response.json()
                service_count = len(services.get('services', []))
                logger.info("Discovery service working", service_count=service_count)
            else:
                logger.error("Discovery service error", status_code=response.status_code)
        except Exception as e:
            logger.error("Discovery service error", error=str(e))
    
    async def test_config_service(self):
        """Test configuration service."""
        logger.info("Testing config service...")
        
        try:
            response = await self.client.get(f"{CONFIG_URL}/config")
            if response.status_code == 200:
                configs = response.json()
                config_count = len(configs.get('configs', {}))
                logger.info("Config service working", config_count=config_count)
            else:
                logger.error("Config service error", status_code=response.status_code)
        except Exception as e:
            logger.error("Config service error", error=str(e))
    
    async def test_user_registration(self):
        """Test user registration."""
        logger.info("Testing user registration...")
        
        try:
            response = await self.client.post(
                f"{REGISTRATION_URL}/register",
                json=self.test_user
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "CREATED":
                    logger.info("User registration successful")
                    return True
                else:
                    logger.error("User registration failed", result=result)
                    return False
            else:
                logger.error("User registration error", status_code=response.status_code)
                return False
        except Exception as e:
            logger.error("User registration error", error=str(e))
            return False

    async def test_recruiter_registration(self):
        """Test recruiter registration."""
        logger.info("Testing recruiter registration...")
        try:
            response = await self.client.post(
                f"{REGISTRATION_URL}/register",
                json=self.recruiter_user
            )
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "CREATED":
                    logger.info("Recruiter registration successful")
                    return True
                else:
                    logger.error("Recruiter registration failed", result=result)
                    return False
            else:
                logger.error("Recruiter registration error", status_code=response.status_code)
                return False
        except Exception as e:
            logger.error("Recruiter registration error", error=str(e))
            return False
    
    async def test_user_login(self):
        """Test user login and get JWT token."""
        logger.info("Testing user login...")
        
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
                    logger.info("User login successful")
                    return True
                else:
                    logger.error("No token received")
                    return False
            else:
                logger.error("User login error", status_code=response.status_code)
                return False
        except Exception as e:
            logger.error("User login error", error=str(e))
            return False

    async def test_recruiter_login(self):
        """Test recruiter login and get JWT token."""
        logger.info("Testing recruiter login...")
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
                    logger.info("Recruiter login successful")
                    return True
                else:
                    logger.error("No recruiter token received")
                    return False
            else:
                logger.error("Recruiter login error", status_code=response.status_code)
                return False
        except Exception as e:
            logger.error("Recruiter login error", error=str(e))
            return False
    
    async def test_job_application_endpoints(self):
        """Test job application endpoints."""
        logger.info("Testing job application endpoints...")
        
        if not self.recruiter_token:
            logger.error("No recruiter token available")
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
                logger.info("Competences endpoint working", count=len(competences))
            else:
                logger.error("Competences endpoint error", status_code=response.status_code)
        except Exception as e:
            logger.error("Competences endpoint error", error=str(e))
        
        # Test getting statuses (recruiter)
        try:
            response = await self.client.get(
                f"{JOB_APP_URL}/en/statuses",
                headers=recruiter_headers
            )
            
            if response.status_code == 200:
                statuses = response.json()
                logger.info("Statuses endpoint working", count=len(statuses))
            else:
                logger.error("Statuses endpoint error", status_code=response.status_code)
        except Exception as e:
            logger.error("Statuses endpoint error", error=str(e))
    
    async def test_person_endpoints(self):
        """Test person management endpoints."""
        logger.info("Testing person endpoints...")
        
        try:
            # Test getting person by ID (assuming ID 2 exists from sample data)
            response = await self.client.get(f"{REGISTRATION_URL}/en/persons/2")
            
            if response.status_code == 200:
                person = response.json()
                logger.info("Person endpoint working", 
                          firstname=person.get('firstname'), 
                          lastname=person.get('lastname'))
            else:
                logger.error("Person endpoint error", status_code=response.status_code)
        except Exception as e:
            logger.error("Person endpoint error", error=str(e))
    
    async def run_all_tests(self):
        """Run all tests."""
        logger.info("Testing Recruitment System Python Microservices")
        
        # Wait a bit for services to be ready
        logger.info("Waiting for services to be ready...")
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
        
        logger.info("Testing completed!")
        
        # Clean up
        await self.client.aclose()

async def main():
    """Main function."""
    tester = SystemTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 