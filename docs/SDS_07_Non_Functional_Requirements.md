# Software Design Specification (SDS)
## Document 7: Non-Functional Requirements

**Version:** 1.0.0  
**Date:** 2024  
**Project:** Visitor Management System

---

## 7.1 Security Requirements

### 7.1.1 Authentication

**Requirement:** JWT-based authentication for all protected endpoints.

**Implementation:**
- JWT tokens generated on login
- Tokens include user_id, username, role
- Token expiration: 24 hours
- Tokens validated on every protected request

**Location:**
- `backend/services/auth_service.py::login()`
- `backend/utils/jwt_utils.py`
- `backend/utils/auth_dependency.py::get_current_user_id()`

---

### 7.1.2 Authorization

**Requirement:** Role-based access control (RBAC).

**Roles:**
- **Admin**: Full system access
- **Security**: Limited access (visitor management, scanning, logs viewing)

**Implementation:**
- Role checked via `get_user_role()` function
- Admin-only endpoints return 403 if not admin
- Frontend hides admin-only menu items for security role

**Location:**
- `backend/services/auth_service.py::get_user_role()`
- All admin-only endpoints check role before processing

---

### 7.1.3 Password Security

**Requirement:** Passwords must be hashed before storage.

**Implementation:**
- SHA256 hashing algorithm
- Plaintext passwords never stored
- Password verification via hash comparison

**Location:**
- `backend/services/auth_service.py::hash_password()`

**Note:** SHA256 is used. Consider upgrading to bcrypt or Argon2 for production.

---

### 7.1.4 SQL Injection Prevention

**Requirement:** All database queries must use parameterized queries.

**Implementation:**
- All queries use `%s` placeholders
- Parameters passed as tuples
- No string concatenation in SQL

**Location:**
- `backend/database/connection.py`
- All service functions use parameterized queries

---

### 7.1.5 Input Validation

**Requirement:** All user inputs must be validated.

**Implementation:**
- Pydantic models for request validation
- Custom validators for CNIC, email, IDs
- Frontend validation mirrors backend

**Location:**
- `backend/utils/validator.py`
- Pydantic models in all API files
- Frontend form validation

---

### 7.1.6 CORS Configuration

**Requirement:** Cross-Origin Resource Sharing must be configured.

**Current Implementation:**
- Allows all origins (`*`)
- Allows all methods
- Allows all headers

**Production Recommendation:**
- Restrict to specific frontend domain
- Limit allowed methods
- Limit allowed headers

**Location:**
- `backend/main.py`

---

## 7.2 Performance Requirements

### 7.2.1 Response Time

**Requirement:** API endpoints should respond within reasonable time.

**Expected Performance:**
- Simple queries: < 100ms
- Complex queries: < 500ms
- QR generation: < 1s
- Excel export: < 2s

**Current Implementation:**
- Synchronous operations
- No caching layer
- Direct database queries

**Optimization Opportunities:**
- Add caching for frequently accessed data
- Optimize database queries with indexes
- Implement async operations for long-running tasks

---

### 7.2.2 Throughput

**Requirement:** System should handle concurrent users.

**Expected Capacity:**
- 10-50 concurrent users (current design)
- 100+ API requests per minute

**Current Implementation:**
- Single-threaded FastAPI (can use async)
- Single database connection
- No connection pooling

**Scalability Considerations:**
- Implement connection pooling
- Use async/await for I/O operations
- Add load balancing for multiple instances

---

### 7.2.3 Database Performance

**Requirement:** Database queries should be optimized.

**Current Implementation:**
- Indexes on primary keys and foreign keys
- Indexes on frequently queried fields (cnic, username)
- No query optimization beyond indexes

**Optimization Opportunities:**
- Add composite indexes for common query patterns
- Analyze slow queries
- Implement query result caching

---

## 7.3 Reliability Requirements

### 7.3.1 System Availability

**Requirement:** System should be available during business hours.

**Expected Uptime:**
- 95% uptime (business hours)
- Graceful error handling
- No data loss on errors

**Current Implementation:**
- Error handling in all endpoints
- Database transactions (implicit)
- Logging for error tracking

---

### 7.3.2 Error Handling

**Requirement:** All errors must be handled gracefully.

**Implementation:**
- Try-catch blocks in service functions
- HTTP exception handling in API endpoints
- User-friendly error messages
- Error logging to AccessLogs

**Location:**
- All service functions
- All API endpoints
- `backend/utils/db_logger.py`

---

### 7.3.3 Data Integrity

**Requirement:** Database integrity must be maintained.

**Implementation:**
- Foreign key constraints
- Unique constraints
- NOT NULL constraints
- CHECK constraints (CNIC format)

**Location:**
- `backend/database/schema.sql`

---

## 7.4 Scalability Requirements

### 7.4.1 Horizontal Scalability

