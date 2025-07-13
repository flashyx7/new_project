#!/usr/bin/env python3
"""
Database initialization script for the recruitment system.
This script creates all necessary tables and inserts test data.
"""

import os
import sys
from sqlalchemy import create_engine, text
from passlib.context import CryptContext

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared.database import engine, Base
from shared.models import Person, Credential, Role

# Password hashing context
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password using pbkdf2_sha256."""
    return pwd_context.hash(password)

def init_database():
    """Initialize the database with tables and test data."""
    print("Initializing database...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")
    
    # Create a session to insert data
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if roles already exist
        existing_roles = db.query(Role).all()
        if existing_roles:
            print("Roles already exist, skipping role creation.")
        else:
            # Create roles
            roles = [
                Role(id=1, name="ROLE_RECRUITER"),
                Role(id=2, name="ROLE_APPLICANT"),
                Role(id=3, name="Admin")
            ]
            db.add_all(roles)
            db.commit()
            print("Roles created successfully.")
        
        # Check if test users already exist
        existing_credentials = db.query(Credential).filter(
            Credential.username.in_(["admin", "applicant"])
        ).all()
        
        if existing_credentials:
            print("Test users already exist, skipping user creation.")
        else:
            # Create test users
            # Admin user
            admin_person = Person(
                firstname="Admin",
                lastname="User",
                date_of_birth="1990-01-01",
                email="admin@example.com",
                role_id=3  # Admin role
            )
            db.add(admin_person)
            db.flush()  # Get the ID
            
            admin_credential = Credential(
                username="admin",
                password=hash_password("admin123"),
                person_id=admin_person.id
            )
            db.add(admin_credential)
            
            # Applicant user
            applicant_person = Person(
                firstname="Applicant",
                lastname="User",
                date_of_birth="1995-01-01",
                email="applicant@example.com",
                role_id=2  # Applicant role
            )
            db.add(applicant_person)
            db.flush()  # Get the ID
            
            applicant_credential = Credential(
                username="applicant",
                password=hash_password("applicant123"),
                person_id=applicant_person.id
            )
            db.add(applicant_credential)
            
            db.commit()
            print("Test users created successfully.")
            print("Admin user: admin / admin123")
            print("Applicant user: applicant / applicant123")
        
        # Create additional test data if needed
        # Check if competence data exists
        from shared.models import Competence, Status
        existing_competences = db.query(Competence).all()
        if not existing_competences:
            # Create some test competences
            competences = [
                Competence(id=1, name="Python Programming"),
                Competence(id=2, name="FastAPI Development"),
                Competence(id=3, name="Database Design")
            ]
            db.add_all(competences)
            
            # Create statuses
            statuses = [
                Status(id=0, name="PENDING"),
                Status(id=1, name="REJECTED"),
                Status(id=2, name="ACCEPTED")
            ]
            db.add_all(statuses)
            
            db.commit()
            print("Test competences and statuses created successfully.")
        
        print("Database initialization completed successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database() 