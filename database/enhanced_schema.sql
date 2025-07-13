
-- Enhanced Recruitment System Database Schema
-- Supports: user management, resume parsing, job posting, candidate matching, 
-- interview scheduling, offer generation

-- Core user roles
DROP TABLE IF EXISTS `role`;
CREATE TABLE `role` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `description` varchar(255),
  PRIMARY KEY (`id`)
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
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `firstname` varchar(45) DEFAULT NULL,
  `lastname` varchar(45) DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  `email` varchar(100) UNIQUE DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `linkedin_url` varchar(255) DEFAULT NULL,
  `portfolio_url` varchar(255) DEFAULT NULL,
  `role_id` int(11) DEFAULT '2',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_active` boolean DEFAULT true,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_person_role` FOREIGN KEY (`role_id`) REFERENCES `role` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
);

-- Credentials
DROP TABLE IF EXISTS `credential`;
CREATE TABLE `credential` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `person_id` int(11) NOT NULL,
  `username` varchar(45) NOT NULL UNIQUE,
  `password` varchar(255) NOT NULL,
  `last_login` datetime DEFAULT NULL,
  `password_reset_token` varchar(255) DEFAULT NULL,
  `password_reset_expires` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_credential_person` FOREIGN KEY (`person_id`) REFERENCES `person` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Job categories
DROP TABLE IF EXISTS `job_category`;
CREATE TABLE `job_category` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `description` text,
  PRIMARY KEY (`id`)
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
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `requirements` text,
  `responsibilities` text,
  `salary_min` decimal(10,2) DEFAULT NULL,
  `salary_max` decimal(10,2) DEFAULT NULL,
  `currency` varchar(3) DEFAULT 'USD',
  `location` varchar(255),
  `remote_allowed` boolean DEFAULT false,
  `employment_type` enum('full-time', 'part-time', 'contract', 'internship') DEFAULT 'full-time',
  `experience_level` enum('entry', 'mid', 'senior', 'executive') DEFAULT 'mid',
  `category_id` int(11),
  `posted_by` int(11) NOT NULL,
  `status` enum('draft', 'active', 'closed', 'on-hold') DEFAULT 'draft',
  `application_deadline` date,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_job_category` FOREIGN KEY (`category_id`) REFERENCES `job_category` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_job_poster` FOREIGN KEY (`posted_by`) REFERENCES `person` (`id`) ON DELETE CASCADE
);

-- Competences/Skills
DROP TABLE IF EXISTS `competence`;
CREATE TABLE `competence` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `category` varchar(50) DEFAULT NULL,
  `description` text,
  PRIMARY KEY (`id`)
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
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `person_id` int(11) NOT NULL,
  `file_path` varchar(500),
  `file_name` varchar(255),
  `file_size` bigint,
  `content_text` longtext,
  `parsed_data` json,
  `upload_date` datetime DEFAULT CURRENT_TIMESTAMP,
  `is_primary` boolean DEFAULT false,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_resume_person` FOREIGN KEY (`person_id`) REFERENCES `person` (`id`) ON DELETE CASCADE
);

-- Availability
DROP TABLE IF EXISTS `availability`;
CREATE TABLE `availability` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `person_id` int(11) NOT NULL,
  `from_date` date NOT NULL,
  `to_date` date NOT NULL,
  `is_flexible` boolean DEFAULT false,
  `notes` text,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_availability_person` FOREIGN KEY (`person_id`) REFERENCES `person` (`id`) ON DELETE CASCADE
);

-- Application status
DROP TABLE IF EXISTS `status`;
CREATE TABLE `status` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `description` varchar(255),
  `order_index` int DEFAULT 0,
  PRIMARY KEY (`id`)
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
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `person_id` int(11) NOT NULL,
  `job_posting_id` int(11) NOT NULL,
  `resume_id` int(11),
  `cover_letter` text,
  `date_of_registration` datetime DEFAULT CURRENT_TIMESTAMP,
  `status_id` int(11) DEFAULT 0,
  `match_score` decimal(5,2) DEFAULT NULL,
  `notes` text,
  `last_updated` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_person_job` (`person_id`, `job_posting_id`),
  CONSTRAINT `fk_application_person` FOREIGN KEY (`person_id`) REFERENCES `person` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_application_job` FOREIGN KEY (`job_posting_id`) REFERENCES `job_posting` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_application_resume` FOREIGN KEY (`resume_id`) REFERENCES `resume` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_application_status` FOREIGN KEY (`status_id`) REFERENCES `status` (`id`) ON DELETE SET NULL
);

-- Competence profiles for applications
DROP TABLE IF EXISTS `competence_profile`;
CREATE TABLE `competence_profile` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `application_id` int(11) DEFAULT NULL,
  `person_id` int(11) DEFAULT NULL,
  `competence_id` int(11) NOT NULL,
  `years_of_experience` decimal(4,2) DEFAULT NULL,
  `proficiency_level` enum('beginner', 'intermediate', 'advanced', 'expert') DEFAULT 'intermediate',
  `verified` boolean DEFAULT false,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_competence_profile_application` FOREIGN KEY (`application_id`) REFERENCES `application` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_competence_profile_person` FOREIGN KEY (`person_id`) REFERENCES `person` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_competence_profile_competence` FOREIGN KEY (`competence_id`) REFERENCES `competence` (`id`) ON DELETE CASCADE
);

