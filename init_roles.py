#!/usr/bin/env python3
"""
Initialize database with required roles.
"""

import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from shared.database import SessionLocal, init_db
from shared.models import Base, Role, Person, Credential
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

def init_roles():
    """Initialize the database with required roles."""
    print("=== Initializing Database Roles ===")
    
    try:
        # Initialize database
        init_db()
        
        db = SessionLocal()
        
        # Check if roles already exist
        existing_roles = db.query(Role).all()
        print(f"Found {len(existing_roles)} existing roles:")
        for role in existing_roles:
            print(f"  - ID: {role.id}, Name: {role.name}")
        
        # Create roles if they don't exist
        roles_to_create = [
            {"id": 1, "name": "Admin"},
            {"id": 2, "name": "Applicant"},
            {"id": 3, "name": "Recruiter"}
        ]
        
        for role_data in roles_to_create:
            existing_role = db.query(Role).filter(Role.id == role_data["id"]).first()
            if not existing_role:
                role = Role(id=role_data["id"], name=role_data["name"])
                db.add(role)
                print(f"✅ Created role: {role.name} (ID: {role.id})")
            else:
                print(f"⏭️  Role already exists: {existing_role.name} (ID: {existing_role.id})")
        
        db.commit()
        
        # Check all roles after creation
        all_roles = db.query(Role).all()
        print(f"\nTotal roles in database: {len(all_roles)}")
        for role in all_roles:
            print(f"  - ID: {role.id}, Name: {role.name}")
        
        # Check users and their roles
        print("\n=== Checking Users and Their Roles ===")
        users = db.query(Person).all()
        print(f"Found {len(users)} users:")
        for user in users:
            role_name = user.role.name if user.role else "No role assigned"
            print(f"  - {user.firstname} {user.lastname} (ID: {user.id}) - Role: {role_name}")
        
        db.close()
        print("\n✅ Role initialization completed successfully!")
        
    except Exception as e:
        print(f"❌ Role initialization failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    init_roles() 