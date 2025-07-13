
-- Enhanced Recruitment System Database Schema for SQLite
-- Supports: user management, resume parsing, job posting, candidate matching, 
-- interview scheduling, offer generation

-- Core user roles
DROP TABLE IF EXISTS `role`;
CREATE TABLE `role` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `name` VARCHAR(45) NOT NULL,
  `description` VARCHAR(255)
);

-- Insert default roles
INSERT INTO `role` (`id`, `name`, `description`) VALUES
(1, 'Recruiter', 'HR personnel who manage job postings and candidates'),
(2, 'Applicant', 'Job seekers who apply for positions'),
(3, 'Admin', 'System administrators'),
(4, 'Hiring Manager', 'Department heads who approve hires');

-- Person entity
DROP TABLE IF EXISTS `person`;
CREATE TABLE `person` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `firstname` VARCHAR(45) DEFAULT NULL,
  `lastname` VARCHAR(45) DEFAULT NULL,
  `date_of_birth` DATE DEFAULT NULL,
  `email` VARCHAR(100) UNIQUE DEFAULT NULL,
  `phone` VARCHAR(20) DEFAULT NULL,
  `address` TEXT DEFAULT NULL,
  `linkedin_url` VARCHAR(255) DEFAULT NULL,
  `portfolio_url` VARCHAR(255) DEFAULT NULL,
  `role_id` INTEGER DEFAULT 2,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `is_active` BOOLEAN DEFAULT 1,
  FOREIGN KEY (`role_id`) REFERENCES `role` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
);

-- Credentials
DROP TABLE IF EXISTS `credential`;
CREATE TABLE `credential` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `person_id` INTEGER NOT NULL,
  `username` VARCHAR(45) NOT NULL UNIQUE,
  `password` VARCHAR(255) NOT NULL,
  `last_login` DATETIME DEFAULT NULL,
  `password_reset_token` VARCHAR(255) DEFAULT NULL,
  `password_reset_expires` DATETIME DEFAULT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`person_id`) REFERENCES `person` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Job categories
DROP TABLE IF EXISTS `job_category`;
CREATE TABLE `job_category` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `description` TEXT
);

INSERT INTO `job_category` (`name`, `description`) VALUES
('Software Development', 'Programming and software engineering roles'),
('Data Science', 'Data analysis and machine learning positions'),
('Product Management', 'Product strategy and management roles'),
('Design', 'UI/UX and graphic design positions'),
('Sales', 'Sales and business development roles'),
('Marketing', 'Marketing and digital marketing positions'),
('Human Resources', 'HR and talent acquisition roles'),
('Finance', 'Financial and accounting positions');

-- Job postings
DROP TABLE IF EXISTS `job_posting`;
CREATE TABLE `job_posting` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `title` VARCHAR(255) NOT NULL,
  `description` TEXT NOT NULL,
  `requirements` TEXT,
  `responsibilities` TEXT,
  `salary_min` DECIMAL(10,2) DEFAULT NULL,
  `salary_max` DECIMAL(10,2) DEFAULT NULL,
  `currency` VARCHAR(3) DEFAULT 'USD',
  `location` VARCHAR(255),
  `remote_allowed` BOOLEAN DEFAULT 0,
  `employment_type` VARCHAR(20) DEFAULT 'full-time',
  `experience_level` VARCHAR(20) DEFAULT 'mid',
  `category_id` INTEGER,
  `posted_by` INTEGER NOT NULL,
  `status` VARCHAR(20) DEFAULT 'draft',
  `application_deadline` DATE,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`category_id`) REFERENCES `job_category` (`id`) ON DELETE SET NULL,
  FOREIGN KEY (`posted_by`) REFERENCES `person` (`id`) ON DELETE CASCADE
);

-- Competences/Skills
DROP TABLE IF EXISTS `competence`;
CREATE TABLE `competence` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `category` VARCHAR(50) DEFAULT NULL,
  `description` TEXT
);

