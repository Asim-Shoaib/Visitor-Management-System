# Software Design Specification (SDS)
## Document 9: Assumptions and Dependencies

**Version:** 1.0.0  
**Date:** 2024  
**Project:** Visitor Management System

---

## 9.1 Assumptions

### 9.1.1 User Assumptions

**Assumption:** Admin role exists and is properly configured.

**Rationale:**
- System requires at least one admin user for initial setup
- Admin user needed for user management and system configuration
- Default admin credentials provided in setup

**Impact:**
- System cannot function without admin user
- Admin user must be created during initial setup
- Admin user cannot be deleted (business rule)

---

**Assumption:** Security personnel are trained to use QR scanning interface.

**Rationale:**
- Security staff operate the scanning interface
- They understand QR code scanning process
- They can handle camera and manual entry

**Impact:**
- Training may be required
- User support may be needed
- Interface should be intuitive

---

**Assumption:** Visitors have email addresses and can receive emails.

**Rationale:**
- QR codes delivered via email
- Visitors must have valid email
- Email delivery must be functional

**Impact:**
- Visitors without email cannot receive QR codes
- Email delivery failures prevent QR access
- Alternative delivery methods not available

---

### 9.1.2 System Assumptions

**Assumption:** Email sending functionality is working.

**Rationale:**
- SMTP server is accessible
- SMTP credentials are valid
- Network connectivity to SMTP server

**Impact:**
- QR code delivery depends on email
- Email failures prevent QR access
- System should handle email errors gracefully

**Location:**
- `backend/services/qr_service.py`
- `backend/services/email_service.py`

---

**Assumption:** Camera permission is allowed by users.

**Rationale:**
- QR scanning requires camera access
- Users must grant permission
- Browser must support camera API

**Impact:**
- Camera permission denial prevents scanning
- Manual QR entry available as fallback
- HTTPS required in production for camera

**Location:**
- `frontend/src/pages/CheckInOut.jsx`

---

**Assumption:** Guards rely on QR scanning for access control.

**Rationale:**
- System designed for QR-based access
- Guards scan QR codes at entry points
- No manual entry for access control

**Impact:**
- QR codes are primary access method
- System cannot function without QR scanning
- Guards must have scanning capability

---

**Assumption:** Internet connection required between frontend and backend.

**Rationale:**
- Frontend makes HTTP requests to backend
- Real-time data fetching
- No offline mode

**Impact:**
- Network connectivity required
- API calls fail without connection
- Error handling for network failures

**Location:**
- `frontend/src/services/api.js`

---

**Assumption:** Database is accessible and properly configured.

**Rationale:**
- All data stored in MySQL database
- Database connection required for all operations
- Database must be running

**Impact:**
- System cannot function without database
- Database connection failures cause errors
- Database must be backed up regularly

**Location:**
- `backend/database/connection.py`

---

**Assumption:** File system has write permissions for QR storage.

**Rationale:**
- QR code images saved to filesystem
- Directory creation required
- Write access needed

**Impact:**
- QR generation fails without write permission
- Directory must be accessible
- File system errors must be handled

**Location:**
- `backend/services/qr_service.py::_ensure_qr_directory()`

---

### 9.1.3 Business Assumptions

**Assumption:** Late arrival threshold (9:10 AM) is appropriate for all employees.

**Rationale:**
- Fixed threshold for all employees
- Business rule applied uniformly
- Cannot be customized per employee

**Impact:**
- All employees subject to same threshold
- No flexibility for different schedules
- Change requires code modification

---

**Assumption:** 24-hour QR code expiry is sufficient for visits.

**Rationale:**
- Visitor QR codes expire after 24 hours
- Most visits complete within 24 hours
- Extended visits require new QR code

**Impact:**
- Long visits may require QR regeneration
- Expired QR codes cannot be used
- Visitors must complete visit within 24 hours

---

**Assumption:** Salary calculation based on attendance logs is accurate.

**Rationale:**
- Salary calculated from sign-in/sign-out pairs
- Missing sign-outs handled (end-of-day)
- Calculation assumes accurate scanning

