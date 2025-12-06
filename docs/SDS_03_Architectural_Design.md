# Software Design Specification (SDS)
## Document 3: Architectural Design

**Version:** 1.0.0  
**Date:** 2024  
**Project:** Visitor Management System

---

## 3.1 High-Level Architecture

### 3.1.1 Architecture Description

The Visitor Management System follows a three-tier architecture:

1. **Presentation Tier**: React-based single-page application running in web browsers
2. **Application Tier**: FastAPI REST API server handling business logic
3. **Data Tier**: MySQL relational database for data persistence

[Architecture Diagram Placeholder: Three-tier architecture diagram showing React Frontend, FastAPI Backend, and MySQL Database with communication flows]

### 3.1.2 Communication Flow

```
Browser (React Frontend)
    ↓ HTTP/REST API (JSON)
FastAPI Backend (Python)
    ↓ SQL Queries
MySQL Database
```

**Request Flow:**
1. User interacts with React frontend
2. Frontend makes HTTP request to FastAPI backend
3. Backend validates request (authentication, authorization)
4. Backend executes business logic via service layer
5. Backend queries/updates MySQL database
6. Backend returns JSON response
7. Frontend updates UI based on response

---

## 3.2 Subsystem Descriptions

### 3.2.1 Authentication Subsystem

**Location:** `backend/services/auth_service.py`, `backend/api/auth_api.py`, `backend/utils/auth_dependency.py`, `backend/utils/jwt_utils.py`

**Responsibilities:**
- User authentication (login)
- JWT token generation and validation
- Password hashing (SHA256)
- User registration (admin-only)
- User deactivation
- Role retrieval
- Token extraction from HTTP headers

**Components:**
- `login()` - Authenticate user and generate JWT token
- `register_user()` - Create new user account
- `deactivate_user()` - Deactivate user (preserves records)
- `get_user_role()` - Get user's role
- `hash_password()` - Hash password using SHA256
- `generate_jwt_token()` - Create JWT token with user info
- `get_user_from_token()` - Decode and validate JWT token
- `get_current_user_id()` - Extract user_id from Authorization header

**Frontend Integration:**
- `AuthContext` - Manages authentication state
- `Login.jsx` - Login page component
- Token stored in localStorage

### 3.2.2 Visitor Management Subsystem

**Location:** `backend/services/visitor_service.py`, `backend/api/visitor_api.py`

**Responsibilities:**
- Visitor registration
- Visitor search
- CNIC validation
- Visitor information management

**Components:**
- `add_visitor()` - Register new visitor
- `search_visitor()` - Search visitor by CNIC or ID
- `list_visitors()` - Get all visitors

**Frontend Integration:**
- `VisitorEntry.jsx` - Visitor registration form

### 3.2.3 Visit Management Subsystem

**Location:** `backend/services/visit_service.py`, `backend/api/visit_api.py`

**Responsibilities:**
- Visit creation
- Visit status management
- Status transition validation
- Active visit retrieval

**Components:**
- `create_visit()` - Create new visit record
- `update_visit_status()` - Update visit status with validation
- `get_active_visits()` - Get all active visits (pending/checked_in)

**Frontend Integration:**
- `VisitorEntry.jsx` - Visit creation form
- `Dashboard.jsx` - Active visits display

### 3.2.4 Employee Management Subsystem

**Location:** `backend/services/site_service.py`, `backend/api/site_api.py`

**Responsibilities:**
- Employee creation
- Employee information retrieval
- Employee status checking
- Employee attendance logs
- Department management

**Components:**
- `create_employee()` - Create new employee
- `get_all_employees()` - Get all employees
- `get_employee_status()` - Get employee current status
- `get_employee_logs()` - Get employee attendance logs
- `get_all_departments()` - Get all departments
- `get_active_employees_count()` - Count signed-in employees
- `get_signed_in_employees()` - Get list of signed-in employees

