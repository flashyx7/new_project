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
                INSERT INTO job_posting (title, description, posted_by, location, employment_type, status, salary_min, salary_max, experience_level)
                VALUES 
                ('Software Engineer', 'We are looking for a skilled software engineer to join our dynamic team. You will work on cutting-edge projects and collaborate with talented developers.', 3, 'Remote', 'full-time', 'active', 60000, 90000, 'mid-level'),
                ('Frontend Developer', 'Join our team as a frontend developer. You will be responsible for creating amazing user interfaces using modern technologies like React and Vue.js.', 3, 'New York', 'full-time', 'active', 50000, 75000, 'junior'),
                ('Data Analyst', 'Analyze data and provide insights to drive business decisions. Experience with SQL, Python, and data visualization tools required.', 3, 'San Francisco', 'contract', 'active', 55000, 80000, 'mid-level'),
                ('Senior Backend Developer', 'Lead backend development initiatives using Python, FastAPI, and microservices architecture.', 3, 'Seattle', 'full-time', 'active', 80000, 120000, 'senior'),
                ('UI/UX Designer', 'Design beautiful and intuitive user interfaces. Proficiency in Figma, Adobe Creative Suite required.', 3, 'Los Angeles', 'part-time', 'active', 40000, 65000, 'mid-level')
            """)

            # Add test applications
            cursor.execute("""
                INSERT INTO application (person_id, job_posting_id, cover_letter, status_id)
                VALUES 
                (2, 1, 'I am very interested in this software engineer position. I have 3 years of experience in Python and web development.', 1),
                (2, 2, 'I would love to work as a frontend developer. I have experience with React and modern JavaScript frameworks.', 2)
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
```

```python
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
                INSERT INTO job_posting (title, description, posted_by, location, employment_type, status, salary_min, salary_max, experience_level)
                VALUES 
                ('Software Engineer', 'We are looking for a skilled software engineer to join our dynamic team. You will work on cutting-edge projects and collaborate with talented developers.', 3, 'Remote', 'full-time', 'active', 60000, 90000, 'mid-level'),
                ('Frontend Developer', 'Join our team as a frontend developer. You will be responsible for creating amazing user interfaces using modern technologies like React and Vue.js.', 3, 'New York', 'full-time', 'active', 50000, 75000, 'junior'),
                ('Data Analyst', 'Analyze data and provide insights to drive business decisions. Experience with SQL, Python, and data visualization tools required.', 3, 'San Francisco', 'contract', 'active', 55000, 80000, 'mid-level'),
                ('Senior Backend Developer', 'Lead backend development initiatives using Python, FastAPI, and microservices architecture.', 3, 'Seattle', 'full-time', 'active', 80000, 120000, 'senior'),
                ('UI/UX Designer', 'Design beautiful and intuitive user interfaces. Proficiency in Figma, Adobe Creative Suite required.', 3, 'Los Angeles', 'part-time', 'active', 40000, 65000, 'mid-level')
            """)

            # Add test applications
            cursor.execute("""
                INSERT INTO application (person_id, job_posting_id, cover_letter, resume_path, status_id)
                VALUES 
                (2, 1, 'I am very interested in this software engineer position. I have 3 years of experience in Python and web development.', 'path/to/resume1.pdf', 1),
                (2, 2, 'I would love to work as a frontend developer. I have experience with React and modern JavaScript frameworks.', 'path/to/resume2.pdf', 2)
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
```

```python
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
                INSERT INTO job_posting (title, description, posted_by, location, employment_type, status, salary_min, salary_max, experience_level)
                VALUES 
                ('Software Engineer', 'We are looking for a skilled software engineer to join our dynamic team. You will work on cutting-edge projects and collaborate with talented developers.', 3, 'Remote', 'full-time', 'active', 60000, 90000, 'mid-level'),
                ('Frontend Developer', 'Join our team as a frontend developer. You will be responsible for creating amazing user interfaces using modern technologies like React and Vue.js.', 3, 'New York', 'full-time', 'active', 50000, 75000, 'junior'),
                ('Data Analyst', 'Analyze data and provide insights to drive business decisions. Experience with SQL, Python, and data visualization tools required.', 3, 'San Francisco', 'contract', 'active', 55000, 80000, 'mid-level'),
                ('Senior Backend Developer', 'Lead backend development initiatives using Python, FastAPI, and microservices architecture.', 3, 'Seattle', 'full-time', 'active', 80000, 120000, 'senior'),
                ('UI/UX Designer', 'Design beautiful and intuitive user interfaces. Proficiency in Figma, Adobe Creative Suite required.', 3, 'Los Angeles', 'part-time', 'active', 40000, 65000, 'mid-level')
            """)

            # Add test applications
            cursor.execute("""
                INSERT INTO application (person_id, job_posting_id, cover_letter, resume_path, status_id)
                VALUES 
                (2, 1, 'I am very interested in this software engineer position. I have 3 years of experience in Python and web development.', 'path/to/resume1.pdf', 1),
                (2, 2, 'I would love to work as a frontend developer. I have experience with React and modern JavaScript frameworks.', 'path/to/resume2.pdf', 2)
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
```

```python
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
                INSERT INTO job_posting (title, description, posted_by, location, employment_type, status, salary_min, salary_max, experience_level)
                VALUES 
                ('Software Engineer', 'We are looking for a skilled software engineer to join our dynamic team. You will work on cutting-edge projects and collaborate with talented developers.', 3, 'Remote', 'full-time', 'active', 60000, 90000, 'mid-level'),
                ('Frontend Developer', 'Join our team as a frontend developer. You will be responsible for creating amazing user interfaces using modern technologies like React and Vue.js.', 3, 'New York', 'full-time', 'active', 50000, 75000, 'junior'),
                ('Data Analyst', 'Analyze data and provide insights to drive business decisions. Experience with SQL, Python, and data visualization tools required.', 3, 'San Francisco', 'contract', 'active', 55000, 80000, 'mid-level'),
                ('Senior Backend Developer', 'Lead backend development initiatives using Python, FastAPI, and microservices architecture.', 3, 'Seattle', 'full-time', 'active', 80000, 120000, 'senior'),
                ('UI/UX Designer', 'Design beautiful and intuitive user interfaces. Proficiency in Figma, Adobe Creative Suite required.', 3, 'Los Angeles', 'part-time', 'active', 40000, 65000, 'mid-level')
            """)

            # Add test applications
            cursor.execute("""
                INSERT INTO application (person_id, job_posting_id, cover_letter, resume_path, status_id)
                VALUES 
                (2, 1, 'I am very interested in this software engineer position. I have 3 years of experience in Python and web development.', 'path/to/resume1.pdf', 1),
                (2, 2, 'I would love to work as a frontend developer. I have experience with React and modern JavaScript frameworks.', 'path/to/resume2.pdf', 2)
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
```

```python
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
                INSERT INTO job_posting (title, description, posted_by, location, employment_type, status, salary_min, salary_max, experience_level)
                VALUES 
                ('Software Engineer', 'We are looking for a skilled software engineer to join our dynamic team. You will work on cutting-edge projects and collaborate with talented developers.', 3, 'Remote', 'full-time', 'active', 60000, 90000, 'mid-level'),
                ('Frontend Developer', 'Join our team as a frontend developer. You will be responsible for creating amazing user interfaces using modern technologies like React and Vue.js.', 3, 'New York', 'full-time', 'active', 50000, 75000, 'junior'),
                ('Data Analyst', 'Analyze data and provide insights to drive business decisions. Experience with SQL, Python, and data visualization tools required.', 3, 'San Francisco', 'contract', 'active', 55000, 80000, 'mid-level'),
                ('Senior Backend Developer', 'Lead backend development initiatives using Python, FastAPI, and microservices architecture.', 3, 'Seattle', 'full-time', 'active', 80000, 120000, 'senior'),
                ('UI/UX Designer', 'Design beautiful and intuitive user interfaces. Proficiency in Figma, Adobe Creative Suite required.', 3, 'Los Angeles', 'part-time', 'active', 40000, 65000, 'mid-level')
            """)

            # Add test applications
            cursor.execute("""
                INSERT INTO application (person_id, job_posting_id, cover_letter,status_id,resume_path)
                VALUES 
                (2, 1, 'I am very interested in this software engineer position. I have 3 years of experience in Python and web development.', 1,'path/to/resume1.pdf'),
                (2, 2, 'I would love to work as a frontend developer. I have experience with React and modern JavaScript frameworks.', 2,'path/to/resume2.pdf')
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
```

```python
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
    conn = sqlite3.connect("recruitment_system.db")
    cursor = conn.cursor()

    try:
        # Drop existing tables if they exist
        cursor.execute("DROP TABLE IF EXISTS application")
        cursor.execute("DROP TABLE IF EXISTS job_posting")
        cursor.execute("DROP TABLE IF EXISTS person")
        cursor.execute("DROP TABLE IF EXISTS credential")
        cursor.execute("DROP TABLE IF EXISTS role")
        cursor.execute("DROP TABLE IF EXISTS application_status")

        conn.commit()
    except Exception as e:
        print(f"Error dropping tables: {e}")
        conn.rollback()

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
                INSERT INTO job_posting (title, description, posted_by, location, employment_type, status, salary_min, salary_max, experience_level)
                VALUES 
                ('Software Engineer', 'We are looking for a skilled software engineer to join our dynamic team. You will work on cutting-edge projects and collaborate with talented developers.', 3, 'Remote', 'full-time', 'active', 60000, 90000, 'mid-level'),
                ('Frontend Developer', 'Join our team as a frontend developer. You will be responsible for creating amazing user interfaces using modern technologies like React and Vue.js.', 3, 'New York', 'full-time', 'active', 50000, 75000, 'junior'),
                ('Data Analyst', 'Analyze data and provide insights to drive business decisions. Experience with SQL, Python, and data visualization tools required.', 3, 'San Francisco', 'contract', 'active', 55000, 80000, 'mid-level'),
                ('Senior Backend Developer', 'Lead backend development initiatives using Python, FastAPI, and microservices architecture.', 3, 'Seattle', 'full-time', 'active', 80000, 120000, 'senior'),
                ('UI/UX Designer', 'Design beautiful and intuitive user interfaces. Proficiency in Figma, Adobe Creative Suite required.', 3, 'Los Angeles', 'part-time', 'active', 40000, 65000, 'mid-level')
            """)

            # Add test applications
            cursor.execute("""
                INSERT INTO application (person_id, job_posting_id, cover_letter, status_id, resume_path)
                VALUES 
                (2, 1, 'I am very interested in this software engineer position. I have 3 years of experience in Python and web development.', 1, 'path/to/resume1.pdf'),
                (2, 2, 'I would love to work as a frontend developer. I have experience with React and modern JavaScript frameworks.', 2, 'path/to/resume2.pdf')
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
```

```python
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
    conn = sqlite3.connect("recruitment_system.db")
    cursor = conn.cursor()

    try:
        # Drop existing tables if they exist
        cursor.execute("DROP TABLE IF EXISTS application")
        cursor.execute("DROP TABLE IF EXISTS job_posting")
        cursor.execute("DROP TABLE IF EXISTS person")
        cursor.execute("DROP TABLE IF EXISTS credential")
        cursor.execute("DROP TABLE IF EXISTS role")
        cursor.execute("DROP TABLE IF EXISTS application_status")

        conn.commit()
    except Exception as e:
        print(f"Error dropping tables: {e}")
        conn.rollback()

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
                INSERT INTO job_posting (title, description, posted_by, location, employment_type, status, salary_min, salary_max, experience_level)
                VALUES 
                ('Software Engineer', 'We are looking for a skilled software engineer to join our dynamic team. You will work on cutting-edge projects and collaborate with talented developers.', 3, 'Remote', 'full-time', 'active', 60000, 90000, 'mid-level'),
                ('Frontend Developer', 'Join our team as a frontend developer. You will be responsible for creating amazing user interfaces using modern technologies like React and Vue.js.', 3, 'New York', 'full-time', 'active', 50000, 75000, 'junior'),
                ('Data Analyst', 'Analyze data and provide insights to drive business decisions. Experience with SQL, Python, and data visualization tools required.', 3, 'San Francisco', 'contract', 'active', 55000, 80000, 'mid-level'),
                ('Senior Backend Developer', 'Lead backend development initiatives using Python, FastAPI, and microservices architecture.', 3, 'Seattle', 'full-time', 'active', 80000, 120000, 'senior'),
                ('UI/UX Designer', 'Design beautiful and intuitive user interfaces. Proficiency in Figma, Adobe Creative Suite required.', 3, 'Los Angeles', 'part-time', 'active', 40000, 65000, 'mid-level')
            """)

            # Add test applications
            cursor.execute("""
                INSERT INTO application (person_id, job_posting_id, cover_letter, resume_path, status_id)
                VALUES 
                (2, 1, 'I am very interested in this software engineer position. I have 3 years of experience in Python and web development.', 'path/to/resume1.pdf', 1),
                (2, 2, 'I would love to work as a frontend developer. I have experience with React and modern JavaScript frameworks.', 'path/to/resume2.pdf', 2)
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
```

```python
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
    conn = sqlite3.connect("recruitment_system.db")
    cursor = conn.cursor()

    try:
        # Drop existing tables if they exist
        cursor.execute("DROP TABLE IF EXISTS application")
        cursor.execute("DROP TABLE IF EXISTS job_posting")
        cursor.execute("DROP TABLE IF EXISTS person")
        cursor.execute("DROP TABLE IF EXISTS credential")
        cursor.execute("DROP TABLE IF EXISTS role")
        cursor.execute("DROP TABLE IF EXISTS application_status")

        conn.commit()
    except Exception as e:
        print(f"Error dropping tables: {e}")
        conn.rollback()

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
                INSERT INTO job_posting (title, description, posted_by, location, employment_type, status, salary_min, salary_max, experience_level)
                VALUES 
                ('Software Engineer', 'We are looking for a skilled software engineer to join our dynamic team. You will work on cutting-edge projects and collaborate with talented developers.', 3, 'Remote', 'full-time', 'active', 60000, 90000, 'mid-level'),
                ('Frontend Developer', 'Join our team as a frontend developer. You will be responsible for creating amazing user interfaces using modern technologies like React and Vue.js.', 3, 'New York', 'full-time', 'active', 50000, 75000, 'junior'),
                ('Data Analyst', 'Analyze data and provide insights to drive business decisions. Experience with SQL, Python, and data visualization tools required.', 3, 'San Francisco', 'contract', 'active', 55000, 80000, 'mid-level'),
                ('Senior Backend Developer', 'Lead backend development initiatives using Python, FastAPI, and microservices architecture.', 3, 'Seattle', 'full-time', 'active', 80000, 120000, 'senior'),
                ('UI/UX Designer', 'Design beautiful and intuitive user interfaces. Proficiency in Figma, Adobe Creative Suite required.', 3, 'Los Angeles', 'part-time', 'active', 40000, 65000, 'mid-level')
            """)

            # Add test applications
            cursor.execute("""
                INSERT INTO application (person_id, job_posting_id, cover_letter, status_id, resume_path)
                VALUES 
                (2, 1, 'I am very interested in this software engineer position. I have 3 years of experience in Python and web development.', 1, 'path/to/resume1.pdf'),
                (2, 2, 'I would love to work as a frontend developer. I have experience with React and modern JavaScript frameworks.', 2, 'path/to/resume2.pdf')
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