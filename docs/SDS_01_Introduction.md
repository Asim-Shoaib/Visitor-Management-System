# Software Design Specification (SDS)
## Document 1: Introduction

**Version:** 1.0.0  
**Date:** 2024  
**Project:** Visitor Management System

---

## 1.1 Purpose

This Software Design Specification (SDS) document provides a comprehensive design specification for the Visitor Management System (VMS). The system is designed to manage visitor registrations, track employee attendance, generate QR codes for access control, and maintain comprehensive audit logs.

This document describes the system architecture, component design, interfaces, data structures, and algorithms as implemented in the actual codebase. All specifications are based on the existing implementation found in the `backend/` and `frontend/` directories.

---

## 1.2 Scope

The Visitor Management System encompasses the following implemented features:

- **Visitor Management**: Visitor registration with CNIC validation, visitor search, and visitor information management
- **Visit Management**: Visit creation, status tracking (pending, checked_in, checked_out, denied), and active visit monitoring
- **QR Code System**: Employee QR code generation (permanent), visitor QR code generation (temporary with expiry), QR code email delivery, and QR code download
- **QR Code Scanning**: QR code verification, employee attendance scanning, visitor check-in/check-out workflows
- **Employee Management**: Employee creation, employee information management, department assignment, hourly rate tracking
- **Attendance Tracking**: Employee sign-in/sign-out logging, late arrival detection (threshold: 9:10 AM), late arrival alerts (3+ times in 30 days)
- **Salary Calculation**: Salary calculation based on attendance logs, date range filtering, daily breakdown, Excel export
- **Authentication & Authorization**: JWT-based user authentication, role-based access control (Admin, Security), secure token management
- **Audit Logging**: Comprehensive access logs for all system actions with filtering capabilities
- **Alert System**: Security alerts for invalid/expired/revoked QR codes, visitor flagging
- **Reporting**: Access log exports, salary report exports, Excel file generation

The system does NOT include:
- Visitor self-registration portals
- Mobile applications
- Biometric authentication
- Real-time notifications (WebSocket)
- Automated email scheduling
- Multi-tenant support

---

## 1.3 Definitions and Acronyms

### Terms Used in Documentation

- **Visitor**: An external person visiting the premises who must be registered in the system
- **Employee**: A staff member of the organization with an employee record and optional QR code
- **Visit**: A scheduled or ad-hoc visit by a visitor, linked to a site and optionally a host employee
- **QR Code**: Quick Response code used for access control and attendance tracking
- **Check-In/Check-Out**: Process of recording visitor entry and exit using QR code scanning
- **Sign-In/Sign-Out**: Process of recording employee attendance using QR code scanning
- **AccessLogs**: Audit trail table storing all system actions with user, action type, details, and timestamp
- **CNIC**: Computerized National Identity Card (format: XXXXX-XXXXXXX-X)
- **JWT**: JSON Web Token used for authentication
- **Admin**: Administrator role with full system access
- **Security**: Security personnel role with scanning and visitor viewing access
- **Site**: Physical location or office where visits occur
- **Department**: Organizational unit for employee categorization

### Acronyms

- **VMS**: Visitor Management System
- **API**: Application Programming Interface
- **REST**: Representational State Transfer
- **JWT**: JSON Web Token
- **CNIC**: Computerized National Identity Card
- **QR**: Quick Response (code)
- **SMTP**: Simple Mail Transfer Protocol
- **HTTP**: Hypertext Transfer Protocol
- **JSON**: JavaScript Object Notation
- **SQL**: Structured Query Language
- **ERD**: Entity Relationship Diagram
- **SDS**: Software Design Specification

---

## 1.4 References

### Project Documentation

1. **API Reference** (`docs/API_REFERENCE.md`)
   - Complete documentation of all 43 API endpoints
   - Request/response formats
   - Authentication requirements
   - Error codes

2. **System Overview** (`docs/SYSTEM_OVERVIEW.md`)
   - System architecture
   - Technology stack
   - Core features explanation
   - Data flow diagrams

3. **Data Dictionary** (`docs/DATA_DICTIONARY.md`)
   - Complete database schema documentation
   - All 13 tables with field definitions
   - Relationships and constraints

4. **Setup Guide** (`docs/SETUP_GUIDE.md`)
   - Installation instructions
   - Configuration details
   - Troubleshooting guide

5. **Deployment Guide** (`docs/DEPLOYMENT.md`)
   - Production deployment instructions
   - Server configuration
   - Security best practices

6. **Implementation Summary** (`docs/IMPLEMENTATION_SUMMARY.md`)
   - Task completion status
   - Implementation details
   - Feature verification

7. **Phase 8 Implementation** (`docs/PHASE_8_IMPLEMENTATION.md`)
   - Phase 8 specific features
   - Employee addition
   - Salary calculation

### External References

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **React Documentation**: https://react.dev/
- **MySQL Documentation**: https://dev.mysql.com/doc/
- **JWT Specification**: RFC 7519 (https://tools.ietf.org/html/rfc7519)
- **Pydantic Documentation**: https://docs.pydantic.dev/
- **React Router Documentation**: https://reactrouter.com/
- **Axios Documentation**: https://axios-http.com/
- **OpenPyXL Documentation**: https://openpyxl.readthedocs.io/
- **QRCode Library**: https://github.com/lincolnloop/python-qrcode

### Codebase References

- **Database Schema**: `backend/database/schema.sql`
- **Backend API Routes**: `backend/api/*.py`
- **Backend Services**: `backend/services/*.py`
- **Frontend Pages**: `frontend/src/pages/*.jsx`
- **Frontend Components**: `frontend/src/components/*.jsx`
- **Configuration**: `backend/config/config.ini`
- **Requirements**: `requirements.txt`
- **Frontend Dependencies**: `frontend/package.json`

---

## 1.5 Document Organization

This SDS is organized into 10 separate documents:

1. **SDS_01_Introduction.md** (This document) - Purpose, scope, definitions, references
2. **SDS_02_System_Overview.md** - System summary, features, users, environments, constraints
3. **SDS_03_Architectural_Design.md** - Architecture, subsystems, components, technology stack
4. **SDS_04_Detailed_Design.md** - Component design, interfaces, data design, algorithms
5. **SDS_05_User_Interface_Design.md** - UI pages, layouts, interactions, placeholders
6. **SDS_06_External_Interface_Design.md** - External dependencies, protocols, integrations
7. **SDS_07_Non_Functional_Requirements.md** - Performance, security, reliability, maintainability
8. **SDS_08_Design_Constraints.md** - Database constraints, QR-only flow, camera requirements
9. **SDS_09_Assumptions_Dependencies.md** - Assumptions, dependencies, prerequisites
10. **SDS_10_Appendices.md** - Glossary, diagrams, additional documentation

Each document focuses on a specific aspect of the system design and references the actual implementation in the codebase.

---

## 1.6 Document Conventions

- **Code blocks**: Used for code examples, SQL queries, API requests/responses
- **Placeholders**: `[Diagram Placeholder]` or `[Screenshot Placeholder]` indicate where diagrams/images would be inserted
- **File paths**: Relative paths from project root (e.g., `backend/api/site_api.py`)
- **API endpoints**: Full URL format (e.g., `POST /site/employees/create`)
- **Database tables**: Capitalized (e.g., `Employees`, `Visits`)
- **Functions**: Python function names (e.g., `create_employee()`)
- **Components**: React component names (e.g., `EmployeeManagement`)

---

**End of Document 1: Introduction**

