
-- Enhanced Recruitment System Database Schema for SQLite

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Drop tables if they exist (reverse order due to dependencies)
DROP TABLE IF EXISTS application_audit;
DROP TABLE IF EXISTS system_config;
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS competence_profile;
DROP TABLE IF EXISTS availability;
DROP TABLE IF EXISTS application;
DROP TABLE IF EXISTS job_skill_requirement;
DROP TABLE IF EXISTS job_posting;
DROP TABLE IF EXISTS job_category;
DROP TABLE IF EXISTS application_status;
DROP TABLE IF EXISTS credential;
DROP TABLE IF EXISTS person;
DROP TABLE IF EXISTS competence;
DROP TABLE IF EXISTS role;

-- Create roles table
CREATE TABLE role (
    role_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    permissions TEXT, -- JSON string of permissions
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default roles
INSERT INTO role (role_id, name, description, permissions) VALUES
(1, 'recruiter', 'Recruiter role with job posting and application management permissions', '["create_job", "view_applications", "update_application_status", "view_candidates"]'),
(2, 'applicant', 'Job applicant role with application submission permissions', '["apply_job", "view_own_applications", "update_profile"]'),
(3, 'admin', 'Administrator role with full system access', '["*"]'),
(4, 'hiring_manager', 'Hiring manager role with interview and decision permissions', '["view_applications", "schedule_interviews", "make_hiring_decisions"]');

-- Create competence table
CREATE TABLE competence (
    competence_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample competencies
INSERT INTO competence (competence_id, name, description, category) VALUES
(1, 'Python', 'Python programming language', 'Programming'),
(2, 'JavaScript', 'JavaScript programming language', 'Programming'),
(3, 'React', 'React.js frontend framework', 'Frontend'),
(4, 'Node.js', 'Node.js backend runtime', 'Backend'),
(5, 'SQL', 'Structured Query Language for databases', 'Database'),
(6, 'Project Management', 'Managing projects and teams', 'Management'),
(7, 'Communication', 'Verbal and written communication skills', 'Soft Skills');

-- Create person table
CREATE TABLE person (
    person_id INTEGER PRIMARY KEY AUTOINCREMENT,
    firstname VARCHAR(100) NOT NULL,
    lastname VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20),
    address TEXT,
    date_of_birth DATE,
    role_id INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    profile_picture_url VARCHAR(500),
    linkedin_url VARCHAR(500),
    portfolio_url VARCHAR(500),
    resume_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES role(role_id)
);

-- Create credential table
CREATE TABLE credential (
    credential_id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    last_login TIMESTAMP,
    password_reset_token VARCHAR(255),
    password_reset_expires TIMESTAMP,
    is_verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (person_id) REFERENCES person(person_id) ON DELETE CASCADE
);

-- Create application status table
CREATE TABLE application_status (
    status_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    order_sequence INTEGER,
    is_final BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert application statuses
INSERT INTO application_status (status_id, name, description, order_sequence, is_final) VALUES
(1, 'submitted', 'Application has been submitted', 1, FALSE),
(2, 'under_review', 'Application is being reviewed by HR', 2, FALSE),
(3, 'interview_scheduled', 'Interview has been scheduled', 3, FALSE),
(4, 'interviewed', 'Interview has been completed', 4, FALSE),
(5, 'accepted', 'Application has been accepted', 5, TRUE),
(6, 'rejected', 'Application has been rejected', 6, TRUE),
(7, 'withdrawn', 'Application has been withdrawn by applicant', 7, TRUE);

-- Create job category table
CREATE TABLE job_category (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    parent_category_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_category_id) REFERENCES job_category(category_id)
);

-- Insert job categories
INSERT INTO job_category (category_id, name, description) VALUES
(1, 'Technology', 'Technology and software development roles'),
(2, 'Marketing', 'Marketing and advertising roles'),
(3, 'Sales', 'Sales and business development roles'),
(4, 'Human Resources', 'HR and people management roles'),
(5, 'Finance', 'Finance and accounting roles');

-- Create job posting table
CREATE TABLE job_posting (
    job_posting_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    requirements TEXT,
    responsibilities TEXT,
    salary_min DECIMAL(12,2),
    salary_max DECIMAL(12,2),
    currency VARCHAR(3) DEFAULT 'USD',
    location VARCHAR(200),
    remote_allowed BOOLEAN DEFAULT FALSE,
    employment_type VARCHAR(20) DEFAULT 'full-time', -- full-time, part-time, contract, internship
    experience_level VARCHAR(20) DEFAULT 'mid', -- entry, mid, senior, executive
    category_id INTEGER,
    posted_by INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'active', -- active, paused, closed, draft
    application_deadline DATE,
    start_date DATE,
    benefits TEXT,
    company_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES job_category(category_id),
    FOREIGN KEY (posted_by) REFERENCES person(person_id)
);

-- Create job skill requirements table
CREATE TABLE job_skill_requirement (
    requirement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_posting_id INTEGER NOT NULL,
    competence_id INTEGER NOT NULL,
    required_level VARCHAR(20) DEFAULT 'intermediate', -- beginner, intermediate, advanced, expert
    min_years_experience DECIMAL(3,1) DEFAULT 0,
    is_required BOOLEAN DEFAULT TRUE,
    weight DECIMAL(3,2) DEFAULT 1.0, -- For scoring applications
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_posting_id) REFERENCES job_posting(job_posting_id) ON DELETE CASCADE,
    FOREIGN KEY (competence_id) REFERENCES competence(competence_id),
    UNIQUE(job_posting_id, competence_id)
);

