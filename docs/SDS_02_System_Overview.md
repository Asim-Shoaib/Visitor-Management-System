# Software Design Specification (SDS)
## Document 2: System Overview

**Version:** 1.0.0  
**Date:** 2024  
**Project:** Visitor Management System

---

## 2.1 System Summary

The Visitor Management System (VMS) is a web-based application designed to manage visitor registrations, track employee attendance, and maintain security through QR code-based access control. The system provides role-based access control with separate interfaces for administrators and security personnel.

The system consists of:
- **Backend**: FastAPI-based REST API server (Python)
- **Frontend**: React-based single-page application
- **Database**: MySQL 8.0+ relational database
- **Authentication**: JWT token-based authentication

The system operates as a client-server architecture where the React frontend communicates with the FastAPI backend via REST API calls, and the backend interacts with the MySQL database for data persistence.

---

## 2.2 Major Features (Implemented)

### 2.2.1 Authentication & Authorization

**Implemented Features:**
- JWT-based user authentication
- Role-based access control (Admin, Security)
- Secure token management with 24-hour expiration
- Password hashing using SHA256
- User registration (admin-only)
- User deactivation (preserves audit trail)

**User Roles:**
- **Admin**: Full system access including user management, employee management, salary calculation, site management
- **Security**: Access to visitor management, scanning, attendance tracking, logs viewing

### 2.2.2 Visitor Management

**Implemented Features:**
- Visitor registration with CNIC validation (format: XXXXX-XXXXXXX-X)
- Visitor search by CNIC or visitor ID
- Unique CNIC enforcement
- Contact number storage (optional)
- Visitor information management

### 2.2.3 Visit Management

**Implemented Features:**
- Visit creation linking visitors to sites
- Optional host employee assignment
- Visit status tracking (pending, checked_in, checked_out, denied)
- Status transition validation
- Active visit monitoring
- Check-in/check-out timestamp recording
- Prevention of duplicate active visits

### 2.2.4 QR Code System

**Implemented Features:**
- Employee QR code generation (permanent, no expiry)
- Visitor QR code generation (temporary, 24-hour expiry)
- QR code storage as PNG files
- QR code email delivery with download links
- QR code download endpoint (public)
- QR code status management (active, expired, revoked)

### 2.2.5 QR Scanning & Attendance

**Implemented Features:**
- QR code verification (employee vs visitor detection)
- Employee attendance scanning (sign-in/sign-out)
- Visitor check-in/check-out workflows
- Late arrival detection (after 9:10 AM)
- Late arrival tracking (count in last 30 days)
- Late arrival email alerts (3+ times triggers alert)
- Automatic status updates based on scans

### 2.2.6 Employee Management

**Implemented Features:**
- Employee creation (admin-only)
- Employee information management
- Department assignment
- Hourly rate tracking
- Employee list viewing
- Employee status checking (signed in/out)
- Employee attendance logs

### 2.2.7 Salary Calculation

**Implemented Features:**
- Salary calculation based on attendance logs
- Date range selection
- Total hours calculation from sign-in/sign-out pairs
- Handling of incomplete days (no sign-out: counts until end of day)
- Daily breakdown display
- Excel export functionality
- Formula: `salary = total_hours × hourly_rate`

### 2.2.8 Audit Logging

**Implemented Features:**
- Comprehensive access logs for all system actions
- User tracking for all operations
- Action type logging
- Timestamp recording
- Date range filtering
- Action type filtering
- Excel export of logs

### 2.2.9 Alert System

**Implemented Features:**
- Security alerts for invalid QR codes
- Security alerts for expired QR codes
- Security alerts for revoked QR codes
- Visitor flagging capability
- Flagged visitor tracking
- Alert creation and management

### 2.2.10 Reporting

**Implemented Features:**
- Access log exports to Excel
- Salary report exports to Excel
- Date range filtering
- Formatted Excel files with headers and styling

### 2.2.11 Site Management

**Implemented Features:**
- Site creation (admin-only)
- Site list viewing
- Site information management

---

## 2.3 Intended Users

### 2.3.1 Administrators

**Capabilities:**
- Full system access
- User management (create, deactivate users)
- Employee management (create, view employees)
- Site management (create, view sites)
- Salary calculation and reporting
- Access to all logs and reports
- System configuration

**Use Cases:**
- Register new system users
- Create employee records
- Generate employee QR codes
- Calculate employee salaries
- View comprehensive system logs
- Export reports
- Manage sites and departments

### 2.3.2 Security Personnel

**Capabilities:**
- Visitor registration
- Visit creation
- QR code scanning (visitor and employee)
- Visitor check-in/check-out
- View active visits
- View access logs
- View alerts

**Use Cases:**
- Register visitors
- Create visits for visitors
- Generate visitor QR codes
- Scan QR codes at entry/exit points
- Check visitors in/out
- Monitor active visits
- View security alerts

### 2.3.3 Employees (Indirect Users)