**Frontend Integration:**
- `EmployeeManagement.jsx` - Employee management page with create form
- `EmployeeAttendance.jsx` - Employee attendance viewing
- `EmployeeQR.jsx` - Employee QR code generation

### 3.2.5 Salary Calculation Subsystem

**Location:** `backend/services/site_service.py`, `backend/api/site_api.py`

**Responsibilities:**
- Salary calculation based on attendance logs
- Date range filtering
- Hours calculation from sign-in/sign-out pairs
- Excel report generation

**Components:**
- `calculate_employee_salary()` - Calculate salary for date range
- `export_salary_report_to_excel()` - Generate Excel report

**Frontend Integration:**
- `SalaryCalculation.jsx` - Salary calculation page with date range picker and Excel export

### 3.2.6 QR Code Generation Subsystem

**Location:** `backend/services/qr_service.py`, `backend/api/qr_api.py`

**Responsibilities:**
- Employee QR code generation (permanent)
- Visitor QR code generation (temporary)
- QR code image file creation
- QR code email delivery
- QR code download

**Components:**
- `generate_employee_qr()` - Generate permanent employee QR code
- `generate_visitor_qr()` - Generate temporary visitor QR code
- `get_visitor_qr_file()` - Get QR code image file path
- `_send_email_with_qr_link()` - Email QR code download link
- `_ensure_qr_directory()` - Ensure QR storage directory exists

**Frontend Integration:**
- `EmployeeQR.jsx` - Employee QR generation page
- `VisitorEntry.jsx` - Visitor QR generation (automatic after visit creation)

### 3.2.7 QR Scanning Subsystem

**Location:** `backend/services/scan_service.py`, `backend/api/scan_api.py`, `backend/api/attendance_api.py`

**Responsibilities:**
- QR code verification
- Employee attendance scanning
- Visitor check-in/check-out
- Late arrival detection
- Late arrival alerts

**Components:**
- `verify_qr_code()` - Verify QR code and determine type (employee/visitor)
- `scan_employee_qr()` - Process employee QR scan
- `scan_visitor_qr()` - Process visitor QR scan
- `visitor_checkin()` - Check in visitor using QR code
- `visitor_checkout()` - Check out visitor using QR code
- `get_employee_late_count()` - Get late arrival count for employee
- `_get_employee_current_status()` - Get employee's current sign-in status
- `_is_late_checkin()` - Check if check-in is late (after 9:10 AM)
- `_calculate_salary_estimate()` - Calculate salary estimate for late alert

**Frontend Integration:**
- `CheckInOut.jsx` - QR scanning page with camera integration
- `EmployeeAttendance.jsx` - Employee attendance viewing

### 3.2.8 Logging Subsystem

**Location:** `backend/services/logs_service.py`, `backend/api/logs_api.py`, `backend/utils/db_logger.py`

**Responsibilities:**
- Access log creation
- Access log retrieval
- Access log filtering
- Access log export to Excel

**Components:**
- `log_action()` - Log system action to AccessLogs table
- `get_access_logs()` - Get access logs with filters
- `export_access_logs_to_excel()` - Export logs to Excel

**Frontend Integration:**
- `VisitLogs.jsx` - Access logs viewing page with filters and export

### 3.2.9 Attendance Subsystem

**Location:** `backend/services/scan_service.py`, `backend/api/attendance_api.py`

**Responsibilities:**
- Employee attendance tracking via QR scanning
- Automatic sign-in/sign-out toggling
- Attendance log creation

**Components:**
- `scan_employee_qr()` - Process attendance scan
- Attendance endpoint that auto-toggles status

**Frontend Integration:**
- `CheckInOut.jsx` - Attendance scanning interface
- `EmployeeAttendance.jsx` - Attendance history viewing

### 3.2.10 Alert Subsystem

**Location:** `backend/services/alert_service.py`, `backend/api/alert_api.py`

**Responsibilities:**
- Security alert creation
- Visitor flagging
- Flagged visitor retrieval
- Alert management

