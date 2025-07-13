from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
import structlog
import consul
import httpx
import os

# Import shared modules
import sys
import os
# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
from shared.models import Person, Credential, Role
from shared.schemas import (
    RegistrationForm, RegistrationResponse, UserCredentialsDTO
)
from shared.security import get_password_hash, verify_password, create_access_token, verify_token
from shared.database import get_db, init_db

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
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
    description="User registration and management service",
    version="1.0.0"
)

# Security
security = HTTPBearer()

# Consul client
consul_host = os.getenv("CONSUL_HOST", "localhost")
consul_port = int(os.getenv("CONSUL_PORT", "8500"))
consul_client = consul.Consul(host=consul_host, port=consul_port)

# Discovery service URL
discovery_service_url = os.getenv("DISCOVERY_SERVICE_URL", "http://localhost:9090")

class UserManager:
    """Domain service for user management."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def register(self, registration_form: RegistrationForm) -> None:
        """Register a new user."""
        try:
            # Check if username already exists
            existing_credential = self.db.query(Credential).filter(
                Credential.username == registration_form.username
            ).first()
            
            if existing_credential:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username already exists"
                )
            
            # Check if email already exists
            existing_person = self.db.query(Person).filter(
                Person.email == registration_form.email
            ).first()
            
            if existing_person:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already exists"
                )
        
            # Create new person
            person = Person(
                firstname=registration_form.firstname,
                lastname=registration_form.lastname,
                date_of_birth=registration_form.date_of_birth,
                email=registration_form.email,
                role_id=getattr(registration_form, 'role_id', 2)  # Use role_id from form or default to Applicant
            )
            
            self.db.add(person)
            self.db.flush()  # Get the person ID
            
            # Create credentials
            hashed_password = get_password_hash(registration_form.password)
            credential = Credential(
                person_id=person.id,
                username=registration_form.username,
                password=hashed_password
            )
            
            self.db.add(credential)
            self.db.commit()
            
            logger.info("User registered successfully", username=registration_form.username)
        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to register user", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    def get_user_by_id(self, user_id: int, lang: str) -> Person:
        """Get user by ID."""
        person = self.db.query(Person).filter(Person.id == user_id).first()
        if not person:
            raise ValueError("User not found")
        return person
    
    def validate_user_id(self, user_id: int) -> bool:
        """Validate if user ID exists."""
        person = self.db.query(Person).filter(Person.id == user_id).first()
        return person is not None
    
    def get_user_ids_by_name(self, name: str) -> List[int]:
        """Get user IDs by first name."""
        persons = self.db.query(Person).filter(Person.firstname == name).all()
        return [person.id for person in persons]
    
    def get_user_and_credentials_by_username(self, username: str) -> dict:
        """Get user and credentials by username."""
        credential = self.db.query(Credential).filter(
            Credential.username == username
        ).first()
        
        if not credential:
            raise ValueError("User not found")
        
        person = credential.person
        role = person.role
        
        return {
            "username": username,
            "user_id": person.id,
            "roles": [role.name]
        }

@app.on_event("startup")
async def startup_event():
    """Initialize the registration service."""
    logger.info("Registration service starting up")
    try:
        # Test Consul connection
        consul_client.agent.self()
        logger.info("Successfully connected to Consul", host=consul_host, port=consul_port)
        
        # Initialize database (optional)
        try:
            init_db()
            logger.info("Database initialized")
        except Exception as e:
            logger.warning("Database initialization failed, continuing without database", error=str(e))
        
        # Register service with discovery service
        service_registration = {
            "service_name": "registration-service",
            "service_id": "registration-service-1",
            "address": "127.0.0.1",
            "port": 8888,
            "tags": ["registration", "user-management"]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{discovery_service_url}/register",
                json=service_registration
            )
            if response.status_code == 200:
                logger.info("Successfully registered with discovery service")
            else:
                logger.warning("Failed to register with discovery service")
                
    except Exception as e:
        logger.warning("Some initialization steps failed, but service will continue", error=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "registration-service"}

@app.post("/register", response_model=RegistrationResponse)
async def register(
    registration_form: RegistrationForm,
    db: Session = Depends(get_db)
):
    """Register a new user."""
    try:
        user_manager = UserManager(db)
        user_manager.register(registration_form)
        return RegistrationResponse(status="CREATED")
        
    except ValueError as e:
        logger.warning("Registration failed", error=str(e))
        return RegistrationResponse(
            status="BAD_REQUEST",
            errors=[str(e)]
        )
    except Exception as e:
        logger.error("Unchecked exception during registration", error=str(e))
        return RegistrationResponse(status="INTERNAL_SERVER_ERROR")

@app.get("/{lang}/persons/{user_id}", response_model=dict) # Changed response_model to dict as PersonResponse is not defined
async def get_person_by_id(
    user_id: int,
    lang: str,
    db: Session = Depends(get_db)
):
    """Get person by ID."""
    try:
        user_manager = UserManager(db)
        person = user_manager.get_user_by_id(user_id, lang)
        return {
            "id": person.id,
            "firstname": person.firstname,
            "lastname": person.lastname,
            "date_of_birth": person.date_of_birth,
            "email": person.email,
            "role_id": person.role_id
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Failed to get person by ID", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/{lang}/persons/{user_id}/valid")
async def validate_user_id(
    user_id: int,
    lang: str,
    db: Session = Depends(get_db)
):
    """Validate if user ID exists."""
    try:
        user_manager = UserManager(db)
        return user_manager.validate_user_id(user_id)
    except Exception as e:
        logger.error("Failed to validate user ID", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/{lang}/persons")
async def get_user_ids_by_name(
    lang: str,
    name: str,
    db: Session = Depends(get_db)
):
    """Get user IDs by first name."""
    try:
        user_manager = UserManager(db)
        return user_manager.get_user_ids_by_name(name)
    except Exception as e:
        logger.error("Failed to get user IDs by name", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/persons/{username}/details", response_model=dict)
async def get_user_and_credentials_by_username(
    username: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get user and credentials by username (service-to-service call)."""
    try:
        # Validate token
        token = credentials.credentials
        token_data = verify_token(token)
        
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Check if user has SERVICE role
        if "SERVICE" not in token_data.get("roles", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        user_manager = UserManager(db)
        return user_manager.get_user_and_credentials_by_username(username)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get user details", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888) 