-- Initial setup script for Visitor Management System
-- Run this after creating the database schema

USE Visitor_Management_System;

-- Insert default roles
INSERT INTO Roles (role_name, description) VALUES 
('admin', 'Administrator with full system access'),
('security', 'Security personnel with scanning and visitor viewing access');

-- Insert default admin user (password: admin123)
-- Password hash is SHA256 of 'admin123'
INSERT INTO Users (username, password_hash, role_id) VALUES 
('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 1);

-- Insert sample department
INSERT INTO Departments (name) VALUES ('IT Department');

-- Insert sample site
INSERT INTO Sites (site_name, address) VALUES ('Main Office', '123 Main Street, City, Country');

-- Insert sample employee
INSERT INTO Employees (name, hourly_rate, department_id) VALUES 
('John Doe', 25.00, 1);

