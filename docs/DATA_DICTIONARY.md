# Data Dictionary

## Overview

This document describes all database tables, their fields, data types, constraints, and relationships in the Visitor Management System.

---

## Tables

### 1. Departments

**Purpose:** Organizational departments for employee categorization.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| department_id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique department identifier |
| name | VARCHAR(100) | NOT NULL, UNIQUE | Department name |

**Relationships:**
- One-to-Many with `Employees`

**Sample Data:**
```
department_id: 1
name: "IT Department"
```

---

### 2. Employees

**Purpose:** Employee records with hourly rate and department assignment.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| employee_id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique employee identifier |
| name | VARCHAR(100) | NOT NULL | Employee full name |
| hourly_rate | DECIMAL(10,2) | NOT NULL, DEFAULT 0.00 | Hourly wage rate |
| department_id | INT | NOT NULL, FOREIGN KEY | Reference to Departments |

**Relationships:**
- Many-to-One with `Departments`
- One-to-Many with `EmployeeQRCodes`
- One-to-Many with `Visits` (as host_employee_id)

**Sample Data:**
```
employee_id: 1
name: "John Doe"
hourly_rate: 25.00
department_id: 1
```

---

### 3. Roles

**Purpose:** System user roles for access control.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| role_id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique role identifier |
| role_name | ENUM('admin','security') | NOT NULL, UNIQUE | Role name |
| description | TEXT | NULL | Role description |

**Relationships:**
- One-to-Many with `Users`

**Sample Data:**
```
role_id: 1
role_name: "admin"
description: "Administrator with full system access"
```

---

### 4. Users

**Purpose:** System user accounts for authentication.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| user_id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique user identifier |
| username | VARCHAR(150) | NOT NULL, UNIQUE | Login username |
| password_hash | VARCHAR(255) | NOT NULL | SHA256 hashed password |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |
| role_id | INT | NOT NULL, FOREIGN KEY | Reference to Roles |

**Relationships:**
- Many-to-One with `Roles`
- One-to-Many with `AccessLogs`

**Sample Data:**
```
user_id: 1
username: "admin"
password_hash: "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"
created_at: "2024-01-01 00:00:00"
role_id: 1
```

**Security Notes:**
- Passwords are hashed using SHA256
- Never store plaintext passwords

---

### 5. AccessLogs

**Purpose:** Audit trail of all system actions.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| log_id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique log identifier |
| user_id | INT | NOT NULL, FOREIGN KEY | User who performed action |
| action | VARCHAR(255) | NOT NULL | Action type (e.g., "login", "create_employee") |
| details | TEXT | NULL | Additional action details |
| timestamp | DATETIME | DEFAULT CURRENT_TIMESTAMP | Action timestamp |

**Relationships:**
- Many-to-One with `Users`

**Sample Data:**
```
log_id: 1
user_id: 1
action: "login"
details: "User admin logged in"
timestamp: "2024-01-01 10:00:00"
```

**Common Actions:**
- `login`, `logout`
- `create_employee`, `create_visit`, `register_user`
- `scan_employee`, `scan_visitor`
- `generate_qr`, `checkin`, `checkout`

---

### 6. Sites

**Purpose:** Physical locations/offices.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| site_id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique site identifier |
| site_name | VARCHAR(150) | NOT NULL, UNIQUE | Site name |
| address | TEXT | NULL | Physical address |

**Relationships:**
- One-to-Many with `Visits`

**Sample Data:**
```
site_id: 1
site_name: "Main Office"
address: "123 Main Street, City, Country"
```

---

### 7. Visitors

**Purpose:** Visitor registration information.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| visitor_id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique visitor identifier |
| full_name | VARCHAR(150) | NOT NULL | Visitor full name |
| cnic | VARCHAR(15) | NOT NULL, UNIQUE | CNIC number (format: XXXXX-XXXXXXX-X) |
| contact_number | VARCHAR(50) | NULL | Contact phone number |

**Constraints:**
- CNIC format validation: `^[0-9]{5}-[0-9]{7}-[0-9]$`

**Relationships:**
- One-to-Many with `Visits`

**Sample Data:**
```
visitor_id: 1
full_name: "Jane Smith"
cnic: "12345-1234567-1"
contact_number: "+1234567890"
```

---

### 8. Visits

