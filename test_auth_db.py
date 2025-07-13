#!/usr/bin/env python3
"""
Test auth service database initialization.
"""

import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from shared.database import init_db, test_database_connection, engine
from shared.models import Base, Person, Credential, Role
from sqlalchemy.orm import Session
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

def main():
    print("=== Auth Service Database Test ===")
    
    # Check if engine was created
    if engine is None:
        print("❌ Database engine is None")
        return
    
    print(f"✅ Database engine created: {engine}")
    
    # Test connection
    print("\n=== Testing Database Connection ===")
    if test_database_connection():
        print("✅ Database connection successful")
    else:
        print("❌ Database connection failed")
        return
    
    # Initialize database
    print("\n=== Initializing Database Tables ===")
    try:
        init_db()
        print("✅ Database initialization completed")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test table creation
    print("\n=== Testing Table Creation ===")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully")
    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test querying users
    print("\n=== Testing User Query ===")
    try:
        from shared.database import SessionLocal
        db = SessionLocal()
        
        # Check if we have any users
        users = db.query(Person).all()
        print(f"✅ Found {len(users)} users in database")
        
        # Check if we have any credentials
        credentials = db.query(Credential).all()
        print(f"✅ Found {len(credentials)} credentials in database")
        
        # Check if we have any roles
        roles = db.query(Role).all()
        print(f"✅ Found {len(roles)} roles in database")
        
        # Try to find the test user
        test_credential = db.query(Credential).filter(Credential.username == "testuser4").first()
        if test_credential:
            print(f"✅ Found test user: {test_credential.username}")
            print(f"   User ID: {test_credential.person_id}")
            print(f"   Person: {test_credential.person.firstname} {test_credential.person.lastname}")
        else:
            print("❌ Test user not found")
        
        db.close()
        
    except Exception as e:
        print(f"❌ User query failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Check if database file exists
    print("\n=== Checking Database File ===")
    db_file = "recruitment_system.db"
    if os.path.exists(db_file):
        print(f"✅ Database file exists: {db_file}")
        print(f"   Size: {os.path.getsize(db_file)} bytes")
    else:
        print(f"❌ Database file not found: {db_file}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main() 