**Current Limitation:**
- Single database connection
- File-based QR storage (not shared)
- No session management (stateless JWT)

**Scalability Considerations:**
- Multiple backend instances can share database
- QR files should be stored in shared storage (S3, NFS)
- Stateless design supports horizontal scaling

---

### 7.4.2 Vertical Scalability

**Current Design:**
- Single-threaded (can use async)
- No connection pooling
- In-memory processing

**Scalability Options:**
- Increase server resources
- Implement async operations
- Add connection pooling
- Optimize database queries

---

## 7.5 Maintainability Requirements

### 7.5.1 Code Organization

**Requirement:** Code must be modular and well-organized.

**Implementation:**
- Separation of concerns (API, Service, Database layers)
- Service functions for business logic
- Utility functions for reusable code
- Clear file structure

**Structure:**
```
backend/
├── api/          # API endpoints
├── services/     # Business logic
├── utils/        # Utilities
├── database/     # Database connection
└── config/       # Configuration
```

---

### 7.5.2 Documentation

**Requirement:** Code must be documented.

**Implementation:**
- Function docstrings
- API endpoint descriptions
- README files
- SDS documentation

**Location:**
- All service functions have docstrings
- All API endpoints have descriptions
- `docs/` folder contains comprehensive documentation

---

### 7.5.3 Logging

**Requirement:** System actions must be logged.

**Implementation:**
- AccessLogs table for all actions
- User tracking for operations
- Action type and details logged
- Timestamp recording

**Location:**
- `backend/utils/db_logger.py::log_action()`
- Called from all service functions

---

## 7.6 Usability Requirements

### 7.6.1 User Interface

**Requirement:** UI must be intuitive and user-friendly.

**Implementation:**
- Clear navigation menu
- Form validation with error messages
- Toast notifications for feedback
- Loading states during operations
- Responsive design

**Location:**
- `frontend/src/pages/*.jsx`
- `frontend/src/components/Layout.jsx`

---

### 7.6.2 Error Messages

**Requirement:** Error messages must be clear and actionable.

**Implementation:**
- User-friendly error messages
- Toast notifications for errors
- Inline validation errors
- HTTP error details in responses

**Location:**
- All API endpoints return descriptive error messages
- Frontend displays user-friendly messages

---

## 7.7 Portability Requirements

### 7.7.1 Operating System

**Requirement:** System must run on multiple operating systems.

**Supported Platforms:**
- Windows 10/11
- Linux (Ubuntu, CentOS, etc.)
- macOS

**Implementation:**
- Python and Node.js are cross-platform
- No OS-specific code
- Configuration via files (not registry)

---

### 7.7.2 Database

**Requirement:** Database must be portable.

**Current Limitation:**
- MySQL-specific features used
- ENUM types
- CHECK constraints

**Portability Considerations:**
- Migration to PostgreSQL would require schema changes
- Migration to SQLite not recommended (concurrent access)

---

## 7.8 Compatibility Requirements

### 7.8.1 Browser Compatibility

**Requirement:** Frontend must work on modern browsers.

**Supported Browsers:**
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Features Used:**
- ES6+ JavaScript
- Fetch API
- LocalStorage
- getUserMedia API

---

### 7.8.2 Python Version

**Requirement:** Backend must work with Python 3.8+.

**Implementation:**
- Python 3.8+ syntax
- Type hints (Python 3.5+)
- f-strings (Python 3.6+)

---

### 7.8.3 Node.js Version

**Requirement:** Frontend must work with Node.js 18+.

**Implementation:**
- Node.js 18+ features
- npm package manager
- Vite build tool

---

## 7.9 Audit Requirements

### 7.9.1 Audit Logging

**Requirement:** All system actions must be logged.

**Implementation:**
- AccessLogs table stores all actions
- User ID, action type, details, timestamp
- No deletion of audit logs
- Export capability for audit logs

**Location:**
- `backend/utils/db_logger.py`
- `backend/services/logs_service.py`

---

### 7.9.2 Data Retention

**Requirement:** Audit logs must be retained.

**Current Implementation:**
- No automatic deletion
- Manual cleanup may be required
- Export functionality for archiving

**Recommendation:**
- Implement archival strategy
- Regular exports for long-term storage
- Database cleanup for old logs (if needed)

---

## 7.10 Backup and Recovery

### 7.10.1 Data Backup

**Requirement:** Database must be backed up regularly.

**Current Implementation:**
- No automatic backup
- Manual backup via MySQL tools

**Recommendation:**
- Implement automated daily backups
- Store backups off-site
- Test backup restoration

---

### 7.10.2 File Backup

**Requirement:** QR code files should be backed up.

**Current Implementation:**
- QR files stored in `backend/generated_qr/`
- No automatic backup

**Recommendation:**
- Include QR directory in backup
- Or use cloud storage (S3) for QR files

---

**End of Document 7: Non-Functional Requirements**

