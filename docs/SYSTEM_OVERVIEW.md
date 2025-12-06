# Visitor Management System - System Overview

## Introduction

The Visitor Management System (VMS) is a comprehensive solution for managing visitors, tracking employee attendance, and maintaining security through QR code-based access control. The system provides role-based access control with separate interfaces for administrators and security personnel.

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.8+)
- **Database**: MySQL 8.0+
- **Authentication**: JWT (JSON Web Tokens)
- **Password Hashing**: SHA256
- **QR Code Generation**: qrcode library (Python)
- **Excel Export**: openpyxl
- **Email**: SMTP (configurable)

### Frontend
- **Framework**: React 18.2+
- **Build Tool**: Vite 5.0+
- **Routing**: React Router 6.20+
- **HTTP Client**: Axios
- **Notifications**: React Toastify
- **QR Code Display**: qrcode.react
- **QR Scanner**: html5-qrcode

## System Architecture

### High-Level Architecture

```
┌─────────────────┐
│   React Frontend │
│   (Port 3000)    │
└────────┬─────────┘
         │
         │ HTTP/REST API
         │
┌────────▼─────────┐
│  FastAPI Backend │
│   (Port 8000)    │
└────────┬─────────┘
         │
         │ SQL Queries
         │
┌────────▼─────────┐
│   MySQL Database │
│  (Port 3306)     │
└──────────────────┘
```

### Component Architecture

**Backend Structure:**
```
backend/
├── api/              # API route handlers
├── services/         # Business logic
├── utils/            # Utility functions
├── database/         # Database connection & schema
└── config/           # Configuration files
```

**Frontend Structure:**
```
frontend/
├── src/
│   ├── pages/        # Page components
│   ├── components/   # Reusable components
│   ├── contexts/     # React Context providers
│   └── services/     # API service layer
```

## Core Features

### 1. Authentication & Authorization

**Login Flow:**
1. User submits username and password
2. Backend validates credentials against Users table
3. If valid, generates JWT token (24-hour expiration)
4. Token stored in localStorage and sent with all subsequent requests

**Role-Based Access:**
- **Admin**: Full system access including user management, employee management, salary calculation
- **Security**: Access to visitor management, scanning, and attendance tracking

**Token Management:**
- JWT tokens include user_id, username, and role
- Tokens validated on every protected endpoint
- Automatic logout on token expiration (401 response)

### 2. Visitor Management

**Visitor Registration:**
- CNIC validation (format: XXXXX-XXXXXXX-X)
- Unique CNIC enforcement
- Contact number optional

**Visit Creation:**
- Link visitor to a site
- Optional host employee assignment
- Purpose details tracking
- Status workflow: pending → checked_in → checked_out

**QR Code Generation:**
- Temporary QR codes for visitors (24-hour expiry)
- QR codes emailed to visitors automatically
- Downloadable QR code images

### 3. Employee Management

**Employee Records:**
- Name, hourly rate, department assignment
- Department-based organization
- Employee creation (admin only)

**QR Code Generation:**
- Permanent QR codes for employees
- No expiry date
- Status tracking (active, expired, revoked)

**Attendance Tracking:**
- Sign-in/sign-out via QR code scanning
- Automatic status toggling
- Late arrival detection (after 9:10 AM)
- Late arrival alerts (3+ times in 30 days)

### 4. Salary Calculation

**Calculation Method:**
- Based on sign-in/sign-out timestamps
- Total hours = sum of (signout_time - signin_time) for each day
- Salary = total_hours × hourly_rate
- Handles incomplete days (no sign-out) by counting until end of day

**Features:**
- Date range selection
- Daily breakdown display
- Excel export functionality
- Admin-only access

### 5. QR Code Scanning

**Employee Scanning:**
- Automatic sign-in/sign-out detection
- Late arrival tracking
- Email alerts for frequent late arrivals

**Visitor Scanning:**
- Visit status updates
- Alert generation for invalid/expired QR codes
- Security flag checking

**QR Code Verification:**
- Determines if QR belongs to employee or visitor
- Validates QR code status (valid, expired, revoked)
- Returns linked entity information

### 6. Alert System

**Alert Types:**
- Invalid QR code scans
- Expired QR code scans
- Revoked QR code scans
- Visitor security flags
- Employee late arrival alerts

**Alert Management:**
- Real-time alert display
- Visitor flagging capability
- Flagged visitor tracking

### 7. Logging & Reporting

**Access Logs:**
- All system actions logged
- User, action, details, timestamp
- Filterable by date range and action type
- Excel export functionality

**Reports:**
- Access log exports
- Salary report exports
- Date range filtering

## Data Flow

### Visitor Check-In Flow

```
1. Visitor Registration
   └─> POST /visitor/add-visitor
       └─> Creates Visitor record

2. Visit Creation
   └─> POST /visit/create-visit
       └─> Creates Visit record (status: pending)

3. QR Code Generation
   └─> POST /qr/generate-visitor
       └─> Creates VisitorQRCode
       └─> Emails QR code to visitor

4. Visitor Arrival
   └─> POST /visitor/checkin
       └─> Updates Visit status to 'checked_in'
       └─> Sets checkin_time

5. Visitor Departure
   └─> POST /visitor/checkout
       └─> Updates Visit status to 'checked_out'
       └─> Sets checkout_time
```

### Employee Attendance Flow

