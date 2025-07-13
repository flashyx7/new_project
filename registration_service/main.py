from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
import structlog
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from shared.database import get_db, create_tables
from shared.models import Person, Credential, Role
from shared.schemas import RegistrationForm, RegistrationResponse, PersonResponse
from shared.security import get_password_hash

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
    user_data: RegistrationForm,
    db: Session = Depends(get_db)
):
    """Register a new user."""
    try:
        logger.info("Registration attempt", username=user_data.username, email=user_data.email)

        # Check if username already exists
        existing_credential = db.query(Credential).filter(
            Credential.username == user_data.username
        ).first()

        if existing_credential:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        # Check if email already exists
        existing_person = db.query(Person).filter(
            Person.email == user_data.email
        ).first()

        if existing_person:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create person record
        person = Person(
            firstname=user_data.firstname,
            lastname=user_data.lastname,
            date_of_birth=user_data.date_of_birth,
            email=user_data.email,
            role_id=user_data.role_id or 2
        )

        db.add(person)
        db.flush()  # Get the person ID

        # Create credentials
        hashed_password = get_password_hash(user_data.password)
        credential = Credential(
            person_id=person.id,
            username=user_data.username,
            password=hashed_password
        )

        db.add(credential)
        db.commit()

        logger.info("User registered successfully", 
                   person_id=person.id, username=user_data.username)

        return RegistrationResponse(
            status="success",
            message="User registered successfully"
        )

    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error("Database integrity error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed due to data conflict"
        )
    except Exception as e:
        db.rollback()
        logger.error("Registration failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@app.get("/persons/{person_id}", response_model=PersonResponse)
async def get_person(person_id: int, db: Session = Depends(get_db)):
    """Get person information by ID."""
    try:
        person = db.query(Person).filter(Person.id == person_id).first()

        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Person not found"
            )

        return PersonResponse.from_orm(person)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get person", person_id=person_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve person information"
        )

@app.get("/username/{username}")
async def check_username(username: str, db: Session = Depends(get_db)):
    """Check if username is available."""
    try:
        existing = db.query(Credential).filter(
            Credential.username == username
        ).first()

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