**Impact:**
- Inaccurate scanning affects salary
- Missing scans result in incorrect hours
- Manual correction may be needed

---

## 9.2 Dependencies

### 9.2.1 Backend Dependencies

#### Python Runtime

**Dependency:** Python 3.8 or higher

**Purpose:** Backend application runtime

**Location:** `requirements.txt`

**Installation:**
```bash
python --version  # Verify version
pip install -r requirements.txt
```

---

#### FastAPI Framework

**Dependency:** fastapi 0.104.1

**Purpose:** Web framework for REST API

**Features Used:**
- API route definition
- Request/response handling
- Dependency injection
- Automatic API documentation

**Location:** `backend/main.py`, all API files

---

#### Uvicorn Server

**Dependency:** uvicorn[standard] 0.24.0

**Purpose:** ASGI server for FastAPI

**Usage:**
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Location:** Server startup command

---

#### MySQL Connector

**Dependency:** mysql-connector-python 8.2.0

**Purpose:** MySQL database driver

**Features Used:**
- Database connection
- Query execution
- Parameterized queries

**Location:** `backend/database/connection.py`

---

#### Pydantic

**Dependency:** pydantic >= 2.7.0

**Purpose:** Data validation and settings management

**Features Used:**
- Request body validation
- Response models
- Field validators

**Location:** All API files (Pydantic models)

---

#### QR Code Library

**Dependency:** qrcode[pil] 7.4.2

**Purpose:** QR code image generation

**Features Used:**
- QR code generation
- Image file creation
- Error correction

**Location:** `backend/services/qr_service.py`

---

#### JWT Library

**Dependency:** PyJWT 2.8.0, python-jose[cryptography] 3.3.0

**Purpose:** JWT token generation and validation

**Features Used:**
- Token encoding
- Token decoding
- Signature verification

**Location:** `backend/utils/jwt_utils.py`

---

#### Excel Library

**Dependency:** openpyxl 3.1.2

**Purpose:** Excel file generation

**Features Used:**
- Workbook creation
- Worksheet manipulation
- Cell formatting
- File export

**Location:** `backend/services/logs_service.py`, `backend/services/site_service.py`

---

#### Email Validator

**Dependency:** email-validator 2.1.0

**Purpose:** Email format validation

**Features Used:**
- Email format checking
- Pydantic email validation

**Location:** `backend/utils/validator.py`, API models

---

### 9.2.2 Frontend Dependencies

#### React

**Dependency:** react 18.2.0+, react-dom 18.2.0+

**Purpose:** UI framework

**Features Used:**
- Component-based architecture
- Hooks (useState, useEffect, useContext)
- JSX syntax

**Location:** All frontend components

---

#### React Router

**Dependency:** react-router-dom 6.20.0+

**Purpose:** Client-side routing

**Features Used:**
- Route definition
- Navigation
- Protected routes

**Location:** `frontend/src/App.jsx`

---

#### Vite

**Dependency:** vite 5.0.8+, @vitejs/plugin-react 4.2.1+

**Purpose:** Build tool and dev server

**Features Used:**
- Development server
- Hot module replacement
- Production build

**Location:** `frontend/vite.config.js`

---

#### Axios

**Dependency:** axios 1.6.2+

**Purpose:** HTTP client

**Features Used:**
- API requests
- Request/response interceptors
- Error handling

**Location:** `frontend/src/services/api.js`

---

#### React Toastify

**Dependency:** react-toastify 9.1.3+

**Purpose:** Toast notifications

**Features Used:**
- Success notifications
- Error notifications
- Info notifications

**Location:** All frontend pages

---

#### QR Code React

**Dependency:** qrcode.react 3.1.0+

**Purpose:** QR code display component

**Features Used:**
- QR code rendering
- Image generation

**Location:** `frontend/src/pages/EmployeeQR.jsx`

---

#### HTML5 QR Code

**Dependency:** html5-qrcode 2.3.8+

**Purpose:** QR code scanning

**Features Used:**
- Camera access
- QR code detection
- Scanning interface

