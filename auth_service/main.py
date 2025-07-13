from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import structlog
import consul
import httpx
import os
import json

# Import shared modules
import sys
import os
# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
from shared.models import Person, Credential, Role
from shared.schemas import AuthRequest, AuthTokenResponse, AuthFailResponse
from shared.security import verify_password, create_access_token, verify_token, decode_token
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
    title="Auth Service",
    description="Authentication and authorization service",
    version="1.0.0"
)

# Security
security = HTTPBearer()

# Consul client
consul_host = os.getenv("CONSUL_HOST", "localhost")
consul_port = int(os.getenv("CONSUL_PORT", "8500"))
consul_client = consul.Consul(host=consul_host, port=consul_port)

# Config service URL
config_service_url = os.getenv("CONFIG_SERVICE_URL", "http://localhost:9999")

# Discovery service URL
discovery_service_url = os.getenv("DISCOVERY_SERVICE_URL", "http://localhost:9090")

class LoginService:
    """Service for handling authentication logic."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def authenticate_and_get_token(self, username: str, password: str) -> str:
        """Authenticate user and return JWT token."""
        # Find user credentials
        credential = self.db.query(Credential).filter(Credential.username == username).first()
        if not credential:
            raise ValueError("User not found")
        
        # Verify password
        if not verify_password(password, credential.password):
            raise ValueError("Invalid password")
        
        # Get user details
        person = credential.person
        role = person.role
        
        # Create user details for JWT
        user_details = {
            "username": username,
            "user_id": person.id,
            "roles": [role.name]
        }
        
        # Generate token
        token = create_access_token(user_details)
        return token
    
    def get_user_details_by_username(self, username: str) -> Optional[dict]:
        """Get user details by username."""
        credential = self.db.query(Credential).filter(Credential.username == username).first()
        if not credential:
            return None
        
        person = credential.person
        role = person.role
        
        return {
            "username": username,
            "user_id": person.id,
            "roles": [role.name]
        }

@app.on_event("startup")
async def startup_event():
    """Initialize the auth service."""
    logger.info("Auth service starting up")
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
            "service_name": "auth-service",
            "service_id": "auth-service-1",
            "address": "127.0.0.1",
            "port": 8081,
            "tags": ["auth", "authentication"]
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
    return {"status": "healthy", "service": "auth-service"}

@app.post("/auth/login", response_model=AuthTokenResponse)
async def generate_jwt_token(
    auth_request: AuthRequest,
    db: Session = Depends(get_db)
):
    """Generate JWT token for user login."""
    logger.info("/login received request")
    
    try:
        login_service = LoginService(db)
        jwt_token = login_service.authenticate_and_get_token(
            auth_request.username, 
            auth_request.password
        )
        
        logger.info("Authentication passed and token created!")
        return AuthTokenResponse(token=jwt_token)
        
    except ValueError as e:
        logger.warning("Authentication failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": str(e)}
        )
    except Exception as e:
        logger.warning({"error": str(e), "event": "Authentication failed"})
        return {"error": str(e), "message": "Authentication failed"}

@app.post("/login", response_model=AuthTokenResponse)
async def generate_jwt_token_alias(
    auth_request: AuthRequest,
    db: Session = Depends(get_db)
):
    """Alias for /auth/login for compatibility with edge service routing."""
    logger.info("/login (alias) received request")
    try:
        login_service = LoginService(db)
        jwt_token = login_service.authenticate_and_get_token(
            auth_request.username, 
            auth_request.password
        )
        logger.info("Authentication passed and token created! (alias)")
        return AuthTokenResponse(token=jwt_token)
    except ValueError as e:
        logger.warning("Authentication failed (alias)", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": str(e)}
        )
    except Exception as e:
        logger.warning({"error": str(e), "event": "Authentication failed (alias)"})
        return {"error": str(e), "message": "Authentication failed (alias)"}

@app.get("/auth/validate")
async def validate_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Validate JWT token."""
    try:
        token = credentials.credentials
        token_data = verify_token(token)
        
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        return {
            "valid": True,
            "username": token_data['username'],
            "user_id": token_data['user_id'],
            "roles": token_data['roles']
        }
        
    except Exception as e:
        logger.error("Token validation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@app.get("/auth/user/{username}/details")
async def get_user_details(
    username: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get user details by username (service-to-service call)."""
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
        if "SERVICE" not in token_data['roles']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        login_service = LoginService(db)
        user_details = login_service.get_user_details_by_username(username)
        
        if user_details is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user_details
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get user details", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081) 