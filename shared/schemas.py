
"""
Shared Pydantic schemas for the recruitment system.
"""

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, EmailStr

# Authentication schemas
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str

# Registration schemas
class RegistrationForm(BaseModel):
    username: str
    password: str
    email: EmailStr
    firstname: str
    lastname: str
    date_of_birth: Optional[date] = None
    role_id: Optional[int] = 2  # Default to Applicant

class RegistrationResponse(BaseModel):
    status: str
    message: str

# Person schemas
class PersonResponse(BaseModel):
    id: int
    firstname: str
    lastname: str
    email: str
    role_id: int
    date_of_birth: Optional[date] = None
    phone: Optional[str] = None
    address: Optional[str] = None

    class Config:
        from_attributes = True

# Job application schemas
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

class ApplicationParamForm(BaseModel):
    person_id: Optional[int] = None
    status_id: Optional[int] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None

class ApplicationStatusForm(BaseModel):
    status_id: int

# Response schemas
class CompetenceResponse(BaseModel):
    id: int
    name: str

class StatusResponse(BaseModel):
    id: int
    name: str

class AvailabilityResponse(BaseModel):
    id: int
    from_date: date
    to_date: date

class ApplicationResponse(BaseModel):
    id: int
    person_id: int
    date_of_registration: datetime
    status_id: int
    availability_id: int
    availability: AvailabilityResponse
    competences: List[dict]
    person: dict

class RequestResponse(BaseModel):
    message: str

class RequestListResponse(BaseModel):
    data: List[ApplicationResponse]

# Auth schemas
class AuthRequest(BaseModel):
    username: str
    password: str

class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_info: dict