**Location:** `frontend/src/pages/CheckInOut.jsx`

---

### 9.2.3 System Dependencies

#### MySQL Database

**Dependency:** MySQL 8.0 or higher

**Purpose:** Data persistence

**Requirements:**
- MySQL server running
- Database created
- Schema applied
- User with appropriate permissions

**Location:** `backend/database/schema.sql`

---

#### SMTP Server

**Dependency:** SMTP server (Gmail, Outlook, or custom)

**Purpose:** Email delivery

**Requirements:**
- SMTP server accessible
- Valid credentials
- Network connectivity

**Location:** `backend/config/config.ini`

---

#### Web Browser

**Dependency:** Modern web browser with camera API support

**Requirements:**
- Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- JavaScript enabled
- Camera API support
- LocalStorage support
- HTTPS (for camera in production)

**Location:** Frontend runtime environment

---

#### Node.js

**Dependency:** Node.js 18 or higher

**Purpose:** Frontend development and build

**Requirements:**
- Node.js installed
- npm package manager
- Build tools

**Location:** `frontend/package.json`

---

### 9.2.4 Development Dependencies

#### Git

**Dependency:** Git (optional)

**Purpose:** Version control

**Usage:** Clone repository, track changes

---

#### Code Editor

**Dependency:** VS Code, PyCharm, or similar

**Purpose:** Code editing

**Features:** Syntax highlighting, debugging, IntelliSense

---

#### MySQL Client

**Dependency:** MySQL command line or MySQL Workbench

**Purpose:** Database management

**Usage:** Run schema, view data, manage database

---

## 9.3 Dependency Management

### 9.3.1 Backend Dependencies

**File:** `requirements.txt`

**Installation:**
```bash
pip install -r requirements.txt
```

**Virtual Environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

### 9.3.2 Frontend Dependencies

**File:** `frontend/package.json`

**Installation:**
```bash
cd frontend
npm install
```

**Production Build:**
```bash
npm run build
```

---

### 9.3.3 Database Setup

**File:** `backend/database/schema.sql`

**Setup:**
```bash
mysql -u root -p < backend/database/schema.sql
```

---

## 9.4 Dependency Versions

### 9.4.1 Version Pinning

**Backend:**
- Exact versions for critical dependencies
- Minimum versions for others
- Regular updates recommended

**Frontend:**
- Caret (^) for minor updates
- Regular updates recommended
- Test after updates

---

### 9.4.2 Compatibility

**Python:**
- Python 3.8+ required
- Tested on Python 3.8, 3.9, 3.10, 3.11

**Node.js:**
- Node.js 18+ required
- Tested on Node.js 18, 20

**MySQL:**
- MySQL 8.0+ required
- Tested on MySQL 8.0, 8.1

---

## 9.5 External Service Dependencies

### 9.5.1 Email Service

**Dependency:** SMTP service provider

**Options:**
- Gmail (with App Password)
- Outlook/Office 365
- Custom SMTP server

**Configuration:** `backend/config/config.ini`

**Failure Impact:**
- QR code delivery fails
- Late alerts not sent
- System continues to function (QR generation succeeds)

---

### 9.5.2 Camera Hardware

**Dependency:** Web camera device

**Requirements:**
- USB or built-in camera
- Browser-compatible
- User permission granted

**Failure Impact:**
- QR scanning unavailable
- Manual QR entry available as fallback
- System continues to function

---

## 9.6 Prerequisites

### 9.6.1 Development Prerequisites

1. Python 3.8+ installed
2. Node.js 18+ installed
3. MySQL 8.0+ installed and running
4. Git (optional, for version control)
5. Code editor (VS Code, PyCharm, etc.)
6. Web browser (for testing)

---

### 9.6.2 Production Prerequisites

1. Linux server (recommended) or Windows Server
2. Python 3.8+ installed
3. MySQL 8.0+ installed and running
4. Reverse proxy (Nginx recommended)
5. SSL certificate (for HTTPS)
6. SMTP server access
7. Firewall configuration
8. Backup system

---

**End of Document 9: Assumptions and Dependencies**