**Components:**
- `flag_visitor()` - Flag visitor for security reasons
- `get_flagged_visitors()` - Get all flagged visitors
- `check_visitor_flags()` - Check if visitor has active flags

**Frontend Integration:**
- `Dashboard.jsx` - Alert display
- Alert creation during QR scanning

### 3.2.11 Reports Subsystem

**Location:** `backend/services/logs_service.py`, `backend/services/site_service.py`, `backend/api/reports_api.py`, `backend/api/logs_api.py`

**Responsibilities:**
- Access log export to Excel
- Salary report export to Excel
- Excel file generation with formatting

**Components:**
- `export_access_logs_to_excel()` - Export access logs
- `export_salary_report_to_excel()` - Export salary report

**Frontend Integration:**
- `VisitLogs.jsx` - Log export button
- `SalaryCalculation.jsx` - Salary export button

### 3.2.12 Site Management Subsystem

**Location:** `backend/services/site_service.py`, `backend/api/site_api.py`

**Responsibilities:**
- Site creation
- Site list retrieval
- Site information management

**Components:**
- `get_all_sites()` - Get all sites
- `create_site()` - Create new site

**Frontend Integration:**
- `SiteManagement.jsx` - Site management page

---

## 3.3 Component Responsibilities

### 3.3.1 Backend API Layer (`backend/api/`)

**Files:**
- `auth_api.py` - Authentication endpoints
- `visitor_api.py` - Visitor management endpoints
- `visit_api.py` - Visit management endpoints
- `qr_api.py` - QR code generation endpoints
- `scan_api.py` - QR scanning endpoints
- `attendance_api.py` - Attendance scanning endpoint
- `site_api.py` - Site, employee, and salary endpoints
- `logs_api.py` - Access log endpoints
- `reports_api.py` - Report export endpoints
- `alert_api.py` - Alert management endpoints
- `user_management_api.py` - User management endpoints
- `email_api.py` - Email service endpoints

**Responsibilities:**
- HTTP request handling
- Request validation (Pydantic models)
- Authentication/authorization checks
- Response formatting
- Error handling
- Route definition

### 3.3.2 Backend Service Layer (`backend/services/`)

**Files:**
- `auth_service.py` - Authentication business logic
- `visitor_service.py` - Visitor business logic
- `visit_service.py` - Visit business logic
- `qr_service.py` - QR code generation logic
- `scan_service.py` - QR scanning and attendance logic
- `site_service.py` - Site, employee, salary business logic
- `logs_service.py` - Logging and report generation
- `alert_service.py` - Alert management logic
- `email_service.py` - Email sending logic

**Responsibilities:**
- Business logic implementation
- Database queries
- Data validation
- Complex calculations
- File operations (QR images, Excel files)
- Email sending

### 3.3.3 Backend Utilities (`backend/utils/`)

**Files:**
- `auth_dependency.py` - FastAPI dependency for authentication
- `jwt_utils.py` - JWT token generation and validation
- `validator.py` - Input validation functions
- `db_logger.py` - Database logging utility

**Responsibilities:**
- Reusable utility functions
- Authentication dependency injection
- Input validation
- Logging helpers

### 3.3.4 Database Layer (`backend/database/`)

**Files:**
- `connection.py` - Database connection management
- `schema.sql` - Database schema definition

**Responsibilities:**
- Database connection pooling
- Query execution
- Transaction management
- Schema definition

### 3.3.5 Frontend Pages (`frontend/src/pages/`)

**Files:**
- `Login.jsx` - Login page
- `Dashboard.jsx` - Dashboard with statistics
- `VisitorEntry.jsx` - Visitor registration and visit creation
- `CheckInOut.jsx` - QR scanning page
- `EmployeeQR.jsx` - Employee QR generation
- `EmployeeAttendance.jsx` - Employee attendance viewing
- `EmployeeManagement.jsx` - Employee management with create form
- `SalaryCalculation.jsx` - Salary calculation page
- `VisitLogs.jsx` - Access logs viewing
- `UserManagement.jsx` - User management
- `SiteManagement.jsx` - Site management
- `AdminProfile.jsx` - Admin profile page

