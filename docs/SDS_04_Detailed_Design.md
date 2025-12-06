# Software Design Specification (SDS)
## Document 4: Detailed Design

**Version:** 1.0.0  
**Date:** 2024  
**Project:** Visitor Management System

---

## 4.1 Component / Class Design

### 4.1.1 Backend Service Components

#### Authentication Service (`backend/services/auth_service.py`)

**Functions:**
- `hash_password(password: str) -> str`
  - Hashes password using SHA256
  - Returns hex digest string
  
- `login(username: str, password: str) -> Optional[Dict]`
  - Validates credentials
  - Generates JWT token
  - Returns user info with token
  
- `register_user(username: str, password: str, role_name: str, admin_user_id: int) -> bool`
  - Creates new user account
  - Validates username uniqueness
  - Hashes password
  - Returns True on success
  
- `deactivate_user(user_id: int, admin_user_id: int) -> bool`
  - Deactivates user (preserves records)
  - Prevents self-deactivation
  - Returns True on success
  
- `get_user_role(user_id: int) -> Optional[str]`
  - Retrieves user's role name
  - Returns "admin" or "security"
  
- `get_user_info(user_id: int) -> Optional[Dict]`
  - Gets user information
  - Returns dict with user_id, username, role_name, created_at

#### Visitor Service (`backend/services/visitor_service.py`)

**Functions:**
- `add_visitor(full_name: str, cnic: str, contact_number: Optional[str]) -> Optional[int]`
  - Validates CNIC format
  - Validates name
  - Inserts visitor record
  - Returns visitor_id on success
  
- `search_visitor(*, cnic: Optional[str], visitor_id: Optional[int]) -> Optional[Dict]`
  - Searches by CNIC or visitor_id
  - Returns visitor information
  
- `list_visitors() -> List[Dict]`
  - Gets all visitors
  - Returns list of visitor dictionaries

#### Visit Service (`backend/services/visit_service.py`)

**Functions:**
- `create_visit(visitor_id: int, site_id: int, purpose_details: Optional[str], host_employee_id: Optional[int], requested_by_user_id: int) -> Optional[int]`
  - Validates visitor, site, employee
  - Prevents duplicate active visits
  - Inserts visit record
  - Returns visit_id on success
  
- `update_visit_status(visit_id: int, new_status: str, requested_by_user_id: int) -> bool`
  - Validates status transitions
  - Updates status and timestamps
  - Returns True on success
  
- `get_active_visits() -> List[Dict]`
  - Gets all active visits (pending/checked_in)
  - Joins with Visitors, Sites, Employees
  - Returns list of visit dictionaries

#### QR Service (`backend/services/qr_service.py`)

**Functions:**
- `generate_employee_qr(employee_id: int, requested_by_user_id: int) -> Optional[Dict]`
  - Generates permanent QR code
  - Creates QR image file
  - Inserts EmployeeQRCodes record
  - Returns QR information
  
- `generate_visitor_qr(visit_id: int, recipient_email: str, requested_by_user_id: int) -> Optional[Dict]`
  - Generates temporary QR code (24-hour expiry)
  - Creates QR image file
  - Inserts VisitorQRCodes record
  - Sends email with download link
  - Returns QR information
  
- `get_visitor_qr_file(visitor_qr_id: int) -> Optional[str]`
  - Gets QR code file path
  - Returns file path string
  
- `_generate_qr_code_image(data: str, filepath: str) -> bool`
  - Generates QR code image using qrcode library
  - Saves to filepath
  - Returns True on success
  
- `_send_email_with_qr_link(recipient_email: str, visitor_name: str, download_url: str, expiry_date: datetime) -> bool`
  - Sends email via SMTP
  - Includes QR code download link
  - Returns True on success

#### Scan Service (`backend/services/scan_service.py`)

**Functions:**
- `scan_employee_qr(emp_qr_id: int, scan_status: str, scanned_by_user_id: int) -> Optional[Dict]`
  - Validates QR code status
  - Inserts EmployeeScanLogs record
  - Detects late arrival
  - Triggers late alert if needed
  - Returns scan result
  
- `scan_visitor_qr(visitor_qr_id: int, scan_status: str, scanned_by_user_id: int) -> Optional[Dict]`
  - Validates QR code status
  - Inserts VisitorScanLogs record
  - Updates visit status
  - Returns scan result
  
- `verify_qr_code(qr_code: str, scanned_by_user_id: int) -> Optional[Dict]`
  - Verifies QR code format
  - Determines type (employee/visitor)
  - Returns verification result
  
- `visitor_checkin(qr_code: str, scanned_by_user_id: int) -> Optional[Dict]`
  - Verifies visitor QR code
  - Updates visit status to checked_in
  - Sets checkin_time
  - Returns check-in result
  
- `visitor_checkout(qr_code: str, scanned_by_user_id: int) -> Optional[Dict]`
  - Verifies visitor QR code
  - Updates visit status to checked_out
  - Sets checkout_time
  - Returns check-out result
  
