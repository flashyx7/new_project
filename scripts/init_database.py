
#!/usr/bin/env python3
"""
Initialize the recruitment system database with comprehensive schema and sample data.
"""

import os
import sys
import sqlite3
import structlog
from datetime import datetime, date, timedelta

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from shared.security import get_password_hash
except ImportError:
    # Fallback if security module is not available
    import bcrypt
    def get_password_hash(password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

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
        # Remove existing database to start fresh
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
                logger.info("Removed existing database file")
            except PermissionError:
                logger.warning("Could not remove existing database file, proceeding anyway")

        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        logger.info("Initializing database", path=db_path)

        # Read and execute enhanced schema
        schema_path = os.path.join(project_root, "database", "enhanced_schema.sql")
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                schema_sql = f.read()

            # Execute the schema statements one by one for better error handling
            statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
            for statement in statements:
                if statement:
                    try:
                        cursor.execute(statement)
                    except sqlite3.Error as e:
                        logger.warning("SQL statement failed", statement=statement[:100], error=str(e))
                        # Continue with other statements
            
            conn.commit()
            logger.info("Schema executed successfully")
        else:
            logger.error("Schema file not found", path=schema_path)
            return False

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
            try:
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

            except sqlite3.Error as e:
                logger.error("Failed to create user", user=user['username'], error=str(e))

        # Create sample job postings
        sample_jobs = [
            {
                'title': 'Senior Python Developer',
                'description': 'We are looking for an experienced Python developer to join our backend team.',
                'requirements': 'Python, FastAPI, SQLite, 5+ years experience',
                'responsibilities': 'Develop and maintain backend services, mentor junior developers',
                'salary_min': 90000,
                'salary_max': 120000,
                'location': 'San Francisco, CA',
                'remote_allowed': 1,
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
                'remote_allowed': 1,
                'employment_type': 'full-time',
                'experience_level': 'mid',
                'category_id': 1,
                'posted_by': 2,
                'status': 'active',
                'application_deadline': (datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d')
            }
        ]

        for job in sample_jobs:
            try:
                cursor.execute("""
                    INSERT INTO job_posting 
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
            except sqlite3.Error as e:
                logger.error("Failed to create job posting", job=job['title'], error=str(e))

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
        import traceback
        traceback.print_exc()
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
