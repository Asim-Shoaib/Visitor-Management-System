# Software Design Specification (SDS)
## Document 10: Appendices

**Version:** 1.0.0  
**Date:** 2024  
**Project:** Visitor Management System

---

## 10.1 Glossary

### A

**AccessLogs**: Database table storing audit trail of all system actions with user, action type, details, and timestamp.

**Admin**: Administrator role with full system access including user management, employee management, salary calculation, and site management.

**API**: Application Programming Interface - REST API endpoints for frontend-backend communication.

**Attendance**: Employee sign-in/sign-out tracking via QR code scanning.

---

### B

**Backend**: FastAPI-based REST API server written in Python.

**Bearer Token**: JWT token sent in Authorization header as "Bearer <token>".

---

### C

**Check-In**: Process of recording visitor entry using QR code scanning, updates visit status to 'checked_in' and sets checkin_time.

**Check-Out**: Process of recording visitor exit using QR code scanning, updates visit status to 'checked_out' and sets checkout_time.

**CNIC**: Computerized National Identity Card - Pakistani ID format (XXXXX-XXXXXXX-X).

**Context**: React Context API for global state management (AuthContext, DataContext).

---

### D

**Dashboard**: Main page displaying system statistics and active visits.

**Department**: Organizational unit for employee categorization, stored in Departments table.

---

### E

**Employee**: Staff member of the organization with employee record, hourly rate, and optional QR code.

**EmployeeQRCodes**: Database table storing permanent QR codes for employees.

**EmployeeScanLogs**: Database table storing employee attendance logs (sign-in/sign-out records).

**ENUM**: Database data type restricting values to specific options (e.g., status ENUM('pending','checked_in','checked_out','denied')).

---

### F

**FastAPI**: Modern Python web framework used for backend API.

**Foreign Key**: Database constraint maintaining referential integrity between tables.

**Frontend**: React-based single-page application running in web browsers.

---

### G

**Guard**: Security personnel role with access to visitor management, scanning, and attendance tracking.

---

### H

**Hourly Rate**: Employee wage rate stored in Employees table, used for salary calculation.

**HTTPS**: Hypertext Transfer Protocol Secure - required for camera access in production.

---

### I

**JWT**: JSON Web Token - token-based authentication mechanism with 24-hour expiration.

---

### L

**Late Arrival**: Employee check-in after 9:10 AM, tracked and triggers alerts if 3+ times in 30 days.

**LocalStorage**: Browser storage for JWT token persistence.

---

### M

**MySQL**: Relational database management system used for data persistence.

---

### P

**Pydantic**: Python library for data validation using type annotations.

**Purpose Details**: Optional text field in Visits table describing visit purpose.

---

### Q

**QR Code**: Quick Response code used for access control and attendance tracking.

**QR Scanner**: Browser-based QR code scanning using camera API (html5-qrcode library).

---

### R

**React**: JavaScript library for building user interfaces.

**REST**: Representational State Transfer - architectural style for web APIs.

**Role**: User role (admin or security) determining system access permissions.

---

### S

**Salary Calculation**: Process of calculating employee salary based on attendance logs and hourly rate.

**Scan Status**: Status of QR scan - "signin" or "signout" for employees, "signin" or "signout" for visitors.

**Security**: Security personnel role with limited access (visitor management, scanning, logs viewing).

**SHA256**: Cryptographic hash function used for password hashing.

**Sign-In**: Employee attendance action recorded via QR scanning, stored in EmployeeScanLogs.

**Sign-Out**: Employee attendance action recorded via QR scanning, stored in EmployeeScanLogs.

**Site**: Physical location or office where visits occur, stored in Sites table.

**SMTP**: Simple Mail Transfer Protocol - used for email delivery of QR codes.

---

### T

**Token**: JWT token used for authentication, stored in localStorage and sent in Authorization header.

---

### U

**User**: System user account for authentication, stored in Users table with username, password_hash, and role_id.

---

### V

**Visit**: Record of a visitor's visit to a site, stored in Visits table with status, timestamps, and optional host employee.

**Visitor**: External person visiting the premises, stored in Visitors table with CNIC, name, and contact number.

**VisitorQRCodes**: Database table storing temporary QR codes for visitors with 24-hour expiry.

**VisitorScanLogs**: Database table storing visitor scan logs (check-in/check-out records).

---

## 10.2 Diagram Placeholders

### 10.2.1 Architecture Diagram

[Architecture Diagram Placeholder: Three-tier architecture showing React Frontend, FastAPI Backend, and MySQL Database with communication flows and protocols]