- `get_employee_late_count(employee_id: int) -> Dict`
  - Counts late arrivals in last 30 days
  - Returns count dictionary
  
- `_is_late_checkin(scan_time: datetime) -> bool`
  - Checks if time is after 9:10 AM
  - Returns True if late
  
- `_get_late_count_last_30_days(employee_id: int) -> int`
  - Counts late check-ins in last 30 days
  - Returns count integer

#### Site Service (`backend/services/site_service.py`)

**Functions:**
- `get_all_sites() -> List[Dict]`
  - Gets all sites
  - Returns list of site dictionaries
  
- `create_site(site_name: str, address: Optional[str], created_by_user_id: int) -> Optional[int]`
  - Creates new site
  - Validates site_name uniqueness
  - Returns site_id on success
  
- `get_all_departments() -> List[Dict]`
  - Gets all departments
  - Returns list of department dictionaries
  
- `get_all_employees() -> List[Dict]`
  - Gets all employees with department info
  - Returns list of employee dictionaries
  
- `create_employee(name: str, hourly_rate: float, department_id: int, created_by_user_id: int) -> Optional[int]`
  - Validates name, hourly_rate, department_id
  - Inserts employee record
  - Returns employee_id on success
  
- `get_employee_status(employee_id: int) -> Optional[Dict]`
  - Gets employee current sign-in status
  - Returns status dictionary
  
- `get_employee_logs(employee_id: int, days: int = 30) -> List[Dict]`
  - Gets employee attendance logs
  - Returns list of log dictionaries
  
- `calculate_employee_salary(employee_id: int, start_date: Optional[str], end_date: Optional[str]) -> Optional[Dict]`
  - Calculates salary from attendance logs
  - Handles missing sign-outs (end-of-day)
  - Returns salary breakdown dictionary
  
- `export_salary_report_to_excel(employee_id: int, start_date: Optional[str], end_date: Optional[str]) -> Optional[BytesIO]`
  - Generates Excel report
  - Includes summary and daily breakdown
  - Returns BytesIO object

#### Logs Service (`backend/services/logs_service.py`)

**Functions:**
- `get_access_logs(start_date: Optional[str], end_date: Optional[str], action: Optional[str]) -> List[Dict]`
  - Gets access logs with filters
  - Returns up to 1000 most recent logs
  - Returns list of log dictionaries
  
- `export_access_logs_to_excel(start_date: Optional[str], end_date: Optional[str], action: Optional[str]) -> BytesIO`
  - Exports logs to Excel
  - Returns BytesIO object

#### Alert Service (`backend/services/alert_service.py`)

**Functions:**
- `flag_visitor(visitor_id: int, reason: str, flagged_by_user_id: int) -> Optional[Dict]`
  - Flags visitor for security reasons
  - Creates alert record
  - Returns alert information
  
- `get_flagged_visitors() -> List[Dict]`
  - Gets all flagged visitors
  - Returns list of flagged visitor dictionaries
  
- `check_visitor_flags(visitor_id: int) -> List[Dict]`
  - Checks if visitor has active flags
  - Returns list of flag dictionaries

#### Email Service (`backend/services/email_service.py`)

**Functions:**
- `send_qr_code_email(recipient_email: str, visitor_id: int, qr_code_data: str, requested_by_user_id: int) -> Dict`
  - Sends QR code email
  - Returns email result dictionary
  
- `send_late_arrival_alert(employee_id: int, late_count: int, salary_estimate: float, requested_by_user_id: int) -> Dict`
  - Sends late arrival alert email
  - Returns email result dictionary

### 4.1.2 Backend API Routers

#### Auth API (`backend/api/auth_api.py`)

**Pydantic Models:**
- `LoginRequest`: username, password
- `RegisterRequest`: username, password, role_name

**Endpoints:**
- `POST /auth/login` - Public login
- `POST /auth/register-user` - Admin-only user registration
- `PATCH /auth/deactivate-user/{user_id}` - Admin-only user deactivation
- `GET /auth/me` - Get current user info

#### Visitor API (`backend/api/visitor_api.py`)

**Pydantic Models:**
- `AddVisitorRequest`: full_name, cnic, contact_number
- `CheckInOutRequest`: qr_code

**Endpoints:**
- `POST /visitor/add-visitor` - Add visitor
- `GET /visitor/search-visitor` - Search visitor
- `POST /visitor/checkin` - Check in visitor
- `POST /visitor/checkout` - Check out visitor

#### Visit API (`backend/api/visit_api.py`)

**Pydantic Models:**
- `CreateVisitRequest`: visitor_id, site_id, purpose_details, host_employee_id
- `UpdateStatusRequest`: status

**Endpoints:**
- `POST /visit/create-visit` - Create visit
- `PATCH /visit/update-status/{visit_id}` - Update visit status
- `GET /visit/active-visits` - Get active visits

#### QR API (`backend/api/qr_api.py`)

