#!/usr/bin/env python3
"""
Test database connection and basic operations
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from shared.database import SessionLocal, engine
from shared.models import Person, Credential, Role

def test_connection():
    """Test database connection and basic queries"""
    try:
        # Test connection
        print("Testing database connection...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✓ Database connection successful")
        
        # Test session
        print("Testing database session...")
        db = SessionLocal()
        try:
            # Test person query
            persons = db.query(Person).limit(3).all()
            print(f"✓ Found {len(persons)} persons")
            for person in persons:
                print(f"  - {person.firstname} {person.lastname} (ID: {person.id})")
            
            # Test credential query
            credentials = db.query(Credential).limit(3).all()
            print(f"✓ Found {len(credentials)} credentials")
            for cred in credentials:
                print(f"  - {cred.username} (Person ID: {cred.person_id})")
            
            # Test role query
            roles = db.query(Role).all()
            print(f"✓ Found {len(roles)} roles")
            for role in roles:
                print(f"  - {role.name} (ID: {role.id})")
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"✗ Database error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_connection() 