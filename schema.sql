DROP DATABASE IF EXISTS job_tracker;
CREATE DATABASE job_tracker;
USE job_tracker;

CREATE TABLE companies (
    company_id INT PRIMARY KEY AUTO_INCREMENT,
    company_name VARCHAR(100) NOT NULL,
    industry VARCHAR(50),
    website VARCHAR(200),
    city VARCHAR(50),
    state VARCHAR(50),
    notes TEXT
);

CREATE TABLE jobs (
    job_id INT PRIMARY KEY AUTO_INCREMENT,
    company_id INT,
    job_title VARCHAR(100) NOT NULL,
    job_type ENUM('Full-time','Part-time','Contract','Internship'),
    salary_min INT,
    salary_max INT,
    job_url VARCHAR(300),
    date_posted DATE,
    requirements JSON,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

CREATE TABLE applications (
    application_id INT PRIMARY KEY AUTO_INCREMENT,
    job_id INT,
    application_date DATE NOT NULL,
    status ENUM('Applied','Screening','Interview','Offer','Rejected','Withdrawn'),
    resume_version VARCHAR(50),
    cover_letter_sent BOOLEAN,
    interview_data JSON,
    FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE
);

CREATE TABLE contacts (
    contact_id INT PRIMARY KEY AUTO_INCREMENT,
    company_id INT,
    contact_name VARCHAR(100) NOT NULL,
    title VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    linkedin_url VARCHAR(200),
    notes TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

INSERT INTO companies (company_name, industry, website, city, state, notes) VALUES
('TechCorp', 'Software', 'https://techcorp.example.com', 'Miami', 'FL', 'Referred by a friend'),
('DataCo', 'Analytics', 'https://dataco.example.com', 'Orlando', 'FL', NULL);

INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max, job_url, date_posted, requirements) VALUES
(1, 'Software Developer', 'Full-time', 70000, 90000, 'https://techcorp.example.com/jobs/1', '2026-11-01', '["Python","SQL","Flask"]'),
(2, 'Data Analyst', 'Full-time', 60000, 80000, 'https://dataco.example.com/jobs/2', '2026-11-05', '["Python","SQL","Tableau"]');

INSERT INTO applications (job_id, application_date, status, resume_version, cover_letter_sent, interview_data) VALUES
(1, '2026-11-10', 'Applied', 'v2', TRUE, NULL),
(2, '2026-11-12', 'Interview', 'v2', FALSE, '{"round": 1, "date": "2026-11-20"}');

INSERT INTO contacts (company_id, contact_name, title, email, phone, linkedin_url, notes) VALUES
(1, 'Sam Rivera', 'Recruiter', 'sam@techcorp.example.com', '305-555-0101', NULL, 'Met at career fair');