**Pydantic Models:**
- `GenerateEmployeeQRRequest`: employee_id
- `GenerateVisitorQRRequest`: visit_id, recipient_email

**Endpoints:**
- `POST /qr/generate-employee` - Generate employee QR
- `POST /qr/generate-visitor` - Generate visitor QR
- `GET /qr/download/{visitor_qr_id}` - Download QR image
- `GET /qr/debug/visit/{visit_id}` - Debug visit info

#### Scan API (`backend/api/scan_api.py`)

**Pydantic Models:**
- `ScanEmployeeRequest`: emp_qr_id, scan_status
- `ScanVisitorRequest`: visitor_qr_id, scan_status
- `VerifyQRRequest`: qr_code

**Endpoints:**
- `POST /scan/employee` - Scan employee QR
- `POST /scan/visitor` - Scan visitor QR
- `POST /scan/verify` - Verify QR code
- `GET /scan/alerts` - Get alerts
- `GET /scan/employee/late-count/{employee_id}` - Get late count

#### Site API (`backend/api/site_api.py`)

**Pydantic Models:**
- `CreateSiteRequest`: site_name, address
- `CreateEmployeeRequest`: name, hourly_rate, department_id

**Endpoints:**
- `GET /site/list` - Get all sites
- `POST /site/create-site` - Create site (admin-only)
- `GET /site/employees` - Get all employees
- `GET /site/employees/{employee_id}/status` - Get employee status
- `GET /site/employees/{employee_id}/logs` - Get employee logs
- `GET /site/departments` - Get all departments
- `POST /site/employees/create` - Create employee (admin-only)
- `GET /site/employees/{employee_id}/salary` - Calculate salary (admin-only)
- `GET /site/employees/{employee_id}/salary/export` - Export salary report (admin-only)
- `GET /site/active-employees-count` - Get active employees count
- `GET /site/employees/signed-in` - Get signed-in employees

#### Logs API (`backend/api/logs_api.py`)

**Endpoints:**
- `GET /logs/access` - Get access logs with filters
- `GET /logs/export` - Export access logs to Excel

#### Reports API (`backend/api/reports_api.py`)

**Endpoints:**
- `GET /reports/export` - Export reports (legacy endpoint)

#### Alert API (`backend/api/alert_api.py`)

**Pydantic Models:**
- `FlagVisitorRequest`: visitor_id, reason

**Endpoints:**
- `POST /alert/flag` - Flag visitor
- `GET /alert/flagged-visitors` - Get flagged visitors

#### User Management API (`backend/api/user_management_api.py`)

**Pydantic Models:**
- `CreateUserRequest`: username, password, role_name
- `UserResponse`: user_id, username, role_name, created_at

**Endpoints:**
- `POST /users/create` - Create user (admin-only)
- `DELETE /users/{user_id}` - Delete user (admin-only)
- `GET /users/list` - Get all users (admin-only)

#### Attendance API (`backend/api/attendance_api.py`)

**Pydantic Models:**
- `ScanRequest`: qr_code

**Endpoints:**
- `POST /attendance/scan` - Scan attendance (auto-toggles status)

#### Email API (`backend/api/email_api.py`)

**Pydantic Models:**
- `SendQRRequest`: recipient_email, visitor_id, qr_code_data
- `AlertLateRequest`: employee_id, late_count, salary_estimate

**Endpoints:**
- `POST /email/send-qr` - Send QR email
- `POST /email/alert-late` - Send late alert email

### 4.1.3 Frontend Components

#### Pages (`frontend/src/pages/`)

**Login.jsx:**
- Login form
- JWT token storage
- Redirect to dashboard

**Dashboard.jsx:**
- Statistics cards
- Active visits display
- Alerts display

**VisitorEntry.jsx:**
- Visitor registration form
- Visit creation form
- QR code generation trigger

**CheckInOut.jsx:**
- QR scanner (camera)
- Manual QR entry
- Check-in/check-out buttons

**EmployeeQR.jsx:**
- Employee QR generation form
- QR code display
- Download button

**EmployeeAttendance.jsx:**
- Employee list
- Attendance logs display
- Status indicators

**EmployeeManagement.jsx:**
- Employee list
- Create employee form
- Department selection

**SalaryCalculation.jsx:**
- Employee selection
- Date range picker
- Salary calculation results
- Excel export button

**VisitLogs.jsx:**
- Access logs table
- Date range filters
- Action type filters
- Excel export button

**UserManagement.jsx:**
- User list
- Create user form
- Deactivate user button

**SiteManagement.jsx:**
- Site list
- Create site form

**AdminProfile.jsx:**
- Admin profile display
- User information

#### Components (`frontend/src/components/`)

**Layout.jsx:**
- Navigation menu
- Route outlet
- User info display
- Logout button

#### Contexts (`frontend/src/contexts/`)

**AuthContext.jsx:**
- Authentication state
- Login/logout functions
- Token management

