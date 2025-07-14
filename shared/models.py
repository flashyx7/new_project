
"""
Shared data models for the recruitment system.
"""

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, EmailStr

# Database Models (simplified for SQLite)
class Role:
    def __init__(self, id: int, name: str, description: str = None):
        self.id = id
        self.name = name
        self.description = description

class Person:
    def __init__(self, id: int, firstname: str, lastname: str, email: str, 
                 role_id: int, date_of_birth: date = None, phone: str = None, 
                 address: str = None):
        self.id = id
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.role_id = role_id
        self.date_of_birth = date_of_birth
        self.phone = phone
        self.address = address

class Credential:
    def __init__(self, id: int, person_id: int, username: str, password: str):
        self.id = id
        self.person_id = person_id
        self.username = username
        self.password = password

class JobPosting:
    def __init__(self, id: int, title: str, description: str, posted_by: int,
                 requirements: str = None, salary_min: float = None, 
                 salary_max: float = None, location: str = None,
                 employment_type: str = 'full-time', status: str = 'active'):
        self.id = id
        self.title = title
        self.description = description
        self.posted_by = posted_by
        self.requirements = requirements
        self.salary_min = salary_min
        self.salary_max = salary_max
        self.location = location
        self.employment_type = employment_type
        self.status = status

class Application:
    def __init__(self, id: int, person_id: int, job_posting_id: int, 
                 status_id: int = 1, cover_letter: str = None):
        self.id = id
        self.person_id = person_id
        self.job_posting_id = job_posting_id
        self.status_id = status_id
        self.cover_letter = cover_letter

class Competence:
    def __init__(self, id: int, name: str, description: str = None):
        self.id = id
        self.name = name
        self.description = description

class CompetenceProfile:
    def __init__(self, id: int, person_id: int, competence_id: int, 
                 years_of_experience: float, proficiency_level: str = 'intermediate'):
        self.id = id
        self.person_id = person_id
        self.competence_id = competence_id
        self.years_of_experience = years_of_experience
        self.proficiency_level = proficiency_level

class Status:
    def __init__(self, id: int, name: str, description: str = None):
        self.id = id
        self.name = name
        self.description = description

class Availability:
    def __init__(self, id: int, person_id: int, from_date: date, to_date: date):
        self.id = id
        self.person_id = person_id
        self.from_date = from_date
        self.to_date = to_date
