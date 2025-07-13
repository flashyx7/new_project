
#!/usr/bin/env python3
"""
Initialize the recruitment system database with comprehensive schema and sample data.
"""

import os
import sys
import sqlite3
import structlog
from datetime import datetime, date, timedelta
import hashlib

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from shared.security import get_password_hash

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

def init_database():
    """Initialize SQLite database with comprehensive schema and sample data."""
    db_path = "recruitment_system.db"
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        logger.info("Initializing database", path=db_path)
        
        # Read and execute enhanced schema
        schema_path = os.path.join(project_root, "database", "enhanced_schema.sql")
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
                # Execute schema in parts (SQLite doesn't handle multiple statements well)
                for statement in schema_sql.split(';'):
                    if statement.strip():
                        try:
                            cursor.execute(statement)
                        except Exception as e:
                            if "already exists" not in str(e).lower():
                                logger.warning("Schema statement failed", statement=statement[:100], error=str(e))
        
        # Create sample users
        sample_users = [
            {
                'firstname': 'Admin',
                'lastname': 'User',
                'email': 'admin@recruitment.com',
                'username': 'admin',
                'password': 'admin123',
                'role_id': 3,
                'date_of_birth': '1980-01-01'
            },
            {
                'firstname': 'Jane',
                'lastname': 'Recruiter',
                'email': 'jane.recruiter@company.com',
                'username': 'jrecruiter',
                'password': 'recruiter123',
                'role_id': 1,
                'date_of_birth': '1985-03-15'
            },
            {
                'firstname': 'John',
                'lastname': 'Candidate',
                'email': 'john.candidate@email.com',
                'username': 'jcandidate',
                'password': 'candidate123',
                'role_id': 2,
                'date_of_birth': '1995-07-20'
            },
            {
                'firstname': 'Sarah',
                'lastname': 'Manager',
                'email': 'sarah.manager@company.com',
                'username': 'smanager',
                'password': 'manager123',
                'role_id': 4,
                'date_of_birth': '1978-11-10'
            }
        ]
        
        for user in sample_users:
            # Check if user already exists
            cursor.execute("SELECT id FROM person WHERE email = ?", (user['email'],))
            if cursor.fetchone():
                continue
                
            # Insert person
            cursor.execute("""
                INSERT INTO person (firstname, lastname, email, date_of_birth, role_id, phone, address)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user['firstname'], user['lastname'], user['email'], 
                user['date_of_birth'], user['role_id'],
                '+1-555-0123', '123 Main St, City, State 12345'
            ))
            
            person_id = cursor.lastrowid
            
            # Insert credentials
            hashed_password = get_password_hash(user['password'])
            cursor.execute("""
                INSERT INTO credential (person_id, username, password)
                VALUES (?, ?, ?)
            """, (person_id, user['username'], hashed_password))
            
        # Create sample job postings
        sample_jobs = [
            {
                'title': 'Senior Python Developer',
                'description': 'We are looking for an experienced Python developer to join our backend team.',
                'requirements': 'Python, FastAPI, PostgreSQL, 5+ years experience',
                'responsibilities': 'Develop and maintain backend services, mentor junior developers',
                'salary_min': 90000,
                'salary_max': 120000,
                'location': 'San Francisco, CA',
                'remote_allowed': True,
                'employment_type': 'full-time',
                'experience_level': 'senior',
                'category_id': 1,
                'posted_by': 2,  # Jane Recruiter
                'status': 'active',
                'application_deadline': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            },
            {
                'title': 'Frontend React Developer',
                'description': 'Join our frontend team to build amazing user experiences.',
                'requirements': 'React, TypeScript, CSS, 3+ years experience',
                'responsibilities': 'Build responsive web applications, collaborate with designers',
                'salary_min': 70000,
                'salary_max': 95000,
                'location': 'Remote',
                'remote_allowed': True,
                'employment_type': 'full-time',
                'experience_level': 'mid',
                'category_id': 1,
                'posted_by': 2,
                'status': 'active',
                'application_deadline': (datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d')
            }
        ]
        
        for job in sample_jobs:
            cursor.execute("""
                INSERT OR IGNORE INTO job_posting 
                (title, description, requirements, responsibilities, salary_min, salary_max, 
                 currency, location, remote_allowed, employment_type, experience_level, 
                 category_id, posted_by, status, application_deadline)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job['title'], job['description'], job['requirements'], job['responsibilities'],
                job['salary_min'], job['salary_max'], 'USD', job['location'], 
                job['remote_allowed'], job['employment_type'], job['experience_level'],
                job['category_id'], job['posted_by'], job['status'], job['application_deadline']
            ))
        
        # Create sample application
        cursor.execute("""
            INSERT OR IGNORE INTO availability (person_id, from_date, to_date, is_flexible)
            VALUES (3, ?, ?, ?)
        """, (
            (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d'),
            (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'),
            True
        ))
        
        availability_id = cursor.lastrowid or 1
        
        cursor.execute("""
            INSERT OR IGNORE INTO application 
            (person_id, job_posting_id, cover_letter, status_id, match_score)
            VALUES (?, ?, ?, ?, ?)
        """, (
            3, 1, 
            "I am very interested in this position and believe my skills align well with your requirements.",
            1, 85.5
        ))
        
        # Add competence profiles
        competence_data = [
            (3, 1, 5.0, 'advanced'),  # John - Python
            (3, 2, 3.0, 'intermediate'),  # John - JavaScript
            (3, 5, 4.0, 'advanced'),  # John - SQL
        ]
        
        for person_id, competence_id, years, level in competence_data:
            cursor.execute("""
                INSERT OR IGNORE INTO competence_profile 
                (person_id, competence_id, years_of_experience, proficiency_level)
                VALUES (?, ?, ?, ?)
            """, (person_id, competence_id, years, level))
        
        conn.commit()
        logger.info("Database initialized successfully with sample data")
        
        # Print sample credentials
        print("\n" + "="*50)
        print("DATABASE INITIALIZED SUCCESSFULLY")
        print("="*50)
        print("\nSample Login Credentials:")
        print("-" * 30)
        for user in sample_users:
            print(f"Role: {['', 'Recruiter', 'Applicant', 'Admin', 'Hiring Manager'][user['role_id']]}")
            print(f"Username: {user['username']}")
            print(f"Password: {user['password']}")
            print(f"Email: {user['email']}")
            print("-" * 30)
        
        return True
        
    except Exception as e:
        logger.error("Database initialization failed", error=str(e))
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    success = init_database()
    if success:
        print("\n✅ Database initialization completed successfully!")
        print("You can now start the application services.")
    else:
        print("\n❌ Database initialization failed!")
        sys.exit(1)
