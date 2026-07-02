-- AI-Solutions MySQL Database Script for XAMPP / phpMyAdmin
-- Compatible with MySQL 5.7+ / MariaDB

CREATE DATABASE IF NOT EXISTS ai_solutions2
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE ai_solutions2;

-- --------------------------------------------------------
-- 1. admin_users
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS admin_users (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin','manager','editor') NOT NULL DEFAULT 'admin',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_admin_username (username),
    UNIQUE KEY uk_admin_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- 2. inquiries
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS inquiries (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone_number VARCHAR(30) DEFAULT NULL,
    company_name VARCHAR(150) DEFAULT NULL,
    country VARCHAR(100) DEFAULT NULL,
    job_title VARCHAR(100) DEFAULT NULL,
    job_details TEXT NOT NULL,
    status ENUM('Pending','In Progress','Completed') NOT NULL DEFAULT 'Pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_inquiries_status (status),
    KEY idx_inquiries_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- 3. feedback
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS feedback (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    customer_name VARCHAR(100) NOT NULL,
    company_name VARCHAR(150) DEFAULT NULL,
    rating TINYINT UNSIGNED NOT NULL,
    comment TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CHECK (rating BETWEEN 1 AND 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- Sample data inserts
-- --------------------------------------------------------
INSERT INTO admin_users (username, email, password, role) VALUES
('admin', 'admin@aisolutions.com', 'scrypt:32768:8:1$Zp9MycWZDCe3YxPf$543fc8dafc980e7329e88d114c8717235ff86c1de5484530b8a8d14a44e710dc54ecb024d75a1c892558fe095f812fa75bc8f067676c551c2198f7d36626d254', 'admin');

INSERT INTO inquiries (full_name, email, phone_number, company_name, country, job_title, job_details, status) VALUES
('Asha Sharma', 'asha@example.com', '+9779800000001', 'Nova Labs', 'Nepal', 'Operations Lead', 'We need an AI chatbot for our support team.', 'Pending'),
('Ravi Thapa', 'ravi@example.com', '+9779800000002', 'BluePeak Tech', 'Nepal', 'CTO', 'We want automation for our internal workflows.', 'In Progress');

INSERT INTO feedback (customer_name, company_name, rating, comment) VALUES
('Maya Chen', 'Northstar Labs', 5, 'Excellent implementation and very professional support.'),
('Arjun Patel', 'Signal Systems', 4, 'The team delivered on time and understood our requirements clearly.');

-- --------------------------------------------------------
-- End of script
-- --------------------------------------------------------
