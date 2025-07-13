from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Role(Base):
    __tablename__ = 'role'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(45), nullable=False)
    
    # Relationships
    persons = relationship("Person", back_populates="role")

class Person(Base):
    __tablename__ = 'person'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    firstname = Column(String(45))
    lastname = Column(String(45))
    date_of_birth = Column(Date)
    email = Column(String(45))
    role_id = Column(Integer, ForeignKey('role.id'), default=2)
    
    # Relationships
    role = relationship("Role", back_populates="persons")
    credentials = relationship("Credential", back_populates="person", uselist=False)
    applications = relationship("Application", back_populates="person")

class Credential(Base):
    __tablename__ = 'credential'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(Integer, ForeignKey('person.id'), nullable=False)
    username = Column(String(45), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    
    # Relationships
    person = relationship("Person", back_populates="credentials")

class Availability(Base):
    __tablename__ = 'availability'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)
    
    # Relationships
    applications = relationship("Application", back_populates="availability")

class Competence(Base):
    __tablename__ = 'competence'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(45), nullable=False)
    
    # Relationships
    competence_profiles = relationship("CompetenceProfile", back_populates="competence")

class Status(Base):
    __tablename__ = 'status'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(45), nullable=False)
    
    # Relationships
    applications = relationship("Application", back_populates="status")

class Application(Base):
    __tablename__ = 'application'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(Integer, ForeignKey('person.id'), nullable=False)
    date_of_registration = Column(DateTime, default=datetime.utcnow)
    status_id = Column(Integer, ForeignKey('status.id'), default=0)
    availability_id = Column(Integer, ForeignKey('availability.id'), nullable=False)
    
    # Relationships
    person = relationship("Person", back_populates="applications")
    status = relationship("Status", back_populates="applications")
    availability = relationship("Availability", back_populates="applications")
    competence_profiles = relationship("CompetenceProfile", back_populates="application")

class CompetenceProfile(Base):
    __tablename__ = 'competence_profile'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(Integer, ForeignKey('application.id'), nullable=False)
    competence_id = Column(Integer, ForeignKey('competence.id'), nullable=False)
    years_of_experience = Column(Float)
    
    # Relationships
    application = relationship("Application", back_populates="competence_profiles")
    competence = relationship("Competence", back_populates="competence_profiles") 