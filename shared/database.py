"""
Database configuration and connection management.
"""

import os
import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import structlog

logger = structlog.get_logger()

# SQLite database configuration
DATABASE_URL = "sqlite:///./recruitment_system.db"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite specific
    echo=False  # Set to True for SQL debugging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_database_connection():
    """Test database connection."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            if result.fetchone()[0] == 1:
                logger.info("Database connection test successful")
                return True
        return False
    except Exception as e:
        logger.error("Database connection test failed", error=str(e))
        return False

def init_db():
    """Initialize database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error("Database initialization failed", error=str(e))
        return False

def execute_sql_file(file_path):
    """Execute SQL file directly using sqlite3."""
    if not os.path.exists(file_path):
        logger.error("SQL file not found", path=file_path)
        return False

    try:
        conn = sqlite3.connect("recruitment_system.db")
        cursor = conn.cursor()

        with open(file_path, 'r') as f:
            sql_content = f.read()

        # Execute SQL statements
        cursor.executescript(sql_content)
        conn.commit()
        conn.close()

        logger.info("SQL file executed successfully", path=file_path)
        return True

    except Exception as e:
        logger.error("SQL file execution failed", path=file_path, error=str(e))
        return False