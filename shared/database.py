
"""
Database connection and utilities for the Recruitment System.
"""

import sqlite3
import os
import structlog
from contextlib import contextmanager
from typing import Optional, Dict, Any, List

logger = structlog.get_logger()

# Database configuration
DB_PATH = "recruitment_system.db"

class DatabaseManager:
    """Manage database connections and operations."""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Ensure database file exists."""
        if not os.path.exists(self.db_path):
            logger.warning("Database file not found, creating new one", path=self.db_path)
            # Create empty database
            conn = sqlite3.connect(self.db_path)
            conn.close()
    
    @contextmanager
    def get_connection(self):
        """Get database connection with context manager."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error("Database operation failed", error=str(e))
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Convert rows to dictionaries
            columns = [description[0] for description in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """Execute an INSERT, UPDATE, or DELETE query."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.rowcount
    
    def execute_insert(self, query: str, params: tuple = None) -> int:
        """Execute an INSERT query and return the last row ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.lastrowid
    
    def health_check(self) -> bool:
        """Check database health."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            return False

# Global database manager instance
db_manager = DatabaseManager()

def get_db_connection():
    """Get database connection (for backward compatibility)."""
    return sqlite3.connect(DB_PATH)

def get_db():
    """Get database connection for dependency injection."""
    return get_db_connection()

def create_tables():
    """Create database tables."""
    # This is handled by the init_database.py script
    pass

def init_db():
    """Initialize database."""
    # This is handled by the init_database.py script
    pass

def test_connection() -> bool:
    """Test database connection."""
    return db_manager.health_check()
