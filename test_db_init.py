#!/usr/bin/env python3
"""
Test database initialization to identify the issue.
"""

import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from shared.database import init_db, test_database_connection, engine
from shared.models import Base
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
    print("=== Database Initialization Test ===")
    
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