---

### 10.2.2 Entity Relationship Diagram (ERD)

[ERD Placeholder: Entity Relationship Diagram showing all 13 database tables (Departments, Employees, Roles, Users, AccessLogs, Sites, Visitors, Visits, EmployeeQRCodes, VisitorQRCodes, Alerts, EmployeeScanLogs, VisitorScanLogs) with relationships, primary keys, and foreign keys]

---

### 10.2.3 Sequence Diagrams

[Sequence Diagram Placeholder: Login Flow - User submits credentials, backend validates, generates JWT, returns token, frontend stores token]

[Sequence Diagram Placeholder: Visitor Registration and QR Generation Flow - User registers visitor, creates visit, generates QR code, sends email]

[Sequence Diagram Placeholder: QR Scanning and Check-In Flow - Security scans QR, backend verifies, updates visit status, returns result]

[Sequence Diagram Placeholder: Employee Attendance Scanning Flow - Security scans employee QR, backend records attendance, detects late arrival, triggers alert if needed]

[Sequence Diagram Placeholder: Salary Calculation Flow - Admin selects employee and date range, backend calculates from logs, returns breakdown, exports to Excel]

---

### 10.2.4 State Diagrams

[State Diagram Placeholder: Visit Status State Machine - States: pending, checked_in, checked_out, denied. Transitions: pending -> checked_in, pending -> denied, checked_in -> checked_out]

[State Diagram Placeholder: QR Code Status State Machine - States: active, expired, revoked. Transitions: active -> expired (time-based), active -> revoked (manual)]

[State Diagram Placeholder: Employee Attendance State Machine - States: signed_out, signed_in. Transitions: signed_out -> signed_in (scan signin), signed_in -> signed_out (scan signout)]

---

### 10.2.5 Component Diagram

[Component Diagram Placeholder: Backend components showing API layer, Service layer, Database layer, and Utilities with relationships]

[Component Diagram Placeholder: Frontend components showing Pages, Components, Contexts, and Services with relationships]

---

### 10.2.6 Deployment Diagram

[Deployment Diagram Placeholder: Production deployment showing Web Browser, Nginx Reverse Proxy, FastAPI Backend, MySQL Database, and SMTP Server with network connections]

---

## 10.3 Additional Documentation

### 10.3.1 API Reference

**File:** `docs/API_REFERENCE.md`

**Content:**
- Complete API endpoint documentation
- Request/response formats
- Authentication requirements
- Error codes
- Example requests

---

### 10.3.2 System Overview

**File:** `docs/SYSTEM_OVERVIEW.md`

**Content:**
- System architecture
- Technology stack
- Core features explanation
- Data flow diagrams

---

### 10.3.3 Data Dictionary

**File:** `docs/DATA_DICTIONARY.md`

**Content:**
- Complete database schema documentation
- All 13 tables with field definitions
- Relationships and constraints
- Sample data

---

### 10.3.4 Setup Guide

**File:** `docs/SETUP_GUIDE.md`

**Content:**
- Installation instructions
- Configuration details
- Database setup
- Troubleshooting guide

---

### 10.3.5 Deployment Guide

**File:** `docs/DEPLOYMENT.md`

**Content:**
- Production deployment instructions
- Server configuration
- Security best practices
- Performance optimization

---

### 10.3.6 Quick Start Guide

**File:** `docs/QUICKSTART.md`

**Content:**
- 5-minute setup guide
- Quick reference commands
- Default credentials
- Common tasks

---

### 10.3.7 Implementation Summary

**File:** `docs/IMPLEMENTATION_SUMMARY.md`

**Content:**
- Task completion status
- Implementation details
- Feature verification
- Testing results

---

### 10.3.8 Phase 8 Implementation

**File:** `docs/PHASE_8_IMPLEMENTATION.md`

**Content:**
- Phase 8 specific features
- Employee addition implementation
- Salary calculation implementation
- Testing and verification

---

### 10.3.9 Build Instructions

**File:** `docs/BUILD_INSTRUCTIONS.md`

**Content:**
- Backend build steps
- Frontend build steps
- Production build process
- Deployment preparation

---

### 10.3.10 Run Commands

**File:** `docs/RUN_COMMANDS.md`

**Content:**
- Development server commands
- Production server commands
- Database commands
- Utility commands

---

### 10.3.11 Requirements Compliance

**File:** `docs/REQUIREMENTS_COMPLIANCE.md`

**Content:**
- Requirements checklist
- Implementation status
- Compliance verification

