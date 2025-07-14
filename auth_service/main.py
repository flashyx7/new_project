"""
Auth Service - Authentication and Authorization microservice
"""

import os
import sys
import sqlite3
import structlog
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends, status, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from shared.security import create_access_token, verify_token, verify_password, get_password_hash
except ImportError:
    # Fallback security functions
    import bcrypt
    import jwt

    def get_password_hash(password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except:
            return False

    def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=24)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, "secret-key", algorithm="HS256")

    def verify_token(token: str) -> dict:
        try:
            return jwt.decode(token, "secret-key", algorithms=["HS256"])
        except:
            return None

app = FastAPI(
    title="Auth Service",
    description="Authentication and Authorization Service",
    version="1.0.0"
)

security = HTTPBearer()

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

# Database helper
def get_db_connection():
    """Get database connection."""
    return sqlite3.connect("recruitment_system.db")

# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str

class UserInfo(BaseModel):
    id: int
    person_id: int
    username: str
    firstname: str
    lastname: str
    email: str
    role_id: int

@app.post("/login", response_model=TokenResponse)
async def login(username: str = Form(...), password: str = Form(...)):
    """Authenticate user and return token."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT c.id, c.person_id, c.username, c.password, p.firstname, p.lastname, p.email, p.role_id
            FROM credential c
            JOIN person p ON c.person_id = p.id
            WHERE c.username = ?
        """, (username,))

        user = cursor.fetchone()
        conn.close()

        if not user or not verify_password(password, user[3]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        # Create access token
        token_data = {
            "user_id": user[0],
            "person_id": user[1],
            "username": user[2]
        }
        access_token = create_access_token(token_data)

        return TokenResponse(
            access_token=access_token,
            user_id=user[0],
            username=user[2]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )

@app.get("/verify")
async def verify_auth_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify authentication token."""
    token = credentials.credentials
    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    return {"valid": True, "payload": payload}

@app.get("/user/{user_id}", response_model=UserInfo)
async def get_user_info(user_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get user information."""
    token = credentials.credentials
    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT c.id, c.person_id, c.username, p.firstname, p.lastname, p.email, p.role_id
            FROM credential c
            JOIN person p ON c.person_id = p.id
            WHERE c.id = ?
        """, (user_id,))

        user = cursor.fetchone()
        conn.close()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return UserInfo(
            id=user[0],
            person_id=user[1],
            username=user[2],
            firstname=user[3],
            lastname=user[4],
            email=user[5],
            role_id=user[6]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Get user error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        conn.close()

        if result and result[0] == 1:
            return {"status": "healthy", "service": "auth", "timestamp": datetime.now().isoformat()}
        else:
            return {"status": "unhealthy", "error": "Database check failed"}

    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8081"))

    print(f"🔐 Starting Auth Service on {host}:{port}")

    try:
        uvicorn.run(app, host=host, port=port, log_level="info")
    except Exception as e:
        print(f"❌ Failed to start auth service: {e}")
        sys.exit(1)