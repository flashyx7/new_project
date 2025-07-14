-- Enhanced Database Schema for Recruitment System
-- SQLite implementation with comprehensive tables

PRAGMA foreign_keys = ON;

-- Drop existing tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS competence_profile;
DROP TABLE IF EXISTS application;
DROP TABLE IF EXISTS availability;
DROP TABLE IF EXISTS job_posting;
DROP TABLE IF EXISTS credential;
DROP TABLE IF EXISTS person;
DROP TABLE IF EXISTS job_category;
DROP TABLE IF EXISTS application_status;
DROP TABLE IF EXISTS competence;
DROP TABLE IF EXISTS role;

-- Core lookup tables
CREATE TABLE role (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE competence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE application_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE job_category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Main entity tables
CREATE TABLE person (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    firstname VARCHAR(100) NOT NULL,
    lastname VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20),
    address TEXT,
    role_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES role(id)
);

CREATE TABLE credential (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (person_id) REFERENCES person(id) ON DELETE CASCADE
);

CREATE TABLE job_posting (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    requirements TEXT,
    responsibilities TEXT,
    salary_min DECIMAL(10,2),
    salary_max DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'USD',
    location VARCHAR(200),
    remote_allowed BOOLEAN DEFAULT 0,
    employment_type VARCHAR(20) DEFAULT 'full-time',
    experience_level VARCHAR(20) DEFAULT 'mid',
    category_id INTEGER,
    posted_by INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    application_deadline DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES job_category(id),
    FOREIGN KEY (posted_by) REFERENCES person(id)
);

CREATE TABLE availability (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL,
    from_date DATE NOT NULL,
    to_date DATE NOT NULL,
    is_flexible BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (person_id) REFERENCES person(id) ON DELETE CASCADE
);

CREATE TABLE application (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL,
    job_posting_id INTEGER NOT NULL,
    cover_letter TEXT,
    status_id INTEGER DEFAULT 1,
    applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    match_score DECIMAL(5,2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (person_id) REFERENCES person(id) ON DELETE CASCADE,
    FOREIGN KEY (job_posting_id) REFERENCES job_posting(id) ON DELETE CASCADE,
    FOREIGN KEY (status_id) REFERENCES application_status(id),
    UNIQUE(person_id, job_posting_id)
);

CREATE TABLE competence_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL,
    competence_id INTEGER NOT NULL,
    years_of_experience DECIMAL(3,1) NOT NULL,
    proficiency_level VARCHAR(20) DEFAULT 'intermediate',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (person_id) REFERENCES person(id) ON DELETE CASCADE,
    FOREIGN KEY (competence_id) REFERENCES competence(id),
    UNIQUE(person_id, competence_id)
);

-- Insert default data
INSERT INTO role (name, description) VALUES
('Recruiter', 'HR personnel who manage job postings and applications'),
('Applicant', 'Job seekers who apply for positions'),
('Admin', 'System administrators with full access'),
('Hiring Manager', 'Managers who make hiring decisions');

INSERT INTO competence (name, description) VALUES
('Python', 'Python programming language'),
('JavaScript', 'JavaScript programming language'),
('React', 'React frontend framework'),
('FastAPI', 'FastAPI web framework'),
('SQL', 'Database query language'),
('Git', 'Version control system'),
('Docker', 'Containerization technology'),
('AWS', 'Amazon Web Services cloud platform'),
('Machine Learning', 'ML and AI technologies'),
('Project Management', 'Project management skills');

INSERT INTO application_status (name, description) VALUES
('Submitted', 'Application has been submitted'),
('Under Review', 'Application is being reviewed'),
('Interview Scheduled', 'Interview has been scheduled'),
('Accepted', 'Application has been accepted'),
('Rejected', 'Application has been rejected'),
('Withdrawn', 'Application was withdrawn by applicant');

INSERT INTO job_category (name, description) VALUES
('Software Development', 'Programming and software engineering roles'),
('Data Science', 'Data analysis and machine learning roles'),
('DevOps', 'Development operations and infrastructure'),
('UI/UX Design', 'User interface and experience design'),
('Product Management', 'Product strategy and management'),
('Quality Assurance', 'Software testing and quality control'),
('Sales', 'Sales and business development'),
('Marketing', 'Marketing and communications'),
('Human Resources', 'HR and talent management'),
('Finance', 'Financial and accounting roles');

-- Create indexes for better performance
CREATE INDEX idx_person_email ON person(email);
CREATE INDEX idx_credential_username ON credential(username);
CREATE INDEX idx_application_person ON application(person_id);
CREATE INDEX idx_application_job ON application(job_posting_id);
CREATE INDEX idx_competence_profile_person ON competence_profile(person_id);