**DataContext.jsx:**
- Sites data
- Employees data
- Refresh functions

#### Services (`frontend/src/services/`)

**api.js:**
- Axios instance
- Token interceptor
- Error handler
- Base URL configuration

---

## 4.2 Interface Design

### 4.2.1 API Endpoints

#### Authentication Endpoints

**POST `/auth/login`**
- **Method:** POST
- **Auth:** None (public)
- **Request Body:**
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Response:**
  ```json
  {
    "token": "jwt_token_string",
    "user_id": 1,
    "username": "admin",
    "role": "admin",
    "message": "Login successful"
  }
  ```
- **Status Codes:** 200, 401

**POST `/auth/register-user`**
- **Method:** POST
- **Auth:** JWT (Admin only)
- **Request Body:**
  ```json
  {
    "username": "string",
    "password": "string",
    "role_name": "admin" | "security"
  }
  ```
- **Response:**
  ```json
  {
    "message": "User {username} created successfully"
  }
  ```
- **Status Codes:** 200, 400, 403

**PATCH `/auth/deactivate-user/{user_id}`**
- **Method:** PATCH
- **Auth:** JWT (Admin only)
- **Path Parameters:** user_id (int)
- **Response:**
  ```json
  {
    "message": "User {user_id} deactivated successfully. All records preserved for audit."
  }
  ```
- **Status Codes:** 200, 400, 403

**GET `/auth/me`**
- **Method:** GET
- **Auth:** JWT
- **Response:**
  ```json
  {
    "user_id": 1,
    "username": "admin",
    "role_name": "admin",
    "created_at": "2024-01-01T00:00:00"
  }
  ```
- **Status Codes:** 200, 404, 401

#### Visitor Endpoints

**POST `/visitor/add-visitor`**
- **Method:** POST
- **Auth:** JWT
- **Request Body:**
  ```json
  {
    "full_name": "string",
    "cnic": "string (format: XXXXX-XXXXXXX-X)",
    "contact_number": "string (optional)"
  }
  ```
- **Response:**
  ```json
  {
    "visitor_id": 1
  }
  ```
- **Status Codes:** 200, 400, 401

**GET `/visitor/search-visitor`**
- **Method:** GET
- **Auth:** JWT
- **Query Parameters:** cnic (string, optional), visitor_id (int, optional)
- **Response:**
  ```json
  {
    "visitor_id": 1,
    "full_name": "John Doe",
    "cnic": "12345-1234567-1",
    "contact_number": "+1234567890"
  }
  ```
- **Status Codes:** 200, 400, 404, 401

**POST `/visitor/checkin`**
- **Method:** POST
- **Auth:** JWT
- **Request Body:**
  ```json
  {
    "qr_code": "string"
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "visit_id": 1,
    "visitor_name": "John Doe",
    "checkin_time": "2024-01-01T10:00:00"
  }
  ```
- **Status Codes:** 200, 400, 401

**POST `/visitor/checkout`**
- **Method:** POST
- **Auth:** JWT
- **Request Body:**
  ```json
  {
    "qr_code": "string"
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "visit_id": 1,
    "visitor_name": "John Doe",
    "checkout_time": "2024-01-01T18:00:00"
  }
  ```
- **Status Codes:** 200, 400, 401

#### Visit Endpoints

**POST `/visit/create-visit`**
- **Method:** POST
- **Auth:** JWT
- **Request Body:**
  ```json
  {
    "visitor_id": 1,
    "site_id": 1,
    "purpose_details": "string (optional)",
    "host_employee_id": 1 (optional)
  }
  ```
- **Response:**
  ```json
  {
    "visit_id": 1
  }
  ```
- **Status Codes:** 200, 400, 401

**PATCH `/visit/update-status/{visit_id}`**
- **Method:** PATCH
- **Auth:** JWT
- **Path Parameters:** visit_id (int)
- **Request Body:**
  ```json
  {
    "status": "pending" | "checked_in" | "checked_out" | "denied"
  }
  ```
- **Response:**
  ```json
  {
    "message": "Visit status updated successfully"
  }
  ```
- **Status Codes:** 200, 400, 401

**GET `/visit/active-visits`**
- **Method:** GET
- **Auth:** JWT
- **Response:**
  ```json
  [
    {
      "visit_id": 1,
      "visitor_id": 1,
      "visitor_name": "John Doe",
      "site_id": 1,
      "site_name": "Main Office",
      "status": "checked_in",
      "checkin_time": "2024-01-01T10:00:00"
    }
  ]
  ```
- **Status Codes:** 200, 401

#### QR Code Endpoints

**POST `/qr/generate-employee`**
- **Method:** POST
- **Auth:** JWT
- **Request Body:**
  ```json
  {
    "employee_id": 1
  }
  ```
- **Response:**
  ```json
  {
    "emp_qr_id": 1,
    "code_value": "EMP_1_...",
    "employee_id": 1,
    "employee_name": "John Doe",
    "message": "Employee QR code generated successfully"
  }
  ```
