from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date, datetime

# Auth Service Schemas
class AuthRequest(BaseModel):
    username: str
    password: str

class AuthTokenResponse(BaseModel):
    token: str

class AuthFailResponse(BaseModel):
    message: str

# Registration Service Schemas
class RegistrationForm(BaseModel):
    firstname: str = Field(..., min_length=1, max_length=45)
    lastname: str = Field(..., min_length=1, max_length=45)
    date_of_birth: date
    email: EmailStr
    username: str = Field(..., min_length=1, max_length=45)
    password: str = Field(..., min_length=6)
    role_id: Optional[int] = 2  # Default to Applicant role

class UserCredentialsDTO(BaseModel):
    username: str
    password: str
    person_id: int

class RegistrationResponse(BaseModel):
    status: str
    message: Optional[str] = None
    errors: Optional[List[str]] = None

class PersonResponse(BaseModel):
    id: int
    firstname: str
    lastname: str
    date_of_birth: date
    email: str
    role_id: int

    class Config:
        from_attributes = True

# Job Application Service Schemas
class AvailabilityForm(BaseModel):
    from_date: date
    to_date: date

class CompetenceForm(BaseModel):
    competence_id: int
    years_of_experience: float

class ApplicationForm(BaseModel):
    person_id: int
    availability: AvailabilityForm
    competences: List[CompetenceForm]

class ApplicationParamForm(BaseModel):
    person_id: Optional[int] = None
    status_id: Optional[int] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None

class ApplicationStatusForm(BaseModel):
    status_id: int

class CompetenceResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class AvailabilityResponse(BaseModel):
    id: int
    from_date: date
    to_date: date

    class Config:
        from_attributes = True

class CompetenceProfileResponse(BaseModel):
    id: int
    competence_id: int
    years_of_experience: float
    competence: CompetenceResponse

    class Config:
        from_attributes = True

class ApplicationResponse(BaseModel):
    id: int
    person_id: int
    date_of_registration: datetime
    status_id: int
    availability_id: int
    availability: AvailabilityResponse
    competences: List[CompetenceProfileResponse]
    person: PersonResponse

    class Config:
        from_attributes = True

class StatusResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class RequestResponse(BaseModel):
    message: str

class RequestListResponse(BaseModel):
    data: List[ApplicationResponse] 