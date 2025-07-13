#!/usr/bin/env python3
"""
Test auth service login functionality directly.
"""

import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from shared.database import SessionLocal
from shared.models import Person, Credential, Role
from shared.security import verify_password, create_access_token
import structlog

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
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

def test_login(username: str, password: str):
    """Test login functionality."""
    print(f"=== Testing Login for {username} ===")
    
    try:
        db = SessionLocal()
        
        # Find user credentials
        print("1. Looking for user credentials...")
        credential = db.query(Credential).filter(Credential.username == username).first()
        if not credential:
            print("❌ User not found")
            return
        
        print(f"✅ Found user: {credential.username}")
        print(f"   User ID: {credential.person_id}")
        
        # Verify password
        print("2. Verifying password...")
        if not verify_password(password, credential.password):
            print("❌ Invalid password")
            return
        
        print("✅ Password verified")
        
        # Get user details
        print("3. Getting user details...")
        person = credential.person
        role = person.role
        
        print(f"✅ User details:")
        print(f"   Name: {person.firstname} {person.lastname}")
        print(f"   Email: {person.email}")
        print(f"   Role: {role.name}")
        
        # Create user details for JWT
        user_details = {
            "username": username,
            "user_id": person.id,
            "roles": [role.name]
        }
        
        # Generate token
        print("4. Generating JWT token...")
        token = create_access_token(user_details)
        print(f"✅ Token generated: {token[:50]}...")
        
        db.close()
        return token
        
    except Exception as e:
        print(f"❌ Login failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("=== Auth Service Login Test ===")
    
    # Test with the user we just created
    token = test_login("testuser4", "testpass123")
    
    if token:
        print("\n✅ Login test successful!")
        print(f"Token: {token[:100]}...")
    else:
        print("\n❌ Login test failed!")

if __name__ == "__main__":
    main() 