-- Interview types
DROP TABLE IF EXISTS `interview_type`;
CREATE TABLE `interview_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `description` text,
  `duration_minutes` int DEFAULT 60,
  PRIMARY KEY (`id`)
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
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `application_id` int(11) NOT NULL,
  `interview_type_id` int(11) NOT NULL,
  `interviewer_id` int(11) NOT NULL,
  `scheduled_date` datetime NOT NULL,
  `duration_minutes` int DEFAULT 60,
  `location` varchar(255),
  `meeting_link` varchar(500),
  `status` enum('scheduled', 'completed', 'cancelled', 'rescheduled') DEFAULT 'scheduled',
  `feedback` text,
  `rating` int CHECK (rating >= 1 AND rating <= 5),
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_interview_application` FOREIGN KEY (`application_id`) REFERENCES `application` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_interview_type` FOREIGN KEY (`interview_type_id`) REFERENCES `interview_type` (`id`),
  CONSTRAINT `fk_interview_interviewer` FOREIGN KEY (`interviewer_id`) REFERENCES `person` (`id`)
);

-- Job offers
DROP TABLE IF EXISTS `job_offer`;
CREATE TABLE `job_offer` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `application_id` int(11) NOT NULL,
  `salary_offered` decimal(10,2) NOT NULL,
  `currency` varchar(3) DEFAULT 'USD',
  `benefits` text,
  `start_date` date,
  `offer_letter_path` varchar(500),
  `expiry_date` date,
  `status` enum('draft', 'sent', 'accepted', 'rejected', 'expired') DEFAULT 'draft',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_offer_application` FOREIGN KEY (`application_id`) REFERENCES `application` (`id`) ON DELETE CASCADE
);

-- Candidate matching scores
DROP TABLE IF EXISTS `candidate_match`;
CREATE TABLE `candidate_match` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `job_posting_id` int(11) NOT NULL,
  `person_id` int(11) NOT NULL,
  `overall_score` decimal(5,2) NOT NULL,
  `skills_score` decimal(5,2),
  `experience_score` decimal(5,2),
  `education_score` decimal(5,2),
  `location_score` decimal(5,2),
  `calculated_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_job_person_match` (`job_posting_id`, `person_id`),
  CONSTRAINT `fk_match_job` FOREIGN KEY (`job_posting_id`) REFERENCES `job_posting` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_match_person` FOREIGN KEY (`person_id`) REFERENCES `person` (`id`) ON DELETE CASCADE
);

-- System notifications
DROP TABLE IF EXISTS `notification`;
CREATE TABLE `notification` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `recipient_id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `message` text NOT NULL,
  `type` enum('info', 'success', 'warning', 'error') DEFAULT 'info',
  `read_status` boolean DEFAULT false,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `read_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_notification_recipient` FOREIGN KEY (`recipient_id`) REFERENCES `person` (`id`) ON DELETE CASCADE
);

-- System configuration
DROP TABLE IF EXISTS `system_config`;
CREATE TABLE `system_config` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `config_key` varchar(100) NOT NULL UNIQUE,
  `config_value` text,
  `description` varchar(255),
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
);

INSERT INTO `system_config` (`config_key`, `config_value`, `description`) VALUES
('max_file_upload_size', '10485760', 'Maximum file upload size in bytes (10MB)'),
('allowed_resume_formats', 'pdf,doc,docx', 'Allowed resume file formats'),
('default_application_expiry_days', '30', 'Default days before application expires'),
('email_notifications_enabled', 'true', 'Enable email notifications'),
('auto_matching_enabled', 'true', 'Enable automatic candidate matching');
