
"""
Database connection and setup for the recruitment system.
"""

import sqlite3
import os
from typing import Generator
from contextlib import contextmanager

DATABASE_PATH = "recruitment_system.db"

def get_db_connection():
    """Get database connection."""
    return sqlite3.connect(DATABASE_PATH)

@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Database context manager."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def create_tables():
    """Create all necessary tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create tables
    cursor.executescript("""
        -- Create roles table
        CREATE TABLE IF NOT EXISTS role (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(50) NOT NULL UNIQUE,
            description TEXT
        );

        -- Create person table
        CREATE TABLE IF NOT EXISTS person (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            firstname VARCHAR(255) NOT NULL,
            lastname VARCHAR(255) NOT NULL,
            date_of_birth DATE,
            email VARCHAR(255) NOT NULL UNIQUE,
            phone VARCHAR(20),
            address TEXT,
            role_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (role_id) REFERENCES role(id)
        );

        -- Create credential table
        CREATE TABLE IF NOT EXISTS credential (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER NOT NULL,
            username VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (person_id) REFERENCES person(id)
        );

        -- Create job_category table
        CREATE TABLE IF NOT EXISTS job_category (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            description TEXT
        );

        -- Create job_posting table
        CREATE TABLE IF NOT EXISTS job_posting (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            requirements TEXT,
            posted_by INTEGER NOT NULL,
            category_id INTEGER,
            salary_min DECIMAL(10,2),
            salary_max DECIMAL(10,2),
            location VARCHAR(255),
            employment_type VARCHAR(50) DEFAULT 'full-time',
            experience_level VARCHAR(50),
            status VARCHAR(20) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (posted_by) REFERENCES person(id),
            FOREIGN KEY (category_id) REFERENCES job_category(id)
        );

        -- Create application_status table
        CREATE TABLE IF NOT EXISTS application_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(50) NOT NULL,
            description TEXT
        );

        -- Create application table
        CREATE TABLE IF NOT EXISTS application (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER NOT NULL,
            job_posting_id INTEGER NOT NULL,
            status_id INTEGER DEFAULT 1,
            cover_letter TEXT,
            applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (person_id) REFERENCES person(id),
            FOREIGN KEY (job_posting_id) REFERENCES job_posting(id),
            FOREIGN KEY (status_id) REFERENCES application_status(id)
        );

        -- Create competence table
        CREATE TABLE IF NOT EXISTS competence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            description TEXT
        );

        -- Create competence_profile table
        CREATE TABLE IF NOT EXISTS competence_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER NOT NULL,
            competence_id INTEGER NOT NULL,
            years_of_experience DECIMAL(3,1),
            proficiency_level VARCHAR(20) DEFAULT 'intermediate',
            FOREIGN KEY (person_id) REFERENCES person(id),
            FOREIGN KEY (competence_id) REFERENCES competence(id)
        );

        -- Create availability table
        CREATE TABLE IF NOT EXISTS availability (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER NOT NULL,
            from_date DATE NOT NULL,
            to_date DATE NOT NULL,
            FOREIGN KEY (person_id) REFERENCES person(id)
        );
    """)
    
    # Insert default data
    cursor.execute("SELECT COUNT(*) FROM role")
    if cursor.fetchone()[0] == 0:
        cursor.executescript("""
            INSERT INTO role (name, description) VALUES 
            ('Admin', 'System administrator'),
            ('Applicant', 'Job applicant'),
            ('Recruiter', 'HR recruiter');

            INSERT INTO application_status (name, description) VALUES
            ('Submitted', 'Application submitted'),
            ('Under Review', 'Application being reviewed'),
            ('Accepted', 'Application accepted'),
            ('Rejected', 'Application rejected');

            INSERT INTO job_category (name, description) VALUES
            ('Engineering', 'Software and technical roles'),
            ('Marketing', 'Marketing and sales roles'),
            ('Operations', 'Operations and support roles');

            INSERT INTO competence (name, description) VALUES
            ('Python', 'Python programming'),
            ('JavaScript', 'JavaScript programming'),
            ('Project Management', 'Project management skills'),
            ('Communication', 'Communication skills');
        """)
    
    conn.commit()
    conn.close()