- **Status Codes:** 200, 400, 422, 401

**POST `/qr/generate-visitor`**
- **Method:** POST
- **Auth:** JWT
- **Request Body:**
  ```json
  {
    "visit_id": 1,
    "recipient_email": "visitor@example.com"
  }
  ```
- **Response:**
  ```json
  {
    "visitor_qr_id": 1,
    "code_value": "VIS_1_...",
    "visit_id": 1,
    "expiry_date": "2024-01-02T10:00:00",
    "message": "Visitor QR code generated and emailed successfully"
  }
  ```
- **Status Codes:** 200, 400, 422, 401

**GET `/qr/download/{visitor_qr_id}`**
- **Method:** GET
- **Auth:** None (public)
- **Path Parameters:** visitor_qr_id (int)
- **Response:** PNG image file
- **Status Codes:** 200, 404

#### Scan Endpoints

**POST `/scan/employee`**
- **Method:** POST
- **Auth:** JWT
- **Request Body:**
  ```json
  {
    "emp_qr_id": 1,
    "scan_status": "signin" | "signout"
  }
  ```
- **Response:**
  ```json
  {
    "emp_qr_id": 1,
    "employee_id": 1,
    "employee_name": "John Doe",
    "scan_status": "signin",
    "timestamp": "2024-01-01T09:00:00",
    "is_late": false
  }
  ```
- **Status Codes:** 200, 400, 422, 401

**POST `/scan/visitor`**
- **Method:** POST
- **Auth:** JWT
- **Request Body:**
  ```json
  {
    "visitor_qr_id": 1,
    "scan_status": "signin" | "signout"
  }
  ```
- **Response:**
  ```json
  {
    "visitor_qr_id": 1,
    "visit_id": 1,
    "visitor_name": "John Doe",
    "scan_status": "signin",
    "timestamp": "2024-01-01T10:00:00"
  }
  ```
- **Status Codes:** 200, 400, 422, 401

**POST `/scan/verify`**
- **Method:** POST
- **Auth:** JWT
- **Request Body:**
  ```json
  {
    "qr_code": "string"
  }
  ```
- **Response:**
  ```json
  {
    "type": "employee" | "visitor",
    "id": 1,
    "valid": true,
    "message": "QR code verified"
  }
  ```
- **Status Codes:** 200, 400, 401

**GET `/scan/alerts`**
- **Method:** GET
- **Auth:** JWT
- **Response:**
  ```json
  [
    {
      "alert_id": 1,
      "description": "Invalid QR code scanned",
      "created_at": "2024-01-01T10:00:00"
    }
  ]
  ```
- **Status Codes:** 200, 401

**GET `/scan/employee/late-count/{employee_id}`**
- **Method:** GET
- **Auth:** JWT
- **Path Parameters:** employee_id (int)
- **Response:**
  ```json
  {
    "employee_id": 1,
    "late_count": 3,
    "period_days": 30
  }
  ```
- **Status Codes:** 200, 404, 401

#### Site/Employee/Salary Endpoints

**GET `/site/list`**
- **Method:** GET
- **Auth:** JWT
- **Response:**
  ```json
  {
    "sites": [
      {
        "site_id": 1,
        "site_name": "Main Office",
        "address": "123 Main St"
      }
    ]
  }
  ```
- **Status Codes:** 200, 401

**POST `/site/create-site`**
- **Method:** POST
- **Auth:** JWT (Admin only)
- **Request Body:**
  ```json
  {
    "site_name": "string",
    "address": "string (optional)"
  }
  ```
- **Response:**
  ```json
  {
    "message": "Site created successfully",
    "site_id": 1
  }
  ```
- **Status Codes:** 200, 400, 403, 401

**GET `/site/employees`**
- **Method:** GET
- **Auth:** JWT
- **Response:**
  ```json
  {
    "employees": [
      {
        "employee_id": 1,
        "name": "John Doe",
        "hourly_rate": 25.00,
        "department_id": 1,
        "department_name": "IT"
      }
    ]
  }
  ```
- **Status Codes:** 200, 401

**POST `/site/employees/create`**
- **Method:** POST
- **Auth:** JWT (Admin only)
- **Request Body:**
  ```json
  {
    "name": "string",
    "hourly_rate": 25.00,
    "department_id": 1
  }
  ```
- **Response:**
  ```json
  {
    "message": "Employee {name} created successfully",
    "employee_id": 1
  }
  ```
- **Status Codes:** 200, 400, 403, 401

**GET `/site/employees/{employee_id}/salary`**
- **Method:** GET
- **Auth:** JWT (Admin only)
- **Path Parameters:** employee_id (int)
- **Query Parameters:** start_date (string, optional), end_date (string, optional)
- **Response:**
  ```json
  {
    "employee_id": 1,
    "employee_name": "John Doe",
    "department": "IT",
    "hourly_rate": 25.00,
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "total_days_worked": 20,
    "total_hours": 160.00,
    "salary": 4000.00,
    "daily_breakdown": [
      {
        "date": "2024-01-01",
        "signin": "2024-01-01 09:00:00",
        "signout": "2024-01-01 17:00:00",
        "hours": 8.00
      }
    ]
  }
  ```
