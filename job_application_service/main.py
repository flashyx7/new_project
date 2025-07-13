from fastapi import FastAPI, HTTPException, Depends, status, Query
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
from shared.models import (
    Person, Credential, Role, Application, Status, 
    Competence, CompetenceProfile, Availability
)
from shared.schemas import (
    ApplicationForm, ApplicationResponse, RequestListResponse,
    CompetenceResponse, StatusResponse, AuthRequest, AuthTokenResponse,
    ApplicationParamForm, ApplicationStatusForm, AvailabilityResponse, RequestResponse
)
from shared.security import verify_token
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
    title="Job Application Service",
    description="Job application management service",
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

class JobApplicationService:
    """Service for handling job application logic."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_application_by_id(self, application_id: int, language: str) -> ApplicationResponse:
        """Get application by ID."""
        try:
            application = self.db.query(Application).filter(
                Application.id == application_id
            ).first()
            
            if not application:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Application with ID {application_id} not found"
                )
            
            return self._build_application_response(application)
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Failed to get application by ID", application_id=application_id, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    def get_applications_by_param(self, param: ApplicationParamForm, language: str) -> List[ApplicationResponse]:
        """Get applications by parameters."""
        query = self.db.query(Application)
        
        if param.person_id:
            query = query.filter(Application.person_id == param.person_id)
        
        if param.status_id:
            query = query.filter(Application.status_id == param.status_id)
        
        if param.from_date:
            query = query.join(Availability).filter(Availability.from_date >= param.from_date)
        
        if param.to_date:
            query = query.join(Availability).filter(Availability.to_date <= param.to_date)
        
        applications = query.all()
        return [self._build_application_response(app) for app in applications]
    
    def get_applications_page(self, page_number: int, language: str) -> List[ApplicationResponse]:
        """Get applications by page."""
        page_size = 10
        offset = (page_number - 1) * page_size
        
        applications = self.db.query(Application).offset(offset).limit(page_size).all()
        return [self._build_application_response(app) for app in applications]
    
    def register_job_application(self, application_form: ApplicationForm, language: str) -> None:
        """Register a new job application."""
        # Validate person exists
        person = self.db.query(Person).filter(Person.id == application_form.person_id).first()
        if not person:
            raise ValueError("Person not found")
        
        # Create availability
        availability = Availability(
            from_date=application_form.availability.from_date,
            to_date=application_form.availability.to_date
        )
        self.db.add(availability)
        self.db.flush()
        
        # Create application
        application = Application(
            person_id=application_form.person_id,
            status_id=0,  # Default to PENDING
            availability_id=availability.id
        )
        self.db.add(application)
        self.db.flush()
        
        # Create competence profiles
        for competence_form in application_form.competences:
            competence_profile = CompetenceProfile(
                application_id=application.id,
                competence_id=competence_form.competence_id,
                years_of_experience=competence_form.years_of_experience
            )
            self.db.add(competence_profile)
        
        self.db.commit()
        logger.info("Job application registered successfully", application_id=application.id)
    
    def change_status_on_application_by_id(self, application_id: int, status_form: ApplicationStatusForm, language: str) -> None:
        """Change status on application."""
        application = self.db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise ValueError("Application not found")
        
        # Validate status exists
        status = self.db.query(Status).filter(Status.id == status_form.status_id).first()
        if not status:
            raise ValueError("Status not found")
        
        application.status_id = status_form.status_id
        self.db.commit()
        
        logger.info("Application status changed", application_id=application_id, new_status=status_form.status_id)
    
    def get_all_valid_status(self, language: str) -> List[StatusResponse]:
        """Get all valid statuses."""
        statuses = self.db.query(Status).all()
        return [
            StatusResponse(id=status.id, name=status.name)
            for status in statuses
        ]
    
    def get_all_valid_competences(self, language: str) -> List[CompetenceResponse]:
        """Get all valid competences."""
        competences = self.db.query(Competence).all()
        return [
            CompetenceResponse(id=competence.id, name=competence.name)
            for competence in competences
        ]
    
    def _build_application_response(self, application: Application) -> ApplicationResponse:
        """Build application response with related data."""
        # Get availability
        availability_response = AvailabilityResponse(
            id=application.availability.id,
            from_date=application.availability.from_date,
            to_date=application.availability.to_date
        )
        
        # Get person
        person_response = {
            "id": application.person.id,
            "firstname": application.person.firstname,
            "lastname": application.person.lastname,
            "date_of_birth": application.person.date_of_birth,
            "email": application.person.email,
            "role_id": application.person.role_id
        }
        
        # Get competence profiles
        competence_profiles = []
        for profile in application.competence_profiles:
            competence_response = CompetenceResponse(
                id=profile.competence.id,
                name=profile.competence.name
            )
            competence_profiles.append({
                "id": profile.id,
                "competence_id": profile.competence_id,
                "years_of_experience": profile.years_of_experience,
                "competence": competence_response
            })
        
        return ApplicationResponse(
            id=application.id,
            person_id=application.person_id,
            date_of_registration=application.date_of_registration,
            status_id=application.status_id,
            availability_id=application.availability_id,
            availability=availability_response,
            competences=competence_profiles,
            person=person_response
        )

def check_role(required_roles: List[str]):
    """Dependency to check user roles."""
    def role_checker(credentials: HTTPAuthorizationCredentials = Depends(security)):
        token = credentials.credentials
        token_data = verify_token(token)
        
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user_roles = token_data.get("roles", [])
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        return token_data
    
    return role_checker

@app.on_event("startup")
async def startup_event():
    """Initialize the job application service."""
    logger.info("Job application service starting up")
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
            "service_name": "job-application-service",
            "service_id": "job-application-service-1",
            "address": "127.0.0.1",
            "port": 8082,
            "tags": ["job-application", "recruitment"]
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
    return {"status": "healthy", "service": "job-application-service"}

@app.get("/{language}/jobapplications/{application_id}", response_model=ApplicationResponse)
async def get_application_by_id(
    application_id: int,
    language: str,
    token_data=Depends(check_role(["Recruiter"])),
    db: Session = Depends(get_db)
):
    """Get application by ID."""
    try:
        service = JobApplicationService(db)
        return service.get_application_by_id(application_id, language)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to get application by ID", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/{language}/jobapplications/params")
async def get_applications_by_param(
    param: ApplicationParamForm,
    language: str,
    token_data=Depends(check_role(["Recruiter"])),
    db: Session = Depends(get_db)
):
    """Get applications by parameters."""
    try:
        service = JobApplicationService(db)
        applications = service.get_applications_by_param(param, language)
        return RequestListResponse(data=applications)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to get applications by param", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/{language}/jobapplications/pages/{page_number}")
async def get_applications_page(
    page_number: int,
    language: str,
    token_data=Depends(check_role(["Recruiter"])),
    db: Session = Depends(get_db)
):
    """Get applications by page."""
    try:
        service = JobApplicationService(db)
        applications = service.get_applications_page(page_number, language)
        return RequestListResponse(data=applications)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to get applications page", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/{language}/jobapplications")
async def register_job_application(
    application: ApplicationForm,
    language: str,
    token_data=Depends(check_role(["Applicant"])),
    db: Session = Depends(get_db)
):
    """Register a new job application."""
    try:
        service = JobApplicationService(db)
        service.register_job_application(application, language)
        return RequestResponse(message="New application was registered")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to register job application", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/{language}/jobapplications/status/{application_id}")
async def change_status_on_application_by_id(
    application_id: int,
    new_status: ApplicationStatusForm,
    language: str,
    token_data=Depends(check_role(["Recruiter"])),
    db: Session = Depends(get_db)
):
    """Change status on application."""
    try:
        service = JobApplicationService(db)
        service.change_status_on_application_by_id(application_id, new_status, language)
        return RequestResponse(message="New status have been set on application")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to change application status", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/{language}/statuses")
async def get_all_valid_status(
    language: str,
    token_data=Depends(check_role(["Recruiter"])),
    db: Session = Depends(get_db)
):
    """Get all valid statuses."""
    try:
        service = JobApplicationService(db)
        return service.get_all_valid_status(language)
    except Exception as e:
        logger.error("Failed to get valid statuses", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/{language}/competences")
async def get_all_valid_competences(
    language: str,
    token_data=Depends(check_role(["Applicant", "Recruiter"])),
    db: Session = Depends(get_db)
):
    """Get all valid competences."""
    try:
        service = JobApplicationService(db)
        return service.get_all_valid_competences(language)
    except Exception as e:
        logger.error("Failed to get valid competences", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082) 