**Responsibilities:**
- User interface rendering
- User input handling
- API calls
- State management
- Form validation
- Error display

### 3.3.6 Frontend Components (`frontend/src/components/`)

**Files:**
- `Layout.jsx` - Main layout with navigation
- `Layout.css` - Layout styles

**Responsibilities:**
- Common layout structure
- Navigation menu
- Route outlet rendering
- User information display

### 3.3.7 Frontend Contexts (`frontend/src/contexts/`)

**Files:**
- `AuthContext.jsx` - Authentication state management
- `DataContext.jsx` - Sites and employees data caching

**Responsibilities:**
- Global state management
- Authentication state
- Data caching and refresh
- Context provider setup

### 3.3.8 Frontend Services (`frontend/src/services/`)

**Files:**
- `api.js` - Axios API client configuration

**Responsibilities:**
- HTTP client setup
- Token management
- Request/response interceptors
- Error handling

---

## 3.4 Technology Stack

### 3.4.1 Backend Technologies

**Framework:**
- FastAPI 0.104.1 - Modern Python web framework
- Uvicorn 0.24.0 - ASGI server

**Database:**
- MySQL 8.0+ - Relational database
- mysql-connector-python 8.2.0 - MySQL driver

**Authentication:**
- PyJWT 2.8.0 - JWT token handling
- python-jose 3.3.0 - JWT cryptography support

**Data Validation:**
- Pydantic 2.7.0+ - Data validation and settings management
- email-validator 2.1.0 - Email format validation

**Utilities:**
- qrcode[pil] 7.4.2 - QR code generation
- openpyxl 3.1.2 - Excel file generation

**Python Version:**
- Python 3.8 or higher

### 3.4.2 Frontend Technologies

**Framework:**
- React 18.2.0+ - UI library
- React DOM 18.2.0+ - React DOM renderer

**Build Tool:**
- Vite 5.0.8+ - Build tool and dev server
- @vitejs/plugin-react 4.2.1+ - Vite React plugin

**Routing:**
- React Router DOM 6.20.0+ - Client-side routing

**HTTP Client:**
- Axios 1.6.2+ - HTTP client library

**UI Libraries:**
- React Toastify 9.1.3+ - Toast notifications
- qrcode.react 3.1.0+ - QR code display component
- html5-qrcode 2.3.8+ - QR code scanner

**Node.js Version:**
- Node.js 18 or higher

### 3.4.3 Development Tools

**Backend:**
- Python virtual environment
- pip - Package manager

**Frontend:**
- npm - Package manager
- Vite dev server - Development server with HMR

**Database:**
- MySQL command line client
- MySQL Workbench (optional)

---

## 3.5 System Integration Points

### 3.5.1 Frontend-Backend Integration

**Protocol:** HTTP/REST
**Data Format:** JSON
**Authentication:** JWT Bearer tokens in Authorization header
**Base URL:** Configurable via `VITE_API_URL` environment variable (default: `http://localhost:8000`)

### 3.5.2 Backend-Database Integration

**Protocol:** MySQL protocol
**Driver:** mysql-connector-python
**Connection:** Persistent connection via Database class
**Query Method:** Parameterized queries (SQL injection prevention)

### 3.5.3 Email Integration

**Protocol:** SMTP
**Configuration:** Via `config.ini` file
**Library:** Python `smtplib` (standard library)
**Usage:** QR code delivery, late arrival alerts

### 3.5.4 Camera Integration

**API:** HTML5 MediaDevices API (getUserMedia)
**Library:** html5-qrcode
**Usage:** QR code scanning in browser
**Requirements:** HTTPS in production, user permission

---

**End of Document 3: Architectural Design**