---

### 10.3.12 Changelog

**File:** `docs/CHANGELOG.md`

**Content:**
- Version history
- Feature additions
- Bug fixes
- Breaking changes

---

## 10.4 Code References

### 10.4.1 Backend Code Structure

```
backend/
├── api/              # API endpoints
│   ├── auth_api.py
│   ├── visitor_api.py
│   ├── visit_api.py
│   ├── qr_api.py
│   ├── scan_api.py
│   ├── site_api.py
│   ├── logs_api.py
│   ├── reports_api.py
│   ├── alert_api.py
│   ├── user_management_api.py
│   ├── attendance_api.py
│   └── email_api.py
├── services/         # Business logic
│   ├── auth_service.py
│   ├── visitor_service.py
│   ├── visit_service.py
│   ├── qr_service.py
│   ├── scan_service.py
│   ├── site_service.py
│   ├── logs_service.py
│   ├── alert_service.py
│   └── email_service.py
├── utils/            # Utilities
│   ├── auth_dependency.py
│   ├── jwt_utils.py
│   ├── validator.py
│   └── db_logger.py
├── database/         # Database files
│   ├── connection.py
│   └── schema.sql
├── config/           # Configuration
│   └── config.ini
├── generated_qr/     # QR code images
└── main.py           # FastAPI application
```

---

### 10.4.2 Frontend Code Structure

```
frontend/
├── src/
│   ├── pages/        # Page components
│   │   ├── Login.jsx
│   │   ├── Dashboard.jsx
│   │   ├── VisitorEntry.jsx
│   │   ├── CheckInOut.jsx
│   │   ├── EmployeeQR.jsx
│   │   ├── EmployeeAttendance.jsx
│   │   ├── EmployeeManagement.jsx
│   │   ├── SalaryCalculation.jsx
│   │   ├── VisitLogs.jsx
│   │   ├── UserManagement.jsx
│   │   ├── SiteManagement.jsx
│   │   └── AdminProfile.jsx
│   ├── components/   # Reusable components
│   │   ├── Layout.jsx
│   │   └── Layout.css
│   ├── contexts/     # React contexts
│   │   ├── AuthContext.jsx
│   │   └── DataContext.jsx
│   ├── services/     # API service layer
│   │   └── api.js
│   ├── App.jsx       # Main app component
│   ├── main.jsx      # Entry point
│   └── index.css     # Global styles
├── package.json
├── vite.config.js
└── index.html
```

---

## 10.5 Configuration Files

### 10.5.1 Backend Configuration

**File:** `backend/config/config.ini`

**Sections:**
- `[database]` - MySQL connection settings
- `[email]` - SMTP server settings
- `[app]` - Application settings (secret_key, QR expiry, base_url)

---

### 10.5.2 Frontend Configuration

**File:** `frontend/.env` (optional)

**Variables:**
- `VITE_API_URL` - Backend API base URL (default: http://localhost:8000)

---

### 10.5.3 Dependencies

**Backend:** `requirements.txt`

**Frontend:** `frontend/package.json`

---

## 10.6 Database Schema Reference

**File:** `backend/database/schema.sql`

**Tables:**
1. Departments
2. Employees
3. Roles
4. Users
5. AccessLogs
6. Sites
7. Visitors
8. Visits
9. EmployeeQRCodes
10. VisitorQRCodes
11. Alerts
12. EmployeeScanLogs
13. VisitorScanLogs

See `docs/DATA_DICTIONARY.md` for complete schema documentation.

---

## 10.7 API Endpoint Summary

**Total Endpoints:** 43

**Categories:**
- Authentication: 4 endpoints
- Visitors: 4 endpoints
- Visits: 3 endpoints
- QR Codes: 4 endpoints
- Scanning: 5 endpoints
- Sites/Employees: 9 endpoints
- Logs: 2 endpoints
- Reports: 1 endpoint
- Alerts: 2 endpoints
- Users: 3 endpoints
- Attendance: 1 endpoint
- Email: 2 endpoints

See `docs/API_REFERENCE.md` for complete endpoint documentation.

---

## 10.8 Version History

**Version 1.0.0** (Current)
- Initial release
- All Phase 1-8 features implemented
- Complete documentation
- Production-ready

---

## 10.9 Contact and Support

**Documentation:** See `docs/` folder for all documentation files.

**Code Repository:** See project root for source code.

**Issues:** Refer to documentation or contact development team.

---

**End of Document 10: Appendices**

**End of Software Design Specification (SDS)**

