#!/usr/bin/env python3
"""
Database initialization script for the Recruitment System.
"""

import pymysql
import structlog
import os
import sys

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

# Database configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3307"))
DB_USER = os.getenv("DB_USER", "recruitment_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "recruitment_pass")
DB_NAME = os.getenv("DB_NAME", "recruitment_system")

def create_database():
    """Create the database if it doesn't exist."""
    try:
        # Connect to MySQL server (without specifying database)
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
            logger.info(f"Database '{DB_NAME}' created or already exists")
            
        connection.close()
        return True
        
    except Exception as e:
        logger.error(f"Failed to create database: {e}")
        return False

def execute_sql_file(connection, file_path):
    """Execute SQL commands from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Split by semicolon and execute each statement
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        with connection.cursor() as cursor:
            for statement in statements:
                if statement:
                    cursor.execute(statement)
                    logger.info(f"Executed SQL statement: {statement[:50]}...")
        
        connection.commit()
        logger.info(f"Successfully executed SQL file: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to execute SQL file {file_path}: {e}")
        return False

def initialize_database():
    """Initialize the database with schema and data."""
    try:
        # Create database
        if not create_database():
            return False
        
        # Connect to the specific database
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4'
        )
        
        # Execute schema file
        schema_file = "database/recruitmentsystem.sql"
        if os.path.exists(schema_file):
            if not execute_sql_file(connection, schema_file):
                connection.close()
                return False
        else:
            logger.warning(f"Schema file not found: {schema_file}")
        
        # Execute data file
        data_file = "database/data.sql"
        if os.path.exists(data_file):
            if not execute_sql_file(connection, data_file):
                connection.close()
                return False
        else:
            logger.warning(f"Data file not found: {data_file}")
        
        connection.close()
        logger.info("Database initialization completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

def test_connection():
    """Test database connection."""
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result and result[0] == 1:
                logger.info("Database connection test successful")
                connection.close()
                return True
        
        connection.close()
        return False
        
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False

def main():
    """Main function."""
    logger.info("Starting database initialization")
    
    # Check if MySQL is running
    logger.info("Testing database connection...")
    if not test_connection():
        logger.error("Cannot connect to database. Please ensure MySQL is running.")
        logger.info("You can start MySQL using Docker with:")
        logger.info("docker run --name mysql-recruitment -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=recruitment_system -e MYSQL_USER=recruitment_user -e MYSQL_PASSWORD=recruitment_pass -p 3307:3306 -d mysql:8.0")
        return False
    
    # Initialize database
    if initialize_database():
        logger.info("Database initialization completed successfully!")
        return True
    else:
        logger.error("Database initialization failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 