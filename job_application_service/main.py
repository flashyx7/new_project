"""
Job Application Service - Handle job applications and matching
"""

import os
import sys
import sqlite3
import structlog
from datetime import datetime, date
from fastapi import FastAPI, HTTPException, Depends, status, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from shared.database import get_db_connection, create_tables
from shared.security import verify_token

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
    title="Job Application Service",
    description="Job application and matching service",
    version="1.0.0"
)

security = HTTPBearer()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class CompetenceForm(BaseModel):
    competence_id: int
    years_of_experience: float

class AvailabilityForm(BaseModel):
    from_date: date
    to_date: date

class ApplicationForm(BaseModel):
    person_id: int
    competences: List[CompetenceForm]
    availability: AvailabilityForm

class ApplicationResponse(BaseModel):
    id: int
    person_id: int
    job_posting_id: Optional[int]
    status_id: int
    applied_date: datetime

@app.on_event("startup")
async def startup_event():
    """Initialize the job application service."""
    logger.info("Job application service starting up")
    try:
        create_tables()
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "job-application-service"}

@app.post("/applications", response_model=ApplicationResponse)
async def create_application(
    job_posting_id: int = Form(...),
    cover_letter: str = Form(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a job application."""
    try:
        # Verify token
        token_data = verify_token(credentials.credentials)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        person_id = token_data.get("person_id")
        if not person_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user data"
            )

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if already applied
        cursor.execute(
            "SELECT id FROM application WHERE person_id = ? AND job_posting_id = ?",
            (person_id, job_posting_id)
        )

        if cursor.fetchone():
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Already applied to this job"
            )

        # Create application
        cursor.execute("""
            INSERT INTO application (person_id, job_posting_id, cover_letter, status_id)
            VALUES (?, ?, ?, ?)
        """, (person_id, job_posting_id, cover_letter, 1))

        application_id = cursor.lastrowid
        conn.commit()

        # Get the created application
        cursor.execute("""
            SELECT id, person_id, job_posting_id, status_id, applied_date
            FROM application WHERE id = ?
        """, (application_id,))

        app_data = cursor.fetchone()
        conn.close()

        return ApplicationResponse(
            id=app_data[0],
            person_id=app_data[1],
            job_posting_id=app_data[2],
            status_id=app_data[3],
            applied_date=datetime.fromisoformat(app_data[4])
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Application creation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create application"
        )

@app.get("/applications/user/{user_id}")
async def get_user_applications(
    user_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get applications for a specific user."""
    try:
        # Verify token
        token_data = verify_token(credentials.credentials)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT a.id, a.job_posting_id, jp.title, a.status_id, ast.name, a.applied_date
            FROM application a
            JOIN job_posting jp ON a.job_posting_id = jp.id
            JOIN application_status ast ON a.status_id = ast.id
            WHERE a.person_id = ?
            ORDER BY a.applied_date DESC
        """, (user_id,))

        applications = cursor.fetchall()
        conn.close()

        return {"applications": [
            {
                "id": app[0],
                "job_posting_id": app[1],
                "job_title": app[2],
                "status_id": app[3],
                "status_name": app[4],
                "applied_date": app[5]
            }
            for app in applications
        ]}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get user applications", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve applications"
        )

@app.get("/competences")
async def get_competences():
    """Get all available competences."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, description FROM competence")
        competences = cursor.fetchall()
        conn.close()

        return {"competences": [
            {"id": comp[0], "name": comp[1], "description": comp[2]}
            for comp in competences
        ]}

    except Exception as e:
        logger.error("Failed to get competences", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve competences"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082)