```
1. Employee QR Generation
   └─> POST /qr/generate-employee
       └─> Creates EmployeeQRCode (permanent)

2. Employee Sign-In
   └─> POST /attendance/scan (or /scan/employee)
       └─> Creates EmployeeScanLog (signin)
       └─> Checks for late arrival
       └─> Updates late count if applicable

3. Employee Sign-Out
   └─> POST /attendance/scan (or /scan/employee)
       └─> Creates EmployeeScanLog (signout)
       └─> Calculates hours worked
```

### Salary Calculation Flow

```
1. Admin Selects Employee & Date Range
   └─> GET /site/employees/{id}/salary

2. Backend Retrieves Scan Logs
   └─> Queries EmployeeScanLogs for date range
   └─> Pairs signin/signout records
   └─> Calculates hours per day

3. Salary Calculation
   └─> Total hours = sum of daily hours
   └─> Salary = total_hours × hourly_rate

4. Excel Export (Optional)
   └─> GET /site/employees/{id}/salary/export
       └─> Generates Excel file with breakdown
```

## Database Schema

### Key Tables

**Users & Roles:**
- `Roles`: System roles (admin, security)
- `Users`: User accounts with authentication

**Employees:**
- `Departments`: Department organization
- `Employees`: Employee records with hourly rates
- `EmployeeQRCodes`: Permanent employee QR codes
- `EmployeeScanLogs`: Attendance tracking

**Visitors:**
- `Visitors`: Visitor registration
- `Sites`: Physical locations
- `Visits`: Visit records
- `VisitorQRCodes`: Temporary visitor QR codes
- `VisitorScanLogs`: Visitor entry/exit tracking

**System:**
- `AccessLogs`: Audit trail
- `Alerts`: Security alerts

See `backend/database/schema.sql` for complete schema definition.

## Security Features

1. **Password Security:**
   - SHA256 hashing
   - Password validation (minimum requirements)

2. **Authentication:**
   - JWT token-based
   - Token expiration (24 hours)
   - Automatic token validation

3. **Authorization:**
   - Role-based access control
   - Endpoint-level permission checks
   - Admin-only operations protected

4. **Data Validation:**
   - Input validation on all endpoints
   - CNIC format validation
   - Email format validation
   - SQL injection prevention (parameterized queries)

5. **Audit Trail:**
   - All actions logged in AccessLogs
   - User tracking for all operations
   - Timestamp recording

## Frontend Architecture

### Context Providers

**AuthContext:**
- Manages user authentication state
- Handles login/logout
- Token management
- User information storage

**DataContext:**
- Caches sites and employees data
- Auto-refresh every 5 minutes
- Provides refreshData() for manual updates

### Navigation Structure

**Public Routes:**
- `/login` - Login page

**Protected Routes (All Users):**
- `/` - Dashboard
- `/employee-qr` - Generate employee QR codes
- `/visitor-entry` - Visitor registration and visit creation
- `/checkin-out` - QR code scanning
- `/employee-attendance` - Employee attendance view
- `/logs` - Access logs

**Admin-Only Routes:**
- `/users` - User management
- `/employees` - Employee management
- `/salary` - Salary calculation

### Component Structure

All pages follow a consistent structure:
- Loading states
- Error handling with toast notifications
- Form validation
- API integration via `api.js` service

## Caching Strategy

**Frontend Caching:**
- Sites and employees cached in DataContext
- Auto-refresh every 5 minutes
- Manual refresh via `refreshData()` function
- Used by EmployeeManagement and SalaryCalculation pages

**Backend:**
- No caching implemented
- Direct database queries
- Consider Redis for production scaling

## Excel Export Mechanism

**Implementation:**
- Uses `openpyxl` library
- Generates formatted Excel files
- Includes headers, styling, and auto-width columns
- Returns as BytesIO stream

**Export Features:**
- Access logs export
- Salary report export
- Date range filtering
- Formatted headers and data

## Email System

**Configuration:**
- SMTP settings in `config/config.ini`
- Configurable sender email and credentials

**Email Features:**
- Visitor QR code delivery
- Late arrival alerts
- Error handling for email failures

## Error Handling

**Backend:**
- Consistent HTTPException responses
- Detailed error messages
- Status code standardization
- Database error handling

**Frontend:**
- Toast notifications for errors
- Console error logging (development)
- Graceful error handling
- User-friendly error messages

## Performance Considerations

1. **Database:**
   - Indexed foreign keys
   - Efficient queries with JOINs
   - Parameterized queries for security

2. **Frontend:**
   - Context-based caching
   - Parallel API calls where possible
   - Lazy loading potential (future enhancement)

3. **API:**
   - FastAPI async capabilities (future enhancement)
   - Response compression (future enhancement)

## Future Enhancements

1. **Performance:**
   - Redis caching layer
   - Database connection pooling optimization
   - Async/await for I/O operations

2. **Features:**
   - Real-time notifications (WebSocket)
   - Advanced reporting and analytics
   - Mobile app support
   - Biometric integration

3. **Security:**
   - Rate limiting
   - Two-factor authentication
   - Password reset functionality
   - Session management improvements

## Deployment Architecture

**Development:**
- Backend: `uvicorn` with auto-reload
- Frontend: Vite dev server with HMR
- Database: Local MySQL instance

**Production:**
- Backend: Served via FastAPI (static files included)
- Frontend: Built and copied to `backend/static/`
- Database: Production MySQL server
- Reverse proxy: Nginx (recommended)

See `docs/DEPLOYMENT.md` for detailed deployment instructions.

