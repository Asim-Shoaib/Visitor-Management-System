# Visitor Management System

**Version:** 1.0.0  
**Status:** Production Ready

A comprehensive visitor and employee management system with QR code-based access control, attendance tracking, salary calculation, and comprehensive audit logging.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Overview](#api-overview)
- [Frontend Pages](#frontend-pages)
- [Documentation](#documentation)
- [License](#license)

---

## Features

### Core Functionality

✅ **Authentication & Authorization**
- JWT-based user authentication (24-hour token expiration)
- Role-based access control (Admin, Security)
- Secure password hashing (SHA256)

✅ **Visitor Management**
- Visitor registration with CNIC validation (format: XXXXX-XXXXXXX-X)
- Visitor search by CNIC or visitor ID
- Visitor check-in/check-out workflows
- Visit creation and status tracking

✅ **Employee Management**
- Employee creation (admin only)
- Department assignment
- Hourly rate tracking
- Employee QR code generation (permanent)

✅ **QR Code System**
- Employee QR codes (permanent, no expiry)
- Visitor QR codes (temporary, 24-hour expiry)
- QR code email delivery
- QR code download endpoint
- QR code verification

✅ **Attendance Tracking**
- Employee sign-in/sign-out via QR scanning
- Late arrival detection (threshold: 9:10 AM)
- Late arrival alerts (3+ times in 30 days)
- Real-time attendance status

✅ **Salary Calculation**
- Calculate salary based on attendance logs
- Date range filtering
- Daily breakdown display
- Excel export functionality
- Formula: `salary = total_hours × hourly_rate`

✅ **Audit & Logging**
- Comprehensive access logs for all operations
- Filterable by date range and action type
- Excel export for logs
- User action tracking

✅ **Alert System**
- Security alerts for invalid/expired QR codes
- Visitor flagging capability
- Alert management interface

---

## Tech Stack

### Backend
- **Framework:** FastAPI 0.104.1
- **Language:** Python 3.8+
- **Database:** MySQL 8.0+
- **Authentication:** JWT (PyJWT 2.8.0)
- **QR Code Generation:** qrcode[pil] 7.4.2
- **Excel Export:** openpyxl 3.1.2
- **Server:** Uvicorn 0.24.0

### Frontend
- **Framework:** React 18.2.0
- **Build Tool:** Vite 5.0.8
- **Routing:** React Router 6.20.0
- **HTTP Client:** Axios 1.6.2
- **Notifications:** React Toastify 9.1.3
- **QR Display:** qrcode.react 3.1.0
- **QR Scanner:** html5-qrcode 2.3.8

### Database
- **RDBMS:** MySQL 8.0+
- **Tables:** 13 core tables (Users, Roles, Visitors, Visits, Employees, Sites, Departments, QR Codes, Scan Logs, AccessLogs, Alerts)

---

## Project Structure

```
Visitor-Management-System/
├── backend/
│   ├── api/                    # FastAPI route handlers
│   │   ├── auth_api.py         # Authentication endpoints
│   │   ├── visitor_api.py      # Visitor management
│   │   ├── visit_api.py        # Visit management
│   │   ├── qr_api.py           # QR code generation
│   │   ├── scan_api.py         # QR scanning
│   │   ├── site_api.py         # Sites, employees, salary
│   │   ├── logs_api.py         # Access logs
│   │   ├── attendance_api.py   # Attendance scanning
│   │   ├── user_management_api.py  # User management
│   │   ├── alert_api.py        # Alert management
│   │   ├── email_api.py        # Email functionality
│   │   └── reports_api.py      # Report exports
│   ├── services/               # Business logic
│   │   ├── auth_service.py     # Authentication logic
│   │   ├── visitor_service.py  # Visitor operations
│   │   ├── visit_service.py    # Visit operations
│   │   ├── qr_service.py       # QR code generation
│   │   ├── scan_service.py     # Scanning logic
│   │   ├── site_service.py     # Site/employee/salary
│   │   ├── logs_service.py     # Logging operations
│   │   ├── alert_service.py    # Alert management
│   │   └── email_service.py    # Email sending
│   ├── utils/                  # Utilities
│   │   ├── auth_dependency.py  # JWT authentication
│   │   ├── jwt_utils.py        # JWT token handling
│   │   ├── validator.py        # Input validation
│   │   └── db_logger.py        # Audit logging
│   ├── database/               # Database files
│   │   ├── connection.py       # Database connection
│   │   └── schema.sql          # Database schema
│   ├── config/                 # Configuration
│   │   └── config.ini          # App configuration
│   ├── generated_qr/           # QR code images (gitignored)
│   └── main.py                 # FastAPI application entry
├── frontend/
│   ├── src/
│   │   ├── pages/              # Page components
│   │   │   ├── Login.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── EmployeeQR.jsx
│   │   │   ├── VisitorEntry.jsx
│   │   │   ├── CheckInOut.jsx
│   │   │   ├── EmployeeAttendance.jsx
│   │   │   ├── VisitLogs.jsx
│   │   │   ├── UserManagement.jsx
│   │   │   ├── EmployeeManagement.jsx
│   │   │   ├── SiteManagement.jsx
│   │   │   ├── SalaryCalculation.jsx
│   │   │   └── AdminProfile.jsx
│   │   ├── components/         # Reusable components
│   │   │   ├── Layout.jsx
│   │   │   └── Layout.css
│   │   ├── contexts/           # React contexts
│   │   │   ├── AuthContext.jsx # Authentication state
│   │   │   └── DataContext.jsx # Data caching
│   │   ├── services/           # API service
│   │   │   └── api.js          # Axios configuration
│   │   ├── App.jsx             # Main app component
│   │   ├── main.jsx            # Entry point
│   │   └── index.css           # Global styles
│   ├── package.json
│   └── vite.config.js
├── docs/                       # Documentation
│   ├── SDS_01_Introduction.md
│   ├── SDS_02_System_Overview.md
│   ├── SDS_03_Architectural_Design.md
│   ├── SDS_04_Detailed_Design.md
│   ├── SDS_05_User_Interface_Design.md
│   ├── SDS_06_External_Interface_Design.md
│   ├── SDS_07_Non_Functional_Requirements.md
│   ├── SDS_08_Design_Constraints.md
│   ├── SDS_09_Assumptions_Dependencies.md
│   ├── SDS_10_Appendices.md
│   ├── API_REFERENCE.md        # Complete API documentation
│   ├── DATA_DICTIONARY.md      # Database schema
│   ├── SETUP_GUIDE.md          # Installation guide
│   ├── SYSTEM_OVERVIEW.md      # Architecture overview
│   ├── DEPLOYMENT.md           # Deployment guide
│   └── README.md               # Documentation index
├── requirements.txt            # Python dependencies
├── setup_database.sql          # Seed data
└── README.md                   # This file
```

---

## Installation

### Prerequisites

- Python 3.8+
- Node.js 18+
- MySQL 8.0+
- Git (optional)

### Backend Setup

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Create database and app user:**
```bash
# Log in as root
mysql -u root -p

# Then run these commands in MySQL:
CREATE DATABASE IF NOT EXISTS Visitor_Management_System 
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'vms'@'localhost' IDENTIFIED BY 'your-strong-password';
GRANT ALL PRIVILEGES ON Visitor_Management_System.* TO 'vms'@'localhost';
FLUSH PRIVILEGES;

# Exit MySQL and run schema
mysql -u vms -p Visitor_Management_System < backend/database/schema.sql
```

3. **Initialize database (optional):**
```bash
mysql -u vms -p Visitor_Management_System < setup_database.sql
```

4. **Configure backend:**
Edit `backend/config/config.ini`:
```ini
[database]
host = localhost
port = 3306
user = vms
password = your-strong-password
database = Visitor_Management_System

[email]
smtp_server = smtp.gmail.com
smtp_port = 587
sender_email = your_email@gmail.com
sender_password = your_app_password
admin_email = admin@example.com

[app]
secret_key = your-secret-key-change-in-production
qr_code_expiry_hours = 24
base_url = http://localhost:8000
```

### Frontend Setup

1. **Install Node dependencies:**
```bash
cd frontend
npm install
```

2. **Configure frontend (optional):**
Create `frontend/.env`:
```
VITE_API_URL=http://localhost:8000
```

---

## Configuration

### Environment Variables

**Backend:**
- Configuration via `backend/config/config.ini`
- Database credentials
- Email SMTP settings
- JWT secret key
- Base URL

**Frontend:**
- `VITE_API_URL` - Backend API URL (defaults to `http://localhost:8000`)

### Default Credentials

- **Username:** `admin`
- **Password:** `admin123`

⚠️ **Important:** Change default password immediately in production!

---

## Running the Application

### Development Mode

**Terminal 1 - Backend:**
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

- Backend API: `http://localhost:8000`
- Frontend: `http://localhost:3000` (or port shown)
- API Docs: `http://localhost:8000/docs`

### Production Mode

1. **Build frontend:**
```bash
cd frontend
npm run build
```

2. **Copy build to backend:**
```bash
# Windows
xcopy /E /I frontend\dist backend\static

# Linux/Mac
cp -r frontend/dist/* backend/static/
```

3. **Run backend:**
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

- Application: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

---

## API Overview

### Base URL
```
http://localhost:8000
```

### Authentication
All protected endpoints require JWT token:
```
Authorization: Bearer <jwt_token>
```

### Endpoint Categories

**Authentication** (`/auth`)
- `POST /auth/login` - Login
- `POST /auth/register-user` - Register user (admin)
- `PATCH /auth/deactivate-user/{id}` - Deactivate user (admin)

**Visitors** (`/visitor`)
- `POST /visitor/add-visitor` - Register visitor
- `GET /visitor/search-visitor` - Search visitor
- `POST /visitor/checkin` - Check in visitor
- `POST /visitor/checkout` - Check out visitor

**Visits** (`/visit`)
- `POST /visit/create-visit` - Create visit
- `PATCH /visit/update-status/{id}` - Update visit status
- `GET /visit/active-visits` - Get active visits

**QR Codes** (`/qr`)
- `POST /qr/generate-employee` - Generate employee QR
- `POST /qr/generate-visitor` - Generate visitor QR
- `GET /qr/download/{id}` - Download QR image

**Scanning** (`/scan`)
- `POST /scan/verify` - Verify QR code
- `POST /scan/employee` - Scan employee QR
- `POST /scan/visitor` - Scan visitor QR
- `GET /scan/alerts` - Get alerts
- `GET /scan/employee/late-count/{id}` - Get late count

**Site & Employees** (`/site`)
- `GET /site/list` - Get all sites
- `POST /site/create-site` - Create site (admin)
- `GET /site/employees` - Get all employees
- `POST /site/employees/create` - Create employee (admin)
- `GET /site/employees/{id}/salary` - Calculate salary (admin)
- `GET /site/employees/{id}/salary/export` - Export salary (admin)
- `GET /site/departments` - Get departments

**Attendance** (`/attendance`)
- `POST /attendance/scan` - Scan employee QR for attendance

**Logs** (`/logs`)
- `GET /logs/access` - Get access logs
- `GET /logs/export` - Export logs to Excel

**Users** (`/users`)
- `POST /users/create` - Create user (admin)
- `DELETE /users/{id}` - Delete user (admin)
- `GET /users/list` - List users (admin)

**Alerts** (`/alerts`)
- `POST /alerts/flag` - Flag visitor
- `GET /alerts/flagged-visitors` - Get flagged visitors

**Reports** (`/reports`)
- `GET /reports/export` - Export reports

**Email** (`/email`)
- `POST /email/send-qr` - Send QR via email
- `POST /email/alert-late` - Send late alerts

**Health** (`/health`)
- `GET /health` - Health check

### Interactive API Documentation

FastAPI provides automatic interactive documentation:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

For complete API documentation, see [docs/API_REFERENCE.md](docs/API_REFERENCE.md).

---

## Frontend Pages

### Public Routes
- `/login` - Login page

### Protected Routes (All Users)
- `/` - Dashboard (statistics and overview)
- `/employee-qr` - Generate employee QR codes
- `/visitor-entry` - Visitor registration and visit creation
- `/checkin-out` - QR code scanning (camera or manual)
- `/employee-attendance` - Employee attendance view
- `/logs` - Access logs viewer

### Admin-Only Routes
- `/users` - User management
- `/employees` - Employee management (with create form)
- `/sites` - Site management
- `/salary` - Salary calculation and export
- `/profile` - Admin profile

### Features
- JWT token management with automatic refresh
- Toast notifications for user feedback
- Loading states and spinners
- Input validation
- QR code scanning via camera
- Responsive design
- Error handling
- Protected routes with role-based access

---

## Documentation

### Software Design Specification (SDS)

Complete SDS documents available in `docs/`:
- **SDS_01_Introduction.md** - Purpose, scope, definitions
- **SDS_02_System_Overview.md** - Features, use cases, architecture
- **SDS_03_Architectural_Design.md** - System architecture, components
- **SDS_04_Detailed_Design.md** - Component design, data structures
- **SDS_05_User_Interface_Design.md** - UI/UX design, wireframes
- **SDS_06_External_Interface_Design.md** - API specifications, interfaces
- **SDS_07_Non_Functional_Requirements.md** - Performance, security, reliability
- **SDS_08_Design_Constraints.md** - Technical constraints, limitations
- **SDS_09_Assumptions_Dependencies.md** - Assumptions, dependencies
- **SDS_10_Appendices.md** - Glossary, references, diagrams

### Additional Documentation

- **[API_REFERENCE.md](docs/API_REFERENCE.md)** - Complete API endpoint documentation
- **[DATA_DICTIONARY.md](docs/DATA_DICTIONARY.md)** - Database schema and data dictionary
- **[SETUP_GUIDE.md](docs/SETUP_GUIDE.md)** - Detailed installation and setup instructions
- **[SYSTEM_OVERVIEW.md](docs/SYSTEM_OVERVIEW.md)** - System architecture and features
- **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Production deployment guide
- **[docs/README.md](docs/README.md)** - Documentation index

---

## Database Schema

The system uses 13 core tables:

1. **Users** - System user accounts
2. **Roles** - User roles (admin, security)
3. **Visitors** - Visitor information
4. **Visits** - Visit records
5. **Employees** - Employee information
6. **Departments** - Employee departments
7. **Sites** - Physical locations
8. **EmployeeQRCodes** - Employee QR codes
9. **VisitorQRCodes** - Visitor QR codes
10. **EmployeeScanLogs** - Employee attendance logs
11. **VisitorScanLogs** - Visitor scan logs
12. **AccessLogs** - Audit trail
13. **Alerts** - Security alerts

See `backend/database/schema.sql` for complete schema and [docs/DATA_DICTIONARY.md](docs/DATA_DICTIONARY.md) for detailed documentation.

---

## Security Features

- **JWT Authentication** - Secure token-based authentication (24-hour expiration)
- **Password Hashing** - SHA256 hashing for passwords
- **Input Validation** - Regex-based validation for CNIC, email, names
- **SQL Injection Prevention** - Parameterized queries throughout
- **CORS Configuration** - Controlled cross-origin access
- **Role-Based Access Control** - Admin and Security roles with endpoint-level protection
- **Audit Logging** - All actions logged to AccessLogs table

---

## Troubleshooting

### Backend Issues

**Database Connection Error:**
- Verify MySQL is running
- Check credentials in `backend/config/config.ini`
- Ensure database `Visitor_Management_System` exists

**Import Errors:**
- Verify all packages installed: `pip list`
- Reinstall: `pip install -r requirements.txt --force-reinstall`

**Port Already in Use:**
- Change port in `main.py` or kill process using port 8000

### Frontend Issues

**API Connection Error:**
- Verify backend is running
- Check `VITE_API_URL` in `.env`
- Check browser console for CORS errors

**Build Errors:**
- Clear node_modules: `rm -rf node_modules && npm install`
- Clear cache: `npm cache clean --force`

### Database Issues

**Schema Errors:**
- Ensure MySQL version is 8.0+
- Drop and recreate database if needed
- Check for existing conflicting tables

---

## Development

### Code Structure

- **Backend:** FastAPI with service layer pattern
- **Frontend:** React with Context API for state management
- **Database:** MySQL with parameterized queries
- **Authentication:** JWT tokens stored in localStorage

### Adding New Features

1. Backend: Add service function in `backend/services/`
2. Backend: Add endpoint in `backend/api/`
3. Frontend: Add page component in `frontend/src/pages/`
4. Frontend: Add route in `frontend/src/App.jsx`
5. Update documentation

---

## License

[Your License Here]

---

## Support

For detailed documentation, see the [docs/](docs/) folder.

For API documentation, visit `http://localhost:8000/docs` when the backend is running.

---

**Version 1.0.0 - Production Ready**