-- Create availability table
CREATE TABLE availability (
    availability_id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL,
    from_date DATE NOT NULL,
    to_date DATE,
    is_flexible BOOLEAN DEFAULT TRUE,
    notice_period_days INTEGER DEFAULT 30,
    preferred_start_time TIME,
    preferred_end_time TIME,
    work_schedule_preference VARCHAR(50), -- full-time, part-time, flexible, remote
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (person_id) REFERENCES person(person_id) ON DELETE CASCADE
);

-- Create application table
CREATE TABLE application (
    application_id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL,
    job_posting_id INTEGER NOT NULL,
    cover_letter TEXT,
    status_id INTEGER DEFAULT 1,
    applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER,
    interview_date TIMESTAMP,
    interview_notes TEXT,
    feedback TEXT,
    match_score DECIMAL(5,2), -- Calculated compatibility score (0-100)
    salary_expectation DECIMAL(12,2),
    additional_documents TEXT, -- JSON array of document URLs
    recruiter_notes TEXT,
    rejection_reason TEXT,
    FOREIGN KEY (person_id) REFERENCES person(person_id),
    FOREIGN KEY (job_posting_id) REFERENCES job_posting(job_posting_id),
    FOREIGN KEY (status_id) REFERENCES application_status(status_id),
    FOREIGN KEY (updated_by) REFERENCES person(person_id),
    UNIQUE(person_id, job_posting_id)
);

-- Create competence profile table
CREATE TABLE competence_profile (
    profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL,
    competence_id INTEGER NOT NULL,
    years_of_experience DECIMAL(3,1) NOT NULL,
    proficiency_level VARCHAR(20) NOT NULL, -- beginner, intermediate, advanced, expert
    certification VARCHAR(200),
    last_used_date DATE,
    is_verified BOOLEAN DEFAULT FALSE,
    verified_by INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (person_id) REFERENCES person(person_id) ON DELETE CASCADE,
    FOREIGN KEY (competence_id) REFERENCES competence(competence_id),
    FOREIGN KEY (verified_by) REFERENCES person(person_id),
    UNIQUE(person_id, competence_id)
);