- **Status Codes:** 200, 404, 403, 401

**GET `/site/employees/{employee_id}/salary/export`**
- **Method:** GET
- **Auth:** JWT (Admin only)
- **Path Parameters:** employee_id (int)
- **Query Parameters:** start_date (string, optional), end_date (string, optional)
- **Response:** Excel file (.xlsx)
- **Status Codes:** 200, 404, 422, 403, 401

**GET `/site/departments`**
- **Method:** GET
- **Auth:** JWT
- **Response:**
  ```json
  {
    "departments": [
      {
        "department_id": 1,
        "name": "IT"
      }
    ]
  }
  ```
- **Status Codes:** 200, 401

**GET `/site/employees/{employee_id}/status`**
- **Method:** GET
- **Auth:** JWT
- **Path Parameters:** employee_id (int)
- **Response:**
  ```json
  {
    "employee_id": 1,
    "status": "signed_in" | "signed_out",
    "last_scan": "2024-01-01T09:00:00"
  }
  ```
- **Status Codes:** 200, 404, 401

**GET `/site/employees/{employee_id}/logs`**
- **Method:** GET
- **Auth:** JWT
- **Path Parameters:** employee_id (int)
- **Query Parameters:** days (int, default=30)
- **Response:**
  ```json
  {
    "logs": [
      {
        "scan_id": 1,
        "scan_status": "signin",
        "timestamp": "2024-01-01T09:00:00"
      }
    ]
  }
  ```
- **Status Codes:** 200, 404, 401

#### Logs Endpoints

**GET `/logs/access`**
- **Method:** GET
- **Auth:** JWT
- **Query Parameters:** start_date (string, optional), end_date (string, optional), action (string, optional)
- **Response:**
  ```json
  {
    "logs": [
      {
        "log_id": 1,
        "user_id": 1,
        "username": "admin",
        "action": "login",
        "details": "User admin logged in",
        "timestamp": "2024-01-01T10:00:00"
      }
    ],
    "count": 100,
    "filters": {
      "start_date": "2024-01-01",
      "end_date": "2024-01-31",
      "action": "login"
    }
  }
  ```
- **Status Codes:** 200, 422, 401

**GET `/logs/export`**
- **Method:** GET
- **Auth:** JWT
- **Query Parameters:** start_date (string, optional), end_date (string, optional), action (string, optional)
- **Response:** Excel file (.xlsx)
- **Status Codes:** 200, 422, 401

#### Alert Endpoints

**POST `/alert/flag`**
- **Method:** POST
- **Auth:** JWT
- **Request Body:**
  ```json
  {
    "visitor_id": 1,
    "reason": "string"
  }
  ```
- **Response:**
  ```json
  {
    "alert_id": 1,
    "message": "Visitor flagged successfully"
  }
  ```
- **Status Codes:** 200, 400, 401

**GET `/alert/flagged-visitors`**
- **Method:** GET
- **Auth:** JWT
- **Response:**
  ```json
  [
    {
      "alert_id": 1,
      "visitor_id": 1,
      "visitor_name": "John Doe",
      "reason": "Suspicious behavior",
      "created_at": "2024-01-01T10:00:00"
    }
  ]
  ```
- **Status Codes:** 200, 401

#### Attendance Endpoints

**POST `/attendance/scan`**
- **Method:** POST
- **Auth:** JWT
- **Request Body:**
  ```json
  {
    "qr_code": "string"
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "employee_id": 1,
    "employee_name": "John Doe",
    "status": "signed_in",
    "timestamp": "2024-01-01T09:00:00"
  }
  ```
- **Status Codes:** 200, 400, 401

#### User Management Endpoints

**POST `/users/create`**
- **Method:** POST
- **Auth:** JWT (Admin only)
- **Request Body:**
  ```json
  {
    "username": "string",
    "password": "string",
    "role_name": "admin" | "security"
  }
  ```
- **Response:**
  ```json
  {
    "message": "User created successfully",
    "user_id": 1
  }
  ```
- **Status Codes:** 200, 400, 403, 401

**DELETE `/users/{user_id}`**
- **Method:** DELETE
- **Auth:** JWT (Admin only)
- **Path Parameters:** user_id (int)
- **Response:**
  ```json
  {
    "message": "User deleted successfully"
  }
  ```
- **Status Codes:** 200, 400, 403, 401

**GET `/users/list`**
- **Method:** GET
- **Auth:** JWT (Admin only)
- **Response:**
  ```json
  {
    "users": [
      {
        "user_id": 1,
        "username": "admin",
        "role_name": "admin",
        "created_at": "2024-01-01T00:00:00"
      }
    ]
  }
  ```
- **Status Codes:** 200, 403, 401

---

## 4.3 Data Design

### 4.3.1 Database Schema

The system uses MySQL 8.0+ with 13 core tables:

1. **Departments** - Organizational departments
2. **Employees** - Employee records
3. **Roles** - User roles (admin, security)
4. **Users** - System user accounts
5. **AccessLogs** - Audit trail
6. **Sites** - Physical locations
7. **Visitors** - Visitor information
8. **Visits** - Visit records
9. **EmployeeQRCodes** - Employee QR codes
10. **VisitorQRCodes** - Visitor QR codes
11. **Alerts** - Security alerts
12. **EmployeeScanLogs** - Employee attendance logs
13. **VisitorScanLogs** - Visitor scan logs

[ERD Placeholder: Entity Relationship Diagram showing all 13 tables with relationships]

### 4.3.2 Table Details

See `docs/DATA_DICTIONARY.md` for complete table definitions, field types, constraints, and relationships.

### 4.3.3 Data Relationships

- **Departments** → **Employees** (One-to-Many)
- **Roles** → **Users** (One-to-Many)
- **Users** → **AccessLogs** (One-to-Many)
- **Visitors** → **Visits** (One-to-Many)
- **Sites** → **Visits** (One-to-Many)
- **Employees** → **Visits** (One-to-Many, as host_employee_id)
- **Employees** → **EmployeeQRCodes** (One-to-Many)
- **Visits** → **VisitorQRCodes** (One-to-Many)
- **EmployeeQRCodes** → **EmployeeScanLogs** (One-to-Many)
- **VisitorQRCodes** → **VisitorScanLogs** (One-to-Many)
- **VisitorQRCodes** → **Alerts** (One-to-Many)

---

## 4.4 Behavior Modeling

### 4.4.1 Sequence Diagrams

[Sequence Diagram Placeholder: Login Flow]
[Sequence Diagram Placeholder: Visitor Registration and QR Generation Flow]
[Sequence Diagram Placeholder: QR Scanning and Check-In Flow]
[Sequence Diagram Placeholder: Employee Attendance Scanning Flow]
[Sequence Diagram Placeholder: Salary Calculation Flow]

### 4.4.2 State Diagrams

[State Diagram Placeholder: Visit Status State Machine]
[State Diagram Placeholder: QR Code Status State Machine]
[State Diagram Placeholder: Employee Attendance State Machine]

---

## 4.5 Algorithm Design

### 4.5.1 QR Code Generation Algorithm

**Location:** `backend/services/qr_service.py::_generate_qr_code_image()`

**Pseudocode:**
```
FUNCTION generate_qr_code_image(data: string, filepath: string) -> boolean:
    TRY:
        CREATE QRCode object with:
            version = 1
            error_correction = ERROR_CORRECT_L
            box_size = 10
            border = 4
        
        ADD data to QR code
        MAKE QR code fit data
        
        CREATE image from QR code:
            fill_color = "black"
            back_color = "white"
        
        SAVE image to filepath
        RETURN True
    EXCEPT:
        RETURN False
END FUNCTION
```

### 4.5.2 Camera Scanning Process

**Location:** `frontend/src/pages/CheckInOut.jsx`

**Pseudocode:**
```
FUNCTION startCamera():
    REQUEST camera permission via getUserMedia()
    IF permission granted:
        INITIALIZE Html5QrcodeScanner with:
            camera_id = selected camera
            config = { fps: 10, qrbox: { width: 250, height: 250 } }
        
        START scanner
        ON scan success:
            CALL handleQRScan(qr_code)
    ELSE:
        SHOW error: "Camera permission denied"
END FUNCTION

FUNCTION handleQRScan(qr_code: string):
    CALL API /scan/verify with qr_code
    IF type == "employee":
        CALL API /scan/employee with emp_qr_id and scan_status
    ELSE IF type == "visitor":
        CALL API /visitor/checkin or /visitor/checkout with qr_code
    SHOW success/error toast
END FUNCTION
```

### 4.5.3 Salary Calculation Algorithm

**Location:** `backend/services/site_service.py::calculate_employee_salary()`

**Pseudocode:**
```
FUNCTION calculate_employee_salary(employee_id: int, start_date: string, end_date: string) -> dict:
    GET employee info from Employees table
    IF employee not found:
        RETURN None
    
    SET hourly_rate = employee.hourly_rate
    SET default dates if not provided:
        end_date = today
        start_date = 30 days ago
    
    PARSE dates to datetime objects
    SET end_date = end of day (23:59:59)
    
    GET all scans from EmployeeScanLogs in date range
    ORDER BY timestamp ASC
    
    INITIALIZE:
        total_hours = 0.0
        signin_time = None
        days_worked = empty set
        daily_hours = empty list
    
    FOR EACH scan in scans:
        scan_time = scan.timestamp
        scan_date = scan_time.date
        
        IF scan.scan_status == "signin":
            signin_time = scan_time
            ADD scan_date to days_worked
        ELSE IF scan.scan_status == "signout" AND signin_time is not None:
            checkout_time = scan_time
            hours = (checkout_time - signin_time).total_seconds() / 3600.0
            hours = MAX(0, hours)
            total_hours += hours
            
            ADD to daily_hours:
                date = scan_date
                signin = signin_time
                signout = checkout_time
                hours = hours
            
            signin_time = None
    
    IF signin_time is not None (incomplete day):
        end_of_day = signin_time.replace(hour=23, minute=59, second=59)
        hours = (end_of_day - signin_time).total_seconds() / 3600.0
        hours = MAX(0, hours)
        total_hours += hours
        
        ADD to daily_hours:
            date = signin_time.date
            signin = signin_time
            signout = end_of_day
            hours = hours
            incomplete = True
    
    salary = total_hours × hourly_rate
    
    RETURN {
        employee_id: employee_id,
        employee_name: employee.name,
        department: employee.department_name,
        hourly_rate: hourly_rate,
        start_date: start_date,
        end_date: end_date,
        total_days_worked: COUNT(days_worked),
        total_hours: ROUND(total_hours, 2),
        salary: ROUND(salary, 2),
        daily_breakdown: daily_hours
    }
END FUNCTION
```

### 4.5.4 Attendance Logging Algorithm

**Location:** `backend/services/scan_service.py::scan_employee_qr()`

**Pseudocode:**
```
FUNCTION scan_employee_qr(emp_qr_id: int, scan_status: string, scanned_by_user_id: int) -> dict:
    GET employee QR code from EmployeeQRCodes
    IF QR not found OR status != "active":
        RETURN None
    
    GET employee info from Employees
    GET current status (signed_in or signed_out)
    
    current_time = NOW()
    
    IF scan_status == "signin":
        IF current status == "signed_in":
            RETURN None (already signed in)
        
        is_late = check_if_late(current_time)
        
        INSERT INTO EmployeeScanLogs:
            emp_qr_id = emp_qr_id
            scan_status = "signin"
            timestamp = current_time
        
        IF is_late:
            late_count = get_late_count_last_30_days(employee_id)
            IF late_count >= 3:
                send_late_alert_email(employee_id, late_count)
        
        RETURN {
            emp_qr_id: emp_qr_id,
            employee_id: employee_id,
            employee_name: employee.name,
            scan_status: "signin",
            timestamp: current_time,
            is_late: is_late
        }
    
    ELSE IF scan_status == "signout":
        IF current status == "signed_out":
            RETURN None (already signed out)
        
        INSERT INTO EmployeeScanLogs:
            emp_qr_id = emp_qr_id
            scan_status = "signout"
            timestamp = current_time
        
        RETURN {
            emp_qr_id: emp_qr_id,
            employee_id: employee_id,
            employee_name: employee.name,
            scan_status: "signout",
            timestamp: current_time
        }
    
    RETURN None
END FUNCTION

FUNCTION check_if_late(scan_time: datetime) -> boolean:
    scan_time_only = scan_time.time()
    late_threshold = TIME(9, 10, 0)  // 9:10 AM
    RETURN scan_time_only > late_threshold
END FUNCTION
```

### 4.5.5 Late Arrival Computation

**Location:** `backend/services/scan_service.py::_get_late_count_last_30_days()`

**Pseudocode:**
```
FUNCTION get_late_count_last_30_days(employee_id: int) -> int:
    thirty_days_ago = NOW() - 30 days
    
    GET all signin scans from EmployeeScanLogs:
        WHERE employee_id = employee_id
        AND scan_status = "signin"
        AND timestamp >= thirty_days_ago
    ORDER BY timestamp
    
    late_count = 0
    
    FOR EACH scan in scans:
        IF check_if_late(scan.timestamp):
            late_count += 1
    
    RETURN late_count
END FUNCTION
```

### 4.5.6 Login JWT Flow

**Location:** `backend/services/auth_service.py::login()`

**Pseudocode:**
```
FUNCTION login(username: string, password: string) -> dict:
    GET user from Users table WHERE username = username
    IF user not found:
        RETURN None
    
    hash_input_password = SHA256(password)
    IF hash_input_password != user.password_hash:
        RETURN None
    
    GET role from Roles table WHERE role_id = user.role_id
    
    token = generate_jwt_token({
        user_id: user.user_id,
        username: user.username,
        role: role.role_name
    })
    
    LOG action: "login"
    
    RETURN {
        token: token,
        user_id: user.user_id,
        username: user.username,
        role: role.role_name
    }
END FUNCTION

FUNCTION generate_jwt_token(payload: dict) -> string:
    SET expiration = NOW() + 24 hours
    
    token = JWT.encode({
        user_id: payload.user_id,
        username: payload.username,
        role: payload.role,
        exp: expiration
    }, SECRET_KEY, algorithm="HS256")
    
    RETURN token
END FUNCTION
```

---

**End of Document 4: Detailed Design**

