from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional
import structlog
import os
import sys
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from shared.database import get_db, create_tables
from shared.models import Person, Credential
from shared.schemas import AuthRequest, AuthTokenResponse, AuthFailResponse
from shared.security import verify_password, create_access_token, verify_token

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
    title="Authentication Service",
    description="User authentication and authorization service",
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

@app.on_event("startup")
async def startup_event():
    """Initialize the authentication service."""
    logger.info("Authentication service starting up")
    try:
        create_tables()
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "auth-service"}

@app.post("/auth/login", response_model=AuthTokenResponse)
async def login(
    auth_request: AuthRequest,
    db: Session = Depends(get_db)
):
    """Authenticate user and return JWT token."""
    try:
        logger.info("Login attempt", username=auth_request.username)

        # Get user credentials
        credential = db.query(Credential).filter(
            Credential.username == auth_request.username
        ).first()

        if not credential:
            logger.warning("Login failed - user not found", username=auth_request.username)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )

        # Verify password
        if not verify_password(auth_request.password, credential.password):
            logger.warning("Login failed - invalid password", username=auth_request.username)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )

        # Get person information
        person = db.query(Person).filter(Person.id == credential.person_id).first()
        if not person:
            logger.error("Login failed - person not found", person_id=credential.person_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication error"
            )

        # Update last login
        credential.last_login = datetime.utcnow()
        db.commit()

        # Create JWT token
        token_data = {
            "sub": credential.username,
            "person_id": person.id,
            "role_id": person.role_id,
            "email": person.email,
            "username": credential.username
        }

        token = create_access_token(token_data)

        logger.info("Login successful", 
                   username=auth_request.username, 
                   person_id=person.id,
                   role_id=person.role_id)

        return AuthTokenResponse(token=token)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login failed", username=auth_request.username, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication error"
        )

@app.post("/auth/verify")
async def verify_token_endpoint(token: str):
    """Verify JWT token and return user information."""
    try:
        token_data = verify_token(token)

        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )

        return {
            "valid": True,
            "data": token_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Token verification failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed"
        )

@app.get("/auth/me")
async def get_current_user(token: str, db: Session = Depends(get_db)):
    """Get current user information from token."""
    try:
        token_data = verify_token(token)

        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )

        person_id = token_data.get("person_id")
        if not person_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token data"
            )

        person = db.query(Person).filter(Person.id == person_id).first()
        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return {
            "id": person.id,
            "firstname": person.firstname,
            "lastname": person.lastname,
            "email": person.email,
            "role_id": person.role_id,
            "username": token_data.get("username")
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get current user", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user information"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)