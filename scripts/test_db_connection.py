#!/usr/bin/env python3
"""
Test database connection for the Recruitment System.
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

def test_database_connection():
    """Test database connection."""
    # Database configuration
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '3307')),
        'user': os.getenv('DB_USER', 'recruitment_user'),
        'password': os.getenv('DB_PASSWORD', 'recruitment_pass'),
        'database': os.getenv('DB_NAME', 'recruitment_system'),
        'charset': 'utf8mb4',
        'autocommit': True
    }
    
    try:
        logger.info("Attempting to connect to database", 
                   host=db_config['host'], 
                   port=db_config['port'],
                   database=db_config['database'])
        
        # Create connection
        connection = pymysql.connect(**db_config)
        
        # Test the connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            
            if result and result[0] == 1:
                logger.info("Database connection test successful")
                
                # Test if tables exist
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                table_count = len(tables)
                logger.info("Database tables found", table_count=table_count)
                
                if table_count > 0:
                    logger.info("Database is properly initialized")
                    return True
                else:
                    logger.warning("No tables found in database")
                    return False
            else:
                logger.error("Database connection test failed - unexpected result")
                return False
                
    except pymysql.Error as e:
        logger.error("Database connection failed", error=str(e))
        return False
    except Exception as e:
        logger.error("Unexpected error during database test", error=str(e))
        return False
    finally:
        try:
            if 'connection' in locals():
                connection.close()
                logger.info("Database connection closed")
        except Exception as e:
            logger.warning("Failed to close database connection", error=str(e))

def main():
    """Main function."""
    logger.info("Starting database connection test")
    
    success = test_database_connection()
    
    if success:
        logger.info("Database connection test completed successfully")
        sys.exit(0)
    else:
        logger.error("Database connection test failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 