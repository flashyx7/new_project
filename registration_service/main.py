
"""
Registration Service - User registration and profile management
"""

import os
import sys
import sqlite3
import structlog
from datetime import datetime
from fastapi import FastAPI, HTTPException, status, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from shared.database import get_db_connection, create_tables
from shared.security import get_password_hash, validate_password_strength

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

app = FastAPI(
    title="Registration Service",
    description="User registration and profile management service",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RegistrationForm(BaseModel):
    username: str
    password: str
    email: EmailStr
    firstname: str
    lastname: str
    role_id: Optional[int] = 2

class RegistrationResponse(BaseModel):
    status: str
    message: str

@app.on_event("startup")
async def startup_event():
    """Initialize the registration service."""
    logger.info("Registration service starting up")
    try:
        create_tables()
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "registration-service"}

@app.post("/register", response_model=RegistrationResponse)
async def register_user(
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(...),
    firstname: str = Form(...),
    lastname: str = Form(...),
    role_id: int = Form(2)
):
    """Register a new user."""
    try:
        logger.info("Registration attempt", username=username, email=email)

        # Validate password strength
        is_strong, message = validate_password_strength(password)
        if not is_strong:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if username already exists
        cursor.execute("SELECT id FROM credential WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        # Check if email already exists
        cursor.execute("SELECT id FROM person WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create person record
        cursor.execute("""
            INSERT INTO person (firstname, lastname, email, role_id)
            VALUES (?, ?, ?, ?)
        """, (firstname, lastname, email, role_id))

        person_id = cursor.lastrowid

        # Create credentials
        hashed_password = get_password_hash(password)
        cursor.execute("""
            INSERT INTO credential (person_id, username, password)
            VALUES (?, ?, ?)
        """, (person_id, username, hashed_password))

        conn.commit()
        conn.close()

        logger.info("User registered successfully", 
                   person_id=person_id, username=username)

        return RegistrationResponse(
            status="success",
            message="User registered successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Registration failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@app.get("/username/{username}")
async def check_username(username: str):
    """Check if username is available."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM credential WHERE username = ?", (username,))
        existing = cursor.fetchone()
        conn.close()

        return {
            "username": username,
            "available": existing is None
        }

    except Exception as e:
        logger.error("Failed to check username", username=username, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check username availability"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)