**Purpose:** Visit records linking visitors to sites.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| visit_id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique visit identifier |
| visitor_id | INT | NOT NULL, FOREIGN KEY | Reference to Visitors |
| site_id | INT | NOT NULL, FOREIGN KEY | Reference to Sites |
| host_employee_id | INT | NULL, FOREIGN KEY | Reference to Employees (optional) |
| purpose_details | TEXT | NULL | Visit purpose description |
| status | ENUM | DEFAULT 'pending' | Visit status: 'pending', 'checked_in', 'checked_out', 'denied' |
| checkin_time | DATETIME | NULL | Visitor check-in timestamp |
| checkout_time | DATETIME | NULL | Visitor check-out timestamp |
| issue_date | DATETIME | DEFAULT CURRENT_TIMESTAMP | Visit creation timestamp |

**Relationships:**
- Many-to-One with `Visitors`
- Many-to-One with `Sites`
- Many-to-One with `Employees` (optional host)
- One-to-Many with `VisitorQRCodes`

**Status Flow:**
```
pending → checked_in → checked_out
   ↓
denied
```

**Sample Data:**
```
visit_id: 1
visitor_id: 1
site_id: 1
host_employee_id: 1
purpose_details: "Business meeting"
status: "checked_in"
checkin_time: "2024-01-01 10:00:00"
checkout_time: "2024-01-01 18:00:00"
issue_date: "2024-01-01 09:00:00"
```

---

### 9. EmployeeQRCodes

**Purpose:** Permanent QR codes for employee attendance.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| emp_qr_id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique QR code identifier |
| code_value | VARCHAR(150) | NOT NULL, UNIQUE | QR code string value |
| employee_id | INT | NOT NULL, FOREIGN KEY | Reference to Employees |
| issue_date | DATETIME | DEFAULT CURRENT_TIMESTAMP | QR code creation timestamp |
| expiry_date | DATETIME | NULL | Expiry date (NULL = permanent) |
| status | ENUM | DEFAULT 'active' | Status: 'active', 'expired', 'revoked' |

**Relationships:**
- Many-to-One with `Employees`
- One-to-Many with `EmployeeScanLogs`

**Sample Data:**
```
emp_qr_id: 1
code_value: "EMP_1_abc123def456"
employee_id: 1
issue_date: "2024-01-01 00:00:00"
expiry_date: NULL
status: "active"
```

**Notes:**
- Employee QR codes are typically permanent (expiry_date = NULL)
- Status can be 'revoked' to disable QR code

---

### 10. VisitorQRCodes

**Purpose:** Temporary QR codes for visitor visits.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| visitor_qr_id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique QR code identifier |
| code_value | VARCHAR(150) | NOT NULL, UNIQUE | QR code string value |
| visit_id | INT | NOT NULL, FOREIGN KEY | Reference to Visits |
| issue_date | DATETIME | DEFAULT CURRENT_TIMESTAMP | QR code creation timestamp |
| expiry_date | DATETIME | NOT NULL | QR code expiry timestamp |
| status | ENUM | DEFAULT 'active' | Status: 'active', 'expired', 'revoked' |

**Relationships:**
- Many-to-One with `Visits`
- One-to-Many with `VisitorScanLogs`
- One-to-Many with `Alerts`

**Sample Data:**
```
visitor_qr_id: 1
code_value: "VIS_1_xyz789abc123"
visit_id: 1
issue_date: "2024-01-01 09:00:00"
expiry_date: "2024-01-02 09:00:00"
status: "active"
```

**Notes:**
- Visitor QR codes have expiry dates (typically 24 hours)
- Status automatically changes to 'expired' after expiry_date

---

### 11. Alerts

**Purpose:** Security alerts and visitor flags.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| alert_id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique alert identifier |
| triggered_by | INT | NOT NULL, FOREIGN KEY | Reference to VisitorQRCodes |
| description | TEXT | NULL | Alert description/reason |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Alert creation timestamp |

**Relationships:**
- Many-to-One with `VisitorQRCodes`

**Sample Data:**
```
alert_id: 1
triggered_by: 1
description: "Invalid QR code scanned"
created_at: "2024-01-01 10:00:00"
```

**Common Alert Types:**
- Invalid QR code scans
- Expired QR code scans
- Revoked QR code scans
- Visitor security flags

---

### 12. EmployeeScanLogs

**Purpose:** Employee attendance tracking (sign-in/sign-out).

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| scan_id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique scan identifier |
| emp_qr_id | INT | NOT NULL, FOREIGN KEY | Reference to EmployeeQRCodes |
| scan_status | ENUM | DEFAULT 'signin' | Status: 'signin', 'signout' |
| timestamp | DATETIME | DEFAULT CURRENT_TIMESTAMP | Scan timestamp |

**Relationships:**
- Many-to-One with `EmployeeQRCodes`

**Sample Data:**
```
scan_id: 1
emp_qr_id: 1
scan_status: "signin"
timestamp: "2024-01-01 09:00:00"
```

**Usage:**
- Calculate working hours for salary calculation
- Track attendance patterns
- Detect late arrivals (after 9:10 AM)

