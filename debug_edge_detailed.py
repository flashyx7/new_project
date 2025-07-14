#!/usr/bin/env python3
"""
Detailed debug script for edge service routing.
"""

import asyncio
import httpx
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the edge service components
from edge_service.main import SERVICE_ROUTES, get_service_name_from_path

async def test_direct_routing():
    """Test the routing logic step by step."""
    print("Testing edge service routing step by step...")

    # Test path
    path = "/registration/register"
    print(f"\n1. Testing path: {path}")

    # Get service name
    service_name = get_service_name_from_path(path)
    print(f"2. Service name: {service_name}")

    if not service_name:
        print("❌ Service name not found")
        return

    # Get route config
    route_config = SERVICE_ROUTES.get(service_name, {})
    print(f"3. Route config: {route_config}")

    if not route_config:
        print("❌ Route config not found")
        return

    # Construct target URL
    target_path = route_config.get("target_path", "/")
    host = route_config.get("host", "localhost")
    port = route_config.get("port", 80)

    # Construct the target URL
    service_path = path[len(route_config['prefix']):] if path.startswith(route_config['prefix']) else path
    if not service_path.startswith('/'):
        service_path = '/' + service_path
    target_url = f"http://{host}:{port}{service_path}"

    print(f"4. Target path: {target_path}")
    print(f"5. Host: {host}")
    print(f"6. Port: {port}")
    print(f"7. Service path: {service_path}")
    print(f"8. Target URL: {target_url}")

    # Test the direct connection
    print(f"\n9. Testing direct connection to: {target_url}")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"http://{host}:{port}/health")
            print(f"   Health check status: {response.status_code}")
            print(f"   Health check response: {response.text}")
    except Exception as e:
        print(f"   ❌ Direct connection failed: {e}")
        return

    # Test the actual endpoint
    print(f"\n10. Testing registration endpoint...")
    registration_data = {
        "firstname": "Debug",
        "lastname": "User",
        "email": "debug@example.com",
        "date_of_birth": "1990-01-01",
        "username": "debuguser",
        "password": "password123",
        "role_id": 2
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                target_url,
                json=registration_data,
                headers={"Content-Type": "application/json"}
            )
            print(f"   Registration status: {response.status_code}")
            print(f"   Registration response: {response.text}")
    except Exception as e:
        print(f"   ❌ Registration failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_direct_routing())