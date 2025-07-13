#!/usr/bin/env python3
"""
Debug script for edge service routing.
"""

# Import the edge service routing logic
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the routing function
from edge_service.main import get_service_name_from_path, SERVICE_ROUTES

def test_routing():
    """Test the routing logic."""
    print("SERVICE_ROUTES configuration:")
    for service_name, config in SERVICE_ROUTES.items():
        print(f"  {service_name}: {config}")
    
    print("\nTesting path matching:")
    test_paths = [
        "/registration/register",
        "/auth/login", 
        "/jobapplications/123",
        "/health",
        "/unknown/path"
    ]
    
    for path in test_paths:
        service_name = get_service_name_from_path(path)
        print(f"  Path: {path} -> Service: {service_name}")

if __name__ == "__main__":
    test_routing() 