**Calculation Logic:**
- Pair signin with next signout for same day
- Calculate hours = signout_time - signin_time
- Sum all paired hours for total working hours

---

### 13. VisitorScanLogs

**Purpose:** Visitor entry/exit tracking.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| scan_id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique scan identifier |
| visitor_qr_id | INT | NOT NULL, FOREIGN KEY | Reference to VisitorQRCodes |
| scan_status | ENUM | DEFAULT 'signin' | Status: 'signin', 'signout' |
| timestamp | DATETIME | DEFAULT CURRENT_TIMESTAMP | Scan timestamp |

**Relationships:**
- Many-to-One with `VisitorQRCodes`

**Sample Data:**
```
scan_id: 1
visitor_qr_id: 1
scan_status: "signin"
timestamp: "2024-01-01 10:00:00"
```

**Usage:**
- Track visitor entry and exit times
- Audit trail for security
- Visit duration calculation

---

## Entity Relationship Diagram (ERD)

### Key Relationships

```
Departments (1) ──< (Many) Employees
Employees (1) ──< (Many) EmployeeQRCodes
EmployeeQRCodes (1) ──< (Many) EmployeeScanLogs

Roles (1) ──< (Many) Users
Users (1) ──< (Many) AccessLogs

Sites (1) ──< (Many) Visits
Visitors (1) ──< (Many) Visits
Employees (1) ──< (Many) Visits (as host)

Visits (1) ──< (Many) VisitorQRCodes
VisitorQRCodes (1) ──< (Many) VisitorScanLogs
VisitorQRCodes (1) ──< (Many) Alerts
```

---

## Data Types Reference

### ENUM Types

**Roles.role_name:**
- `'admin'` - Administrator
- `'security'` - Security personnel

**Visits.status:**
- `'pending'` - Visit created, not yet checked in
- `'checked_in'` - Visitor has checked in
- `'checked_out'` - Visitor has checked out
- `'denied'` - Visit denied/rejected

**EmployeeQRCodes.status / VisitorQRCodes.status:**
- `'active'` - QR code is active and valid
- `'expired'` - QR code has expired
- `'revoked'` - QR code has been revoked

**EmployeeScanLogs.scan_status / VisitorScanLogs.scan_status:**
- `'signin'` - Sign in / Check in
- `'signout'` - Sign out / Check out

---

## Indexes

### Primary Keys
- All tables have `id` fields as PRIMARY KEY with AUTO_INCREMENT

### Foreign Keys
- All foreign key relationships are enforced
- Cascade behavior: None (preserve data integrity)

### Unique Constraints
- `Departments.name`
- `Users.username`
- `Visitors.cnic`
- `Sites.site_name`
- `EmployeeQRCodes.code_value`
- `VisitorQRCodes.code_value`
- `Roles.role_name`

---

## Data Validation Rules

1. **CNIC Format:** `^[0-9]{5}-[0-9]{7}-[0-9]$`
2. **Password:** Minimum length and complexity (enforced in application)
3. **Email:** Valid email format (enforced in application)
4. **Hourly Rate:** Non-negative decimal value
5. **Dates:** Valid datetime format, logical date ranges

---

## Sample Queries

### Get Employee with Department
```sql
SELECT e.*, d.name as department_name
FROM Employees e
LEFT JOIN Departments d ON e.department_id = d.department_id;
```

### Get Active Visits
```sql
SELECT v.*, vi.full_name, s.site_name
FROM Visits v
JOIN Visitors vi ON v.visitor_id = vi.visitor_id
JOIN Sites s ON v.site_id = s.site_id
WHERE v.status IN ('pending', 'checked_in');
```

### Calculate Employee Hours (Last 30 Days)
```sql
SELECT 
    e.employee_id,
    e.name,
    SUM(TIMESTAMPDIFF(HOUR, signin.timestamp, signout.timestamp)) as total_hours
FROM Employees e
JOIN EmployeeQRCodes eqr ON e.employee_id = eqr.employee_id
JOIN EmployeeScanLogs signin ON eqr.emp_qr_id = signin.emp_qr_id
JOIN EmployeeScanLogs signout ON eqr.emp_qr_id = signout.emp_qr_id
WHERE signin.scan_status = 'signin'
  AND signout.scan_status = 'signout'
  AND signin.timestamp < signout.timestamp
  AND DATE(signin.timestamp) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY e.employee_id, e.name;
```

---

## Notes

- All timestamps use `DATETIME` type
- All monetary values use `DECIMAL(10,2)` for precision
- Foreign keys ensure referential integrity
- Unique constraints prevent duplicate data
- AUTO_INCREMENT ensures unique IDs

