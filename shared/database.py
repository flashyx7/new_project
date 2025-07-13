from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from fastapi import HTTPException
import structlog
import os
import time

# Configure logging
logger = structlog.get_logger()

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./recruitment_system.db"
)

# Database connection settings
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))

def create_database_engine():
    """Create database engine with proper configuration."""
    try:
        # Check if it's SQLite or MySQL
        if DATABASE_URL.startswith("sqlite"):
            engine = create_engine(
                DATABASE_URL,
                connect_args={"check_same_thread": False},
                echo=False  # Set to True for SQL query logging
            )
        else:
            # MySQL configuration
            engine = create_engine(
                DATABASE_URL,
                pool_pre_ping=True,
                pool_size=DB_POOL_SIZE,
                max_overflow=DB_MAX_OVERFLOW,
                pool_timeout=DB_POOL_TIMEOUT,
                pool_recycle=DB_POOL_RECYCLE,
                echo=False,  # Set to True for SQL query logging
                connect_args={
                    "charset": "utf8mb4",
                    "autocommit": False
                }
            )
        
        # Test the connection with retry logic
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                with engine.connect() as conn:
                    from sqlalchemy import text
                    conn.execute(text("SELECT 1"))
                logger.info("Database engine created successfully")
                return engine
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Database connection failed, retrying in {retry_delay} seconds...", 
                                 attempt=attempt + 1, error=str(e))
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    logger.error("Failed to create database engine after all retries", error=str(e))
                    # Return engine anyway - let the application handle connection issues
                    return engine
                    
    except Exception as e:
        logger.error("Failed to create database engine", error=str(e))
        # Return None to indicate failure
        return None

# Create SQLAlchemy engine
engine = create_database_engine()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Create metadata
metadata = MetaData()

def get_db():
    """Dependency to get database session with error handling."""
    if engine is None:
        logger.warning("Database engine is None, cannot provide database session")
        raise HTTPException(status_code=503, detail="Database not available")
        
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error("Database session error", error=str(e))
        db.rollback()
        raise HTTPException(status_code=503, detail="Database error")
    except Exception as e:
        logger.error("Unexpected database error", error=str(e))
        db.rollback()
        raise HTTPException(status_code=503, detail="Database error")
    finally:
        try:
            db.close()
        except Exception as e:
            logger.warning("Failed to close database session", error=str(e))

def create_tables():
    """Create all tables in the database with retry logic."""
    if engine is None:
        logger.warning("Database engine is None, skipping table creation")
        return
        
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
            return
        except OperationalError as e:
            if attempt < max_retries - 1:
                logger.warning(f"Database connection failed, retrying in {retry_delay} seconds...", 
                             attempt=attempt + 1, error=str(e))
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                logger.warning("Failed to create database tables after all retries, continuing without database", error=str(e))
                return
        except Exception as e:
            logger.warning("Failed to create database tables, continuing without database", error=str(e))
            return

def init_db():
    """Initialize database tables (alias for create_tables)."""
    create_tables()

def test_database_connection():
    """Test database connection."""
    try:
        if engine is None:
            logger.error("Database engine is None")
            return False
            
        with engine.connect() as conn:
            from sqlalchemy import text
            result = conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            if row and row[0] == 1:
                logger.info("Database connection test successful")
                return True
            else:
                logger.error("Database connection test failed - unexpected result")
                return False
    except Exception as e:
        logger.error("Database connection test failed", error=str(e))
        return False 