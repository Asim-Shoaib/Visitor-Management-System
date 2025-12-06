# API Reference Documentation

## Base URL
```
http://localhost:8000
```

## Authentication

All protected endpoints require JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

The JWT token is obtained from the `/auth/login` endpoint and is valid for 24 hours.

---

## Endpoints

### Authentication Endpoints (`/auth`)

#### POST `/auth/login`
**Public endpoint** - No authentication required.

Login and receive JWT token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "token": "jwt_token_string",
  "user_id": 1,
  "username": "admin",
  "role": "admin",
  "message": "Login successful"
}
```

**Status Codes:**
- `200`: Login successful
- `401`: Invalid username or password

---

#### POST `/auth/register-user`
**Admin only** - Requires JWT authentication.

Register a new user account.

**Request Body:**
```json
{
  "username": "string",
  "password": "string",
  "role_name": "admin" | "security"
}
```

**Response:**
```json
{
  "message": "User {username} created successfully"
}
```

**Status Codes:**
- `200`: User created successfully
- `400`: Unable to register user (duplicate or invalid data)
- `403`: Admin role required

---

#### PATCH `/auth/deactivate-user/{user_id}`
**Admin only** - Requires JWT authentication.

Deactivate a user account (preserves audit trail).

**Path Parameters:**
- `user_id` (int): User ID to deactivate

**Response:**
```json
{
  "message": "User {user_id} deactivated successfully. All records preserved for audit."
}
```

**Status Codes:**
- `200`: User deactivated successfully
- `400`: Unable to deactivate user (user not found or self-deactivation attempted)
- `403`: Admin role required

---

### Visitor Endpoints (`/visitor`)

#### POST `/visitor/add-visitor`
**Requires JWT authentication.**

Add a new visitor to the system.

**Request Body:**
```json
{
  "full_name": "string",
  "cnic": "string (format: XXXXX-XXXXXXX-X)",
  "contact_number": "string (optional)"
}
```

**Response:**
```json
{
  "visitor_id": 1
}
```

**Status Codes:**
- `200`: Visitor added successfully
- `400`: Unable to add visitor (validation failed or CNIC already exists)
- `401`: Unauthorized

---

#### GET `/visitor/search-visitor`
**Requires JWT authentication.**

Search for a visitor by CNIC or visitor ID.

**Query Parameters:**
- `cnic` (string, optional): CNIC number
- `visitor_id` (int, optional): Visitor ID

**Response:**
```json
{
  "visitor_id": 1,
  "full_name": "John Doe",
  "cnic": "12345-1234567-1",
  "contact_number": "+1234567890"
}
```

**Status Codes:**
- `200`: Visitor found
- `400`: Provide cnic or visitor_id
- `404`: Visitor not found
- `401`: Unauthorized

---

#### POST `/visitor/checkin`
**Requires JWT authentication.**

Check in a visitor using their QR code.

**Request Body:**
```json
{
  "qr_code": "string"
}
```

**Response:**
```json
{
  "success": true,
  "visit_id": 1,
  "visitor_name": "John Doe",
  "checkin_time": "2024-01-01T10:00:00"
}
```

**Status Codes:**
- `200`: Check-in successful
- `400`: Unable to check in visitor (QR code not found or invalid)
- `401`: Unauthorized

---

#### POST `/visitor/checkout`
**Requires JWT authentication.**

Check out a visitor using their QR code.

**Request Body:**
```json
{
  "qr_code": "string"
}
```

**Response:**
```json
{
  "success": true,
  "visit_id": 1,
  "visitor_name": "John Doe",
  "checkout_time": "2024-01-01T18:00:00"
}
```

**Status Codes:**
- `200`: Check-out successful
- `400`: Unable to check out visitor (QR code not found or invalid)
- `401`: Unauthorized

---

### Visit Endpoints (`/visit`)

#### POST `/visit/create-visit`
**Requires JWT authentication.**

Create a new visit record.

**Request Body:**
```json
{
  "visitor_id": 1,
  "site_id": 1,
  "purpose_details": "string (optional)",
  "host_employee_id": 1 (optional)
}
```

**Response:**
```json
{
  "visit_id": 1
}
```

**Status Codes:**
- `200`: Visit created successfully
- `400`: Unable to create visit (visitor/site/employee not found or active visit exists)
- `401`: Unauthorized

---

#### PATCH `/visit/update-status/{visit_id}`
**Requires JWT authentication.**

Update visit status.

**Path Parameters:**
- `visit_id` (int): Visit ID

**Request Body:**
```json
{
  "status": "pending" | "checked_in" | "checked_out" | "denied"
}
```

**Response:**
```json
{
  "message": "Visit status updated successfully"
}
```

**Status Codes:**
- `200`: Status updated successfully
- `400`: Unable to update status (invalid status or transition)
- `401`: Unauthorized

---

#### GET `/visit/active-visits`
**Requires JWT authentication.**

Get all active visits.

**Response:**
```json
{
  "visits": [
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
}
```

**Status Codes:**
- `200`: Success
- `401`: Unauthorized

---

### QR Code Endpoints (`/qr`)

#### POST `/qr/generate-employee`
**Requires JWT authentication.**

Generate a permanent QR code for an employee.

**Request Body:**
```json
{
  "employee_id": 1
}
```

**Response:**
```json
{
  "emp_qr_id": 1,
  "code_value": "EMP_1_abc123",
  "employee_id": 1,
  "employee_name": "John Doe",
  "message": "Employee QR code generated successfully"
}
```

**Status Codes:**
- `200`: QR code generated successfully
- `400`: Unable to generate employee QR code (employee not found)
- `401`: Unauthorized
- `422`: Invalid employee_id format

---

#### POST `/qr/generate-visitor`
**Requires JWT authentication.**

Generate a temporary QR code for a visitor visit and email it.

**Request Body:**
```json
{
  "visit_id": 1,
  "recipient_email": "visitor@example.com"
}
```

**Response:**
```json
{
  "visitor_qr_id": 1,
  "code_value": "VIS_1_xyz789",
  "visit_id": 1,
  "visitor_name": "John Doe",
  "download_url": "http://localhost:8000/qr/download/1",
  "expiry_date": "2024-01-02T23:59:59",
  "email_sent": true,
  "message": "Visitor QR code generated successfully"
}
```

**Status Codes:**
- `200`: QR code generated successfully
- `400`: Unable to generate visitor QR code (visit not found or invalid status)
- `401`: Unauthorized
- `422`: Invalid visit_id or email format
- `500`: Internal error generating QR code

---

#### GET `/qr/download/{visitor_qr_id}`
**Public endpoint** - No authentication required.

Download a visitor QR code image.

**Path Parameters:**
- `visitor_qr_id` (int): Visitor QR code ID

**Response:**
- PNG image file

**Status Codes:**
- `200`: QR code image
- `404`: QR code not found, expired, or revoked
- `422`: Invalid visitor_qr_id format

---

#### GET `/qr/debug/visit/{visit_id}`
**Requires JWT authentication.**

Debug endpoint to check visit and visitor information.

**Path Parameters:**
- `visit_id` (int): Visit ID

**Response:**
```json
{
  "visit_id": 1,
  "visitor_id": 1,
  "visitor_name": "John Doe",
  "status": "pending"
}
```

**Status Codes:**
- `200`: Success
- `404`: Visit not found
- `401`: Unauthorized
- `422`: Invalid visit_id format
- `500`: Debug function error

---

### Scanning Endpoints (`/scan`)

#### POST `/scan/employee`
**Requires JWT authentication.**

Scan an employee QR code for attendance.

**Request Body:**
```json
{
  "emp_qr_id": 1,
  "scan_status": "signin" | "signout"
}
```

**Response:**
```json
{
  "success": true,
  "employee_id": 1,
  "employee_name": "John Doe",
  "scan_status": "signin",
  "timestamp": "2024-01-01T09:00:00",
  "is_late": false,
  "late_count": 0
}
```

**Status Codes:**
- `200`: Scan successful
- `400`: Unable to scan employee QR (QR not found, inactive, or invalid scan status)
- `401`: Unauthorized
- `422`: Invalid emp_qr_id or scan_status format

---

#### POST `/scan/visitor`
**Requires JWT authentication.**

Scan a visitor QR code.

**Request Body:**
```json
{
  "visitor_qr_id": 1,
  "scan_status": "signin" | "signout"
}
```

**Response:**
```json
{
  "success": true,
  "visit_id": 1,
  "visitor_name": "John Doe",
  "scan_status": "signin",
  "timestamp": "2024-01-01T10:00:00"
}
```

**Status Codes:**
- `200`: Scan successful
- `400`: Unable to scan visitor QR (QR not found, expired, revoked, or invalid scan status)
- `401`: Unauthorized
- `422`: Invalid visitor_qr_id or scan_status format

---

#### POST `/scan/verify`
**Requires JWT authentication.**

Verify a QR code and determine if it belongs to an employee or visitor.

**Request Body:**
```json
{
  "qr_code": "string"
}
```

**Response:**
```json
{
  "type": "employee" | "visitor",
  "status": "valid" | "expired" | "revoked" | "invalid",
  "linked_id": 1,
  "employee_id": 1 (if type is employee),
  "visitor_id": 1 (if type is visitor),
  "alert": true (if visitor has security flags),
  "flags": [...] (if alert is true)
}
```

**Status Codes:**
- `200`: Verification successful
- `400`: Unable to verify QR code
- `401`: Unauthorized

---

#### GET `/scan/alerts`
**Requires JWT authentication.**

Get all active alerts.

**Response:**
```json
{
  "alerts": [
    {
      "alert_id": 1,
      "description": "Invalid QR code scanned",
      "created_at": "2024-01-01T10:00:00",
      "visitor_name": "John Doe"
    }
  ],
  "count": 1
}
```

**Status Codes:**
- `200`: Success
- `401`: Unauthorized

---

#### GET `/scan/employee/late-count/{employee_id}`
**Requires JWT authentication.**

Get late arrival count for an employee in the last 30 days.

**Path Parameters:**
- `employee_id` (int): Employee ID

**Response:**
```json
{
  "employee_id": 1,
  "employee_name": "John Doe",
  "late_count": 3,
  "salary_estimate": 1250.50
}
```

**Status Codes:**
- `200`: Success
- `404`: Employee not found
- `401`: Unauthorized
- `422`: Invalid employee_id format

---

### Attendance Endpoints (`/attendance`)

#### POST `/attendance/scan`
**Requires JWT authentication.**

Scan employee QR code for attendance (check-in/check-out). Automatically toggles status.

**Request Body:**
```json
{
  "qr_code": "string"
}
```

**Response:**
```json
{
  "status": "checked_in" | "checked_out",
  "time": "2024-01-01T09:00:00",
  "employee": {
    "id": 1,
    "name": "John Doe",
    "dept": "Unknown"
  }
}
```

**Status Codes:**
- `200`: Attendance scan successful
- `400`: Invalid QR code or failed to process attendance scan
- `401`: Unauthorized

---

### Site & Employee Endpoints (`/site`)

#### GET `/site/list`
**Requires JWT authentication.**

Get all sites.

**Response:**
```json
{
  "sites": [
    {
      "site_id": 1,
      "site_name": "Main Office",
      "address": "123 Main Street"
    }
  ]
}
```

**Status Codes:**
- `200`: Success
- `401`: Unauthorized

---

#### GET `/site/employees`
**Requires JWT authentication.**

Get all employees.

**Response:**
```json
{
  "employees": [
    {
      "employee_id": 1,
      "name": "John Doe",
      "hourly_rate": 25.00,
      "department_name": "IT Department"
    }
  ]
}
```

**Status Codes:**
- `200`: Success
- `401`: Unauthorized

---

#### GET `/site/active-employees-count`
**Requires JWT authentication.**

Get count of currently signed-in employees.

**Response:**
```json
{
  "active_employees_count": 5
}
```

**Status Codes:**
- `200`: Success
- `401`: Unauthorized

---

#### GET `/site/employees/signed-in`
**Requires JWT authentication.**

Get list of currently signed-in employees.

**Response:**
```json
{
  "employees": [
    {
      "employee_id": 1,
      "name": "John Doe",
      "hourly_rate": 25.00,
      "department_name": "IT Department",
      "last_scan_time": "2024-01-01T09:00:00"
    }
  ]
}
```

**Status Codes:**
- `200`: Success
- `401`: Unauthorized

---

#### GET `/site/employees/{employee_id}/status`
**Requires JWT authentication.**

Get current status of an employee.

**Path Parameters:**
- `employee_id` (int): Employee ID

**Response:**
```json
{
  "employee_id": 1,
  "name": "John Doe",
  "department": "IT Department",
  "hourly_rate": 25.00,
  "is_signed_in": true,
  "last_scan_time": "2024-01-01T09:00:00",
  "last_scan_status": "signin"
}
```

**Status Codes:**
- `200`: Success
- `404`: Employee not found
- `401`: Unauthorized

---

#### GET `/site/employees/{employee_id}/logs`
**Requires JWT authentication.**

Get employee logs for last N days.

**Path Parameters:**
- `employee_id` (int): Employee ID

**Query Parameters:**
- `days` (int, optional, default=30, min=1, max=365): Number of days

**Response:**
```json
{
  "logs": [
    {
      "scan_id": 1,
      "scan_status": "signin",
      "timestamp": "2024-01-01T09:00:00",
      "qr_code_value": "EMP_1_abc123"
    }
  ],
  "count": 1,
  "days": 30
}
```

**Status Codes:**
- `200`: Success
- `401`: Unauthorized

---

#### GET `/site/departments`
**Requires JWT authentication.**

Get all departments.

**Response:**
```json
{
  "departments": [
    {
      "department_id": 1,
      "name": "IT Department"
    }
  ]
}
```

**Status Codes:**
- `200`: Success
- `401`: Unauthorized

---

#### POST `/site/employees/create`
**Admin only** - Requires JWT authentication.

Create a new employee.

**Request Body:**
```json
{
  "name": "John Doe",
  "hourly_rate": 25.00,
  "department_id": 1
}
```

**Response:**
```json
{
  "message": "Employee John Doe created successfully",
  "employee_id": 1
}
```

**Status Codes:**
- `200`: Employee created successfully
- `400`: Failed to create employee (validation failed or department not found)
- `403`: Admin role required
- `401`: Unauthorized

---

#### GET `/site/employees/{employee_id}/salary`
**Admin only** - Requires JWT authentication.

Calculate employee salary for a date range.

**Path Parameters:**
- `employee_id` (int): Employee ID

**Query Parameters:**
- `start_date` (string, optional, format: YYYY-MM-DD): Start date (defaults to 30 days ago)
- `end_date` (string, optional, format: YYYY-MM-DD): End date (defaults to today)

**Response:**
```json
{
  "employee_id": 1,
  "employee_name": "John Doe",
  "department": "IT Department",
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
      "hours": 8.00,
      "incomplete": false
    }
  ]
}
```

**Status Codes:**
- `200`: Success
- `404`: Employee not found or invalid date range
- `403`: Admin role required
- `401`: Unauthorized

---

#### GET `/site/employees/{employee_id}/salary/export`
**Admin only** - Requires JWT authentication.

Export employee salary report to Excel.

**Path Parameters:**
- `employee_id` (int): Employee ID

**Query Parameters:**
- `start_date` (string, optional, format: YYYY-MM-DD): Start date
- `end_date` (string, optional, format: YYYY-MM-DD): End date

**Response:**
- Excel file (.xlsx)

**Status Codes:**
- `200`: Excel file
- `404`: Employee not found or invalid date range
- `403`: Admin role required
- `401`: Unauthorized
- `422`: Invalid date format

---

### User Management Endpoints (`/users`)

#### POST `/users/create`
**Admin only** - Requires JWT authentication.

Create a new user account.

**Request Body:**
```json
{
  "username": "string",
  "password": "string",
  "role_name": "admin" | "security"
}
```

**Response:**
```json
{
  "message": "User {username} created successfully"
}
```

**Status Codes:**
- `200`: User created successfully
- `400`: Failed to create user (username may already exist)
- `403`: Only admins can create users
- `401`: Unauthorized

---

#### DELETE `/users/{user_id}`
**Admin only** - Requires JWT authentication.

Delete (deactivate) a user.

**Path Parameters:**
- `user_id` (int): User ID

**Response:**
```json
{
  "message": "User {user_id} deactivated successfully"
}
```

**Status Codes:**
- `200`: User deactivated successfully
- `400`: Failed to deactivate user or cannot delete own account
- `403`: Only admins can delete users
- `401`: Unauthorized

---

#### GET `/users/list`
**Admin only** - Requires JWT authentication.

Get list of all users.

**Response:**
```json
{
  "users": [
    {
      "user_id": 1,
      "username": "admin",
      "role_name": "admin",
      "created_at": "2024-01-01T00:00:00"
    }
  ],
  "count": 1
}
```

**Status Codes:**
- `200`: Success
- `403`: Only admins can view user list
- `401`: Unauthorized

---

### Logs Endpoints (`/logs`)

#### GET `/logs/access`
**Requires JWT authentication.**

Get access logs with optional filters.

**Query Parameters:**
- `start_date` (string, optional, format: YYYY-MM-DD): Start date filter
- `end_date` (string, optional, format: YYYY-MM-DD): End date filter
- `action` (string, optional): Action type filter

**Response:**
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
  "count": 1,
  "filters": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "action": "login"
  }
}
```

**Status Codes:**
- `200`: Success
- `401`: Unauthorized
- `422`: Invalid date format

---

#### GET `/logs/export`
**Requires JWT authentication.**

Export access logs to Excel format.

**Query Parameters:**
- `start_date` (string, optional, format: YYYY-MM-DD): Start date filter
- `end_date` (string, optional, format: YYYY-MM-DD): End date filter
- `action` (string, optional): Action type filter

**Response:**
- Excel file (.xlsx)

**Status Codes:**
- `200`: Excel file
- `401`: Unauthorized
- `422`: Invalid date format

---

### Reports Endpoints (`/reports`)

#### GET `/reports/export`
**Requires JWT authentication.**

Export access logs to Excel format (alternative endpoint).

**Query Parameters:**
- `from` (string, optional, format: YYYY-MM-DD): Start date (alias: from_date)
- `to` (string, optional, format: YYYY-MM-DD): End date (alias: to_date)

**Response:**
- Excel file (.xlsx)

**Status Codes:**
- `200`: Excel file
- `401`: Unauthorized
- `422`: Invalid date format

---

### Alerts Endpoints (`/alerts`)

#### POST `/alerts/flag`
**Requires JWT authentication.**

Flag a visitor for security reasons.

**Request Body:**
```json
{
  "visitor_id": 1,
  "reason": "string"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Visitor flagged successfully",
  "alert": {
    "alert_id": 1,
    "description": "string",
    "created_at": "2024-01-01T10:00:00"
  }
}
```

**Status Codes:**
- `200`: Visitor flagged successfully
- `400`: Failed to flag visitor (visitor not found or database error)
- `401`: Unauthorized

---

#### GET `/alerts/flagged-visitors`
**Requires JWT authentication.**

Get all currently flagged visitors.

**Response:**
```json
{
  "visitors": [
    {
      "visitor_id": 1,
      "full_name": "John Doe",
      "cnic": "12345-1234567-1",
      "alert_count": 1
    }
  ],
  "count": 1
}
```

**Status Codes:**
- `200`: Success
- `401`: Unauthorized

---

### Email Endpoints (`/email`)

#### POST `/email/send-qr`
**Requires JWT authentication.**

Send QR code as email attachment.

**Request Body:**
```json
{
  "email": "visitor@example.com",
  "visitor_id": 1,
  "qr_code_data": "string"
}
```

**Response:**
```json
{
  "success": true,
  "message": "QR code email sent successfully"
}
```

**Status Codes:**
- `200`: Email sent successfully
- `400`: Failed to send email
- `401`: Unauthorized

---

#### POST `/email/alert-late`
**Requires JWT authentication.**

Check for late arrivals and send alerts to admin.

**Request Body:**
```json
{
  "employee_id": 1 (optional)
}
```

**Response:**
```json
{
  "success": true,
  "message": "Late arrival alerts processed",
  "alerts_sent": 2
}
```

**Status Codes:**
- `200`: Alerts processed successfully
- `400`: Failed to process alerts
- `401`: Unauthorized

---

### Health Check

#### GET `/health`
**Public endpoint** - No authentication required.

Check API health status.

**Response:**
```json
{
  "status": "healthy"
}
```

**Status Codes:**
- `200`: API is healthy

---

## Error Responses

All endpoints may return the following error responses:

### 401 Unauthorized
```json
{
  "detail": "Authorization header required"
}
```

### 403 Forbidden
```json
{
  "detail": "Admin role required"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": "Invalid input format"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

Currently, there are no rate limits implemented. Consider implementing rate limiting for production deployments.

---

## Notes

- All timestamps are in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)
- Date parameters should be in YYYY-MM-DD format
- JWT tokens expire after 24 hours
- Password hashing uses SHA256
- CNIC format validation: `^[0-9]{5}-[0-9]{7}-[0-9]$`
- Employee QR codes are permanent (no expiry)
- Visitor QR codes have expiry dates (typically 24 hours from generation)

