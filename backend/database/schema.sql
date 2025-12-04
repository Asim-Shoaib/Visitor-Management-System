CREATE DATABASE Visitor_Management_System;

USE Visitor_Management_System;

CREATE TABLE Departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE Employees (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    hourly_rate DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    department_id INT NOT NULL,
    FOREIGN KEY (department_id) REFERENCES Departments(department_id)
);

CREATE TABLE Roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name ENUM('admin','security') NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    role_id INT NOT NULL,
    FOREIGN KEY (role_id) REFERENCES Roles(role_id)
);

CREATE TABLE AccessLogs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action VARCHAR(255) NOT NULL,
    details TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE Sites (
    site_id INT AUTO_INCREMENT PRIMARY KEY,
    site_name VARCHAR(150) NOT NULL UNIQUE,
    address TEXT
);

CREATE TABLE Visitors (
    visitor_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    cnic VARCHAR(15) NOT NULL UNIQUE,
    contact_number VARCHAR(50),
    CHECK (cnic REGEXP '^[0-9]{5}-[0-9]{7}-[0-9]$')
);

CREATE TABLE Visits (
    visit_id INT AUTO_INCREMENT PRIMARY KEY,
    visitor_id INT NOT NULL,
    site_id INT NOT NULL,
    host_employee_id INT NULL,
    purpose_details TEXT,
    status ENUM('pending','checked_in','checked_out','denied') DEFAULT 'pending',
    checkin_time DATETIME NULL,
    checkout_time DATETIME NULL,
    issue_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (visitor_id) REFERENCES Visitors(visitor_id),
    FOREIGN KEY (site_id) REFERENCES Sites(site_id),
    FOREIGN KEY (host_employee_id) REFERENCES Employees(employee_id)
);

CREATE TABLE EmployeeQRCodes (
    emp_qr_id INT AUTO_INCREMENT PRIMARY KEY,
    code_value VARCHAR(150) NOT NULL UNIQUE,
    employee_id INT NOT NULL,
    issue_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    expiry_date DATETIME NULL,
    status ENUM('active','expired','revoked') DEFAULT 'active',
    FOREIGN KEY (employee_id) REFERENCES Employees(employee_id)
);

CREATE TABLE VisitorQRCodes (
    visitor_qr_id INT AUTO_INCREMENT PRIMARY KEY,
    code_value VARCHAR(150) NOT NULL UNIQUE,
    visit_id INT NOT NULL,
    issue_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    expiry_date DATETIME NOT NULL,
    status ENUM('active','expired','revoked') DEFAULT 'active',
    FOREIGN KEY (visit_id) REFERENCES Visits(visit_id)
);

CREATE TABLE Alerts (
    alert_id INT AUTO_INCREMENT PRIMARY KEY,
    triggered_by INT NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (triggered_by) REFERENCES VisitorQRCodes(visitor_qr_id)
);

CREATE TABLE EmployeeScanLogs (
    scan_id INT AUTO_INCREMENT PRIMARY KEY,
    emp_qr_id INT NOT NULL,
    scan_status ENUM('signin','signout') DEFAULT 'signin',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (emp_qr_id) REFERENCES EmployeeQRCodes(emp_qr_id)
);

CREATE TABLE VisitorScanLogs (
    scan_id INT AUTO_INCREMENT PRIMARY KEY,
    visitor_qr_id INT NOT NULL,
    scan_status ENUM('signin','signout') DEFAULT 'signin',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (visitor_qr_id) REFERENCES VisitorQRCodes(visitor_qr_id)
);