INSERT INTO `competence` (`name`, `category`, `description`) VALUES
('Python', 'Programming', 'Python programming language'),
('JavaScript', 'Programming', 'JavaScript programming language'),
('React', 'Frontend', 'React.js framework'),
('Node.js', 'Backend', 'Node.js runtime'),
('SQL', 'Database', 'SQL database querying'),
('Project Management', 'Management', 'Project management skills'),
('Communication', 'Soft Skills', 'Communication and interpersonal skills'),
('Leadership', 'Management', 'Team leadership abilities'),
('Data Analysis', 'Analytics', 'Data analysis and interpretation'),
('Machine Learning', 'AI/ML', 'Machine learning algorithms and models');

-- Resumes
DROP TABLE IF EXISTS `resume`;
CREATE TABLE `resume` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `person_id` INTEGER NOT NULL,
  `file_path` VARCHAR(500),
  `file_name` VARCHAR(255),
  `file_size` BIGINT,
  `content_text` TEXT,
  `parsed_data` TEXT,
  `upload_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `is_primary` BOOLEAN DEFAULT 0,
  FOREIGN KEY (`person_id`) REFERENCES `person` (`id`) ON DELETE CASCADE
);

-- Availability
DROP TABLE IF EXISTS `availability`;
CREATE TABLE `availability` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `person_id` INTEGER NOT NULL,
  `from_date` DATE NOT NULL,
  `to_date` DATE NOT NULL,
  `is_flexible` BOOLEAN DEFAULT 0,
  `notes` TEXT,
  FOREIGN KEY (`person_id`) REFERENCES `person` (`id`) ON DELETE CASCADE
);

-- Application status
DROP TABLE IF EXISTS `status`;
CREATE TABLE `status` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `name` VARCHAR(45) NOT NULL,
  `description` VARCHAR(255),
  `order_index` INTEGER DEFAULT 0
);

INSERT INTO `status` (`id`, `name`, `description`, `order_index`) VALUES
(0, 'Submitted', 'Application has been submitted', 1),
(1, 'Under Review', 'Application is being reviewed', 2),
(2, 'Phone Screen', 'Initial phone screening scheduled', 3),
(3, 'Technical Interview', 'Technical interview scheduled', 4),
(4, 'Final Interview', 'Final interview with hiring manager', 5),
(5, 'Offer Extended', 'Job offer has been extended', 6),
(6, 'Hired', 'Candidate has been hired', 7),
(7, 'Rejected', 'Application has been rejected', 8),
(8, 'Withdrawn', 'Candidate withdrew application', 9);

-- Job applications
DROP TABLE IF EXISTS `application`;
CREATE TABLE `application` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `person_id` INTEGER NOT NULL,
  `job_posting_id` INTEGER NOT NULL,
  `resume_id` INTEGER,
  `cover_letter` TEXT,
  `date_of_registration` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `status_id` INTEGER DEFAULT 0,
  `match_score` DECIMAL(5,2) DEFAULT NULL,
  `notes` TEXT,
  `last_updated` DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(`person_id`, `job_posting_id`),
  FOREIGN KEY (`person_id`) REFERENCES `person` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`job_posting_id`) REFERENCES `job_posting` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`resume_id`) REFERENCES `resume` (`id`) ON DELETE SET NULL,
  FOREIGN KEY (`status_id`) REFERENCES `status` (`id`) ON DELETE SET NULL
);

-- Competence profiles for applications
DROP TABLE IF EXISTS `competence_profile`;
CREATE TABLE `competence_profile` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `application_id` INTEGER DEFAULT NULL,
  `person_id` INTEGER DEFAULT NULL,
  `competence_id` INTEGER NOT NULL,
  `years_of_experience` DECIMAL(4,2) DEFAULT NULL,
  `proficiency_level` VARCHAR(20) DEFAULT 'intermediate',
  `verified` BOOLEAN DEFAULT 0,
  FOREIGN KEY (`application_id`) REFERENCES `application` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`person_id`) REFERENCES `person` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`competence_id`) REFERENCES `competence` (`id`) ON DELETE CASCADE
);

-- Interview types
DROP TABLE IF EXISTS `interview_type`;
CREATE TABLE `interview_type` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `description` TEXT,
  `duration_minutes` INTEGER DEFAULT 60
);

INSERT INTO `interview_type` (`name`, `description`, `duration_minutes`) VALUES
('Phone Screen', 'Initial phone conversation', 30),
('Technical Interview', 'Technical skills assessment', 90),
('Behavioral Interview', 'Cultural fit and soft skills', 60),
('Final Interview', 'Interview with hiring manager', 60),
('Panel Interview', 'Interview with multiple team members', 90);

-- Interview scheduling
DROP TABLE IF EXISTS `interview`;
CREATE TABLE `interview` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `application_id` INTEGER NOT NULL,
  `interview_type_id` INTEGER NOT NULL,
  `interviewer_id` INTEGER NOT NULL,
  `scheduled_date` DATETIME NOT NULL,
  `duration_minutes` INTEGER DEFAULT 60,
  `location` VARCHAR(255),
  `meeting_link` VARCHAR(500),
  `status` VARCHAR(20) DEFAULT 'scheduled',
  `feedback` TEXT,
  `rating` INTEGER CHECK (rating >= 1 AND rating <= 5),
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`application_id`) REFERENCES `application` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`interview_type_id`) REFERENCES `interview_type` (`id`),
  FOREIGN KEY (`interviewer_id`) REFERENCES `person` (`id`)
);

-- Job offers
DROP TABLE IF EXISTS `job_offer`;
CREATE TABLE `job_offer` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `application_id` INTEGER NOT NULL,
  `salary_offered` DECIMAL(10,2) NOT NULL,
  `currency` VARCHAR(3) DEFAULT 'USD',
  `benefits` TEXT,
  `start_date` DATE,
  `offer_letter_path` VARCHAR(500),
  `expiry_date` DATE,
  `status` VARCHAR(20) DEFAULT 'draft',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`application_id`) REFERENCES `application` (`id`) ON DELETE CASCADE
);

-- Candidate matching scores
DROP TABLE IF EXISTS `candidate_match`;
CREATE TABLE `candidate_match` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `job_posting_id` INTEGER NOT NULL,
  `person_id` INTEGER NOT NULL,
  `overall_score` DECIMAL(5,2) NOT NULL,
  `skills_score` DECIMAL(5,2),
  `experience_score` DECIMAL(5,2),
  `education_score` DECIMAL(5,2),
  `location_score` DECIMAL(5,2),
  `calculated_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(`job_posting_id`, `person_id`),
  FOREIGN KEY (`job_posting_id`) REFERENCES `job_posting` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`person_id`) REFERENCES `person` (`id`) ON DELETE CASCADE
);

-- System notifications
DROP TABLE IF EXISTS `notification`;
CREATE TABLE `notification` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `recipient_id` INTEGER NOT NULL,
  `title` VARCHAR(255) NOT NULL,
  `message` TEXT NOT NULL,
  `type` VARCHAR(20) DEFAULT 'info',
  `read_status` BOOLEAN DEFAULT 0,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `read_at` DATETIME DEFAULT NULL,
  FOREIGN KEY (`recipient_id`) REFERENCES `person` (`id`) ON DELETE CASCADE
);

-- System configuration
DROP TABLE IF EXISTS `system_config`;
CREATE TABLE `system_config` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `config_key` VARCHAR(100) NOT NULL UNIQUE,
  `config_value` TEXT,
  `description` VARCHAR(255),
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO `system_config` (`config_key`, `config_value`, `description`) VALUES
('max_file_upload_size', '10485760', 'Maximum file upload size in bytes (10MB)'),
('allowed_resume_formats', 'pdf,doc,docx', 'Allowed resume file formats'),
('default_application_expiry_days', '30', 'Default days before application expires'),
('email_notifications_enabled', 'true', 'Enable email notifications'),
('auto_matching_enabled', 'true', 'Enable automatic candidate matching');