**Capabilities:**
- None (no direct system access)
- QR codes used by security for attendance tracking

**Use Cases:**
- Present QR code for attendance scanning
- QR code scanned by security personnel

### 2.3.4 Visitors (Indirect Users)

**Capabilities:**
- None (no direct system access)
- Receive QR codes via email

**Use Cases:**
- Receive QR code via email
- Present QR code at entry point
- QR code scanned by security personnel

---

## 2.4 Operating Environments

### 2.4.1 Backend Environment

**Operating System:**
- Windows 10/11
- Linux (Ubuntu, CentOS, etc.)
- macOS

**Runtime:**
- Python 3.8 or higher
- FastAPI framework
- Uvicorn ASGI server

**Database:**
- MySQL 8.0 or higher
- MySQL Connector/Python driver

**Additional Services:**
- SMTP server for email delivery (Gmail, Outlook, or custom SMTP)

### 2.4.2 Frontend Environment

**Build Tool:**
- Node.js 18 or higher
- npm or yarn package manager
- Vite 5.0+ build tool

**Runtime:**
- Modern web browsers:
  - Chrome 90+
  - Firefox 88+
  - Safari 14+
  - Edge 90+

**Browser Features Required:**
- JavaScript enabled
- Camera API access (for QR scanning)
- LocalStorage support (for token storage)
- Fetch API support

### 2.4.3 Development Environment

**Backend Development:**
- Python virtual environment
- Code editor (VS Code, PyCharm, etc.)
- MySQL client (MySQL Workbench, command line, etc.)

**Frontend Development:**
- Node.js and npm
- Code editor with React support
- Browser developer tools

### 2.4.4 Production Environment

**Server:**
- Linux server (recommended) or Windows Server
- Python 3.8+ installed
- MySQL 8.0+ server
- Reverse proxy (Nginx recommended) for production

**Deployment:**
- Backend served via Uvicorn or Gunicorn
- Frontend built and served as static files
- Database on separate server (recommended for production)

---

## 2.5 Constraints

### 2.5.1 Database Constraints

- **No Schema Changes**: Database schema must not be modified. All features must use existing tables and fields only.
- **MySQL Only**: System designed for MySQL. Migration to other databases would require code changes.
- **Foreign Key Constraints**: All foreign key relationships are enforced at database level.

### 2.5.2 Functional Constraints

- **QR-Only Check-In**: Visitors and employees must use QR codes for check-in/check-out. No manual entry option.
- **Single Camera Device**: QR scanning assumes one camera device per security station.
- **Email Required**: Visitor QR codes are delivered via email. System requires functional SMTP configuration.
- **Admin-Only System Changes**: User creation, employee creation, site creation restricted to admin role.

### 2.5.3 Technical Constraints

- **JWT Token Expiration**: Tokens expire after 24 hours. Users must re-authenticate.
- **QR Code Expiry**: Visitor QR codes expire after 24 hours (configurable).
- **File System**: QR code images stored in `backend/generated_qr/` directory. Requires write permissions.
- **Browser Camera**: QR scanning requires browser camera permission and HTTPS in production (for camera access).

### 2.5.4 Business Constraints

- **CNIC Format**: Must follow format XXXXX-XXXXXXX-X (enforced by database CHECK constraint and application validation).
- **Late Arrival Threshold**: Fixed at 9:10 AM (hardcoded in `scan_service.py`).
- **Late Alert Threshold**: 3 or more late arrivals in 30 days triggers email alert.
- **Active Visit Limit**: Visitor cannot have multiple active visits (pending or checked_in) simultaneously.

### 2.5.5 Performance Constraints

- **Access Log Limit**: Access logs query returns up to 1000 most recent records.
- **No Caching**: Currently no caching layer. All queries hit database directly.
- **Synchronous Operations**: Email sending and QR generation are synchronous (may block request).

### 2.5.6 Security Constraints

- **Password Hashing**: SHA256 hashing (not bcrypt or Argon2). Consider upgrading for production.
- **CORS**: Currently allows all origins (`*`). Should be restricted in production.
- **Secret Key**: JWT secret key must be changed from default in production.
- **No Rate Limiting**: Currently no rate limiting on API endpoints.

---

## 2.6 System Boundaries

### 2.6.1 In Scope

- Visitor registration and management
- Visit creation and tracking
- QR code generation and management
- QR code scanning and verification
- Employee attendance tracking
- Salary calculation
- User authentication and authorization
- Audit logging
- Alert management
- Report generation and export

### 2.6.2 Out of Scope

- Visitor self-registration portals
- Mobile applications (iOS/Android)
- Biometric authentication
- Real-time notifications (WebSocket)
- Automated email scheduling
- Multi-tenant support
- Integration with external HR systems
- Integration with external access control systems
- Visitor pre-registration workflows
- Automated visitor approval workflows
- Visitor photo capture
- Visitor badge printing
- Visitor history analytics beyond basic logs

---

**End of Document 2: System Overview**