-- Create notifications table
CREATE TABLE notifications (
    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipient_id INTEGER NOT NULL,
    sender_id INTEGER,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) DEFAULT 'info', -- info, warning, success, error
    related_entity_type VARCHAR(50), -- application, job_posting, interview
    related_entity_id INTEGER,
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recipient_id) REFERENCES person(person_id),
    FOREIGN KEY (sender_id) REFERENCES person(person_id)
);

-- Create system configuration table
CREATE TABLE system_config (
    config_id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value TEXT,
    description TEXT,
    data_type VARCHAR(20) DEFAULT 'string', -- string, number, boolean, json
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default system configurations
INSERT INTO system_config (config_key, config_value, description, data_type, is_public) VALUES
('application_deadline_buffer_days', '7', 'Number of days before deadline to send reminder', 'number', FALSE),
('max_applications_per_user', '10', 'Maximum active applications per user', 'number', FALSE),
('auto_reject_after_days', '90', 'Auto-reject applications after this many days', 'number', FALSE),
('company_name', 'Recruitment Corp', 'Company name for branding', 'string', TRUE),
('support_email', 'support@recruitment.com', 'Support contact email', 'string', TRUE);

-- Create application audit table for tracking changes
CREATE TABLE application_audit (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER NOT NULL,
    field_name VARCHAR(100) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    changed_by INTEGER NOT NULL,
    change_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES application(application_id),
    FOREIGN KEY (changed_by) REFERENCES person(person_id)
);

-- Create indexes for better performance
CREATE INDEX idx_person_email ON person(email);
CREATE INDEX idx_person_role ON person(role_id);
CREATE INDEX idx_credential_username ON credential(username);
CREATE INDEX idx_application_person ON application(person_id);
CREATE INDEX idx_application_job ON application(job_posting_id);
CREATE INDEX idx_application_status ON application(status_id);
CREATE INDEX idx_job_posting_status ON job_posting(status);
CREATE INDEX idx_job_posting_category ON job_posting(category_id);
CREATE INDEX idx_job_posting_posted_by ON job_posting(posted_by);
CREATE INDEX idx_notifications_recipient ON notifications(recipient_id, is_read);
CREATE INDEX idx_competence_profile_person ON competence_profile(person_id);

-- Create views for common queries
CREATE VIEW active_job_postings AS
SELECT 
    jp.*,
    jc.name as category_name,
    p.firstname || ' ' || p.lastname as posted_by_name
FROM job_posting jp
LEFT JOIN job_category jc ON jp.category_id = jc.category_id
LEFT JOIN person p ON jp.posted_by = p.person_id
WHERE jp.status = 'active' 
AND (jp.application_deadline IS NULL OR jp.application_deadline >= DATE('now'));

CREATE VIEW application_summary AS
SELECT 
    a.*,
    p.firstname || ' ' || p.lastname as applicant_name,
    p.email as applicant_email,
    jp.title as job_title,
    ast.name as status_name,
    ast.description as status_description
FROM application a
JOIN person p ON a.person_id = p.person_id
JOIN job_posting jp ON a.job_posting_id = jp.job_posting_id
JOIN application_status ast ON a.status_id = ast.status_id;

-- Add triggers for timestamp updates
CREATE TRIGGER update_person_timestamp 
    AFTER UPDATE ON person
    BEGIN
        UPDATE person SET updated_at = CURRENT_TIMESTAMP WHERE person_id = NEW.person_id;
    END;

CREATE TRIGGER update_credential_timestamp 
    AFTER UPDATE ON credential
    BEGIN
        UPDATE credential SET updated_at = CURRENT_TIMESTAMP WHERE credential_id = NEW.credential_id;
    END;

CREATE TRIGGER update_job_posting_timestamp 
    AFTER UPDATE ON job_posting
    BEGIN
        UPDATE job_posting SET updated_at = CURRENT_TIMESTAMP WHERE job_posting_id = NEW.job_posting_id;
    END;

CREATE TRIGGER update_application_timestamp 
    AFTER UPDATE ON application
    BEGIN
        UPDATE application SET last_updated = CURRENT_TIMESTAMP WHERE application_id = NEW.application_id;
    END;
