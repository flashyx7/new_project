#!/usr/bin/env python3
"""
Initialize the recruitment system database with schema and test data.
"""

import os
import sys
import sqlite3

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from shared.database import create_tables
from shared.security import get_password_hash

def init_database():
    """Initialize database with schema and test data."""
    print("🔄 Initializing database...")

    # Create tables
    create_tables()

    # Add test data
    conn = sqlite3.connect("recruitment_system.db")
    cursor = conn.cursor()

    try:
        # Check if test data already exists
        cursor.execute("SELECT COUNT(*) FROM person")
        person_count = cursor.fetchone()[0]

        if person_count == 0:
            print("📝 Adding test data...")

            # Create test users
            test_users = [
                ("admin", "admin123", "admin@example.com", "System", "Administrator", 1),
                ("jcandidate", "candidate123", "john.candidate@example.com", "John", "Candidate", 2),
                ("jrecruiter", "recruiter123", "jane.recruiter@example.com", "Jane", "Recruiter", 3)
            ]

            for username, password, email, firstname, lastname, role_id in test_users:
                # Create person
                cursor.execute("""
                    INSERT INTO person (firstname, lastname, email, role_id)
                    VALUES (?, ?, ?, ?)
                """, (firstname, lastname, email, role_id))

                person_id = cursor.lastrowid

                # Create credential
                hashed_password = get_password_hash(password)
                cursor.execute("""
                    INSERT INTO credential (person_id, username, password)
                    VALUES (?, ?, ?)
                """, (person_id, username, hashed_password))

            # Add test job postings
            cursor.execute("""
                INSERT INTO job_posting (title, description, posted_by, location, employment_type, status)
                VALUES 
                ('Software Engineer', 'We are looking for a skilled software engineer...', 3, 'Remote', 'full-time', 'active'),
                ('Frontend Developer', 'Join our team as a frontend developer...', 3, 'New York', 'full-time', 'active'),
                ('Data Analyst', 'Analyze data and provide insights...', 3, 'San Francisco', 'contract', 'active')
            """)

            conn.commit()
            print("✅ Test data added successfully")
        else:
            print("✅ Database already contains data")

    except Exception as e:
        print(f"❌ Error adding test data: {e}")
        conn.rollback()
    finally:
        conn.close()

    print("✅ Database initialization complete")

if __name__ == "__main__":
    init_database()