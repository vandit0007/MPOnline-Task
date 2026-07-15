-- ============================================
-- Task Management App - Database Schema
-- ============================================

CREATE DATABASE IF NOT EXISTS task_manager;
USE task_manager;

-- Admin login table
CREATE TABLE IF NOT EXISTS admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Default admin user (username: admin / password: admin123)
-- Change this password after first login in a real deployment!
INSERT INTO admin (username, password)
VALUES ('admin', 'admin123')
ON DUPLICATE KEY UPDATE username = username;

-- Tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL,
    employee_name VARCHAR(100) NOT NULL,
    task_title VARCHAR(255) NOT NULL,
    completed ENUM('Yes', 'No') NOT NULL DEFAULT 'No',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample data (optional, remove if not needed)
INSERT INTO tasks (employee_id, employee_name, task_title, completed)
VALUES
('E101', 'Ravi Kumar', 'Prepare monthly sales report', 'No'),
('E102', 'Anita Sharma', 'Fix login page bug', 'Yes'),
('E103', 'Suresh Raina', 'Update client database', 'No');
