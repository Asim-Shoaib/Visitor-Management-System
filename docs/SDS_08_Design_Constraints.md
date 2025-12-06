# Software Design Specification (SDS)
## Document 8: Design Constraints

**Version:** 1.0.0  
**Date:** 2024  
**Project:** Visitor Management System

---

## 8.1 Database Constraints

### 8.1.1 Schema Immutability

**Constraint:** Database schema must not be modified.

**Rationale:**
- Existing database structure must be preserved
- No new tables or fields can be added
- All features must use existing schema

**Impact:**
- New features must work within existing table structure
- No schema migrations allowed
- Data must fit existing field types and constraints

**Location:**
- `backend/database/schema.sql` defines the schema
- All features use only existing tables and fields

---

### 8.1.2 Foreign Key Constraints

**Constraint:** All foreign key relationships are enforced at database level.

**Impact:**
- Cannot delete records with dependent records
- Must maintain referential integrity
- Cascading deletes not implemented (manual handling required)

**Example:**
- Cannot delete Employee if EmployeeQRCodes exist
- Cannot delete Visitor if Visits exist
- Cannot delete Visit if VisitorQRCodes exist

---

### 8.1.3 Unique Constraints

**Constraint:** Unique fields must remain unique.

**Enforced Fields:**
- `Users.username` - UNIQUE
- `Visitors.cnic` - UNIQUE
- `Sites.site_name` - UNIQUE
- `Departments.name` - UNIQUE
- `EmployeeQRCodes.code_value` - UNIQUE
- `VisitorQRCodes.code_value` - UNIQUE

**Impact:**
- Duplicate usernames rejected
- Duplicate CNICs rejected
- Duplicate site names rejected
- Application must handle uniqueness violations

---

### 8.1.4 Data Type Constraints

**Constraint:** Field data types are fixed.

**Examples:**
- `hourly_rate` is DECIMAL(10,2) - cannot store more than 2 decimal places
- `cnic` is VARCHAR(15) - limited to 15 characters
- `status` is ENUM - only specific values allowed

**Impact:**
- Data must fit within type constraints
- Validation must ensure data fits types
- ENUM values cannot be changed without schema modification

---

## 8.2 Functional Constraints

### 8.2.1 QR-Only Check-In Flow

**Constraint:** Visitors and employees must use QR codes for check-in/check-out.

**Rationale:**
- System designed for QR-based access control
- No manual entry option for check-in/check-out
- QR codes provide security and tracking

**Impact:**
- Visitors must have QR code to enter
- Employees must have QR code for attendance
- No alternative check-in methods
- QR code generation required before access

---

### 8.2.2 Single Camera Device

**Constraint:** QR scanning assumes one camera device per security station.

**Rationale:**
- Typical deployment has one camera per entry point
- Multiple cameras add complexity
- Current implementation supports camera selection but assumes single active camera

**Impact:**
- Security personnel use one camera at a time
- Camera switching requires user interaction
- No simultaneous multi-camera scanning

---

### 8.2.3 Email Delivery Requirement

**Constraint:** Visitor QR codes are delivered via email only.

**Rationale:**
- Email is primary delivery method
- No SMS or other delivery methods
- Email must be provided during visit creation

**Impact:**
- Visitors must have valid email address
- Email delivery failure prevents QR access
- System requires functional SMTP configuration

---

### 8.2.4 Admin-Only System Changes

**Constraint:** Certain operations restricted to admin role.

**Restricted Operations:**
- User creation
- User deactivation
- Employee creation
- Site creation
- Salary calculation
- Salary export

**Rationale:**
- Security and access control
- Prevents unauthorized system modifications
- Maintains audit trail integrity

**Impact:**
- Security role cannot perform admin operations
- Admin role required for system management
- Role checks enforced at API and frontend levels

---

## 8.3 Technical Constraints

### 8.3.1 JWT Token Expiration

**Constraint:** JWT tokens expire after 24 hours.

**Rationale:**
- Security best practice
- Limits token lifetime
- Forces periodic re-authentication

**Impact:**
- Users must re-login after 24 hours
- Tokens cannot be refreshed (must re-authenticate)
- Frontend must handle token expiration

**Location:**
- `backend/utils/jwt_utils.py`
- Token expiration set to 24 hours

---

### 8.3.2 QR Code Expiry

**Constraint:** Visitor QR codes expire after 24 hours.

**Rationale:**
- Security measure
- Prevents reuse of old QR codes
- Limits access window

**Impact:**
- Visitors must use QR code within 24 hours
- Expired QR codes rejected
- New QR code required for extended visits

**Location:**
- `backend/services/qr_service.py::generate_visitor_qr()`
- Expiry set to 24 hours from generation

---

### 8.3.3 File System Storage

**Constraint:** QR code images stored in file system, not database.

**Rationale:**
- Database not optimized for binary data
- File system more efficient for images
- Easier file serving

**Impact:**
- Requires file system write permissions
- QR files must be backed up separately
- File paths stored in database, not files themselves
- Directory structure must be maintained

**Location:**
- `backend/generated_qr/` directory
- Files named `emp_{id}.png` and `visitor_{id}.png`

---

### 8.3.4 Browser Camera Requirements

**Constraint:** QR scanning requires browser camera permission and HTTPS in production.

**Rationale:**
- Browser security policy
- getUserMedia API requires HTTPS
- User permission required for privacy

**Impact:**
- Production deployment must use HTTPS
- Users must grant camera permission
- Some browsers may block camera access
- Fallback to manual QR entry if camera unavailable

**Location:**
- `frontend/src/pages/CheckInOut.jsx`
- Uses html5-qrcode library with getUserMedia

---

## 8.4 Business Constraints

### 8.4.1 CNIC Format

**Constraint:** CNIC must follow format XXXXX-XXXXXXX-X.

**Rationale:**
- Pakistani CNIC format standard
- Database CHECK constraint enforces format
- Application validation mirrors constraint

**Impact:**
- Invalid CNIC formats rejected
- Format validation at database and application levels
- No flexibility in format

**Location:**
- `backend/database/schema.sql` - CHECK constraint
- `backend/utils/validator.py::validate_cnic()`

---

### 8.4.2 Late Arrival Threshold

**Constraint:** Late arrival threshold fixed at 9:10 AM.

**Rationale:**
- Business rule
- Hardcoded in application
- Cannot be configured without code change

**Impact:**
- Any check-in after 9:10 AM considered late
- Threshold cannot be adjusted per employee or department
- Change requires code modification

**Location:**
- `backend/services/scan_service.py`
- `LATE_THRESHOLD_TIME = time(9, 10, 0)`

---

### 8.4.3 Late Alert Threshold

**Constraint:** Late alert triggered at 3+ late arrivals in 30 days.

**Rationale:**
- Business rule for attendance management
- Hardcoded in application
- Cannot be configured without code change

**Impact:**
- Alert sent after 3rd late arrival in 30-day window
- Threshold cannot be adjusted
- Change requires code modification

**Location:**
- `backend/services/scan_service.py::scan_employee_qr()`
- Checks `late_count >= 3`

---

### 8.4.4 Active Visit Limit

**Constraint:** Visitor cannot have multiple active visits simultaneously.

**Rationale:**
- Prevents duplicate visit records
- Ensures accurate tracking
- Business logic requirement

**Impact:**
- Visitor must complete or cancel visit before new visit
- System checks for active visits before creating new one
- Prevents data inconsistency

**Location:**
- `backend/services/visit_service.py::create_visit()`
- Checks for existing pending/checked_in visits

---

## 8.5 Performance Constraints

### 8.5.1 Access Log Limit

**Constraint:** Access logs query returns up to 1000 most recent records.

**Rationale:**
- Performance optimization
- Prevents large result sets
- UI cannot display unlimited records

**Impact:**
- Older logs may not be visible in UI
- Export functionality for full log access
- Pagination not implemented (future enhancement)

**Location:**
- `backend/services/logs_service.py::get_access_logs()`
- Query includes `LIMIT 1000`

---

### 8.5.2 Synchronous Operations

**Constraint:** Email sending and QR generation are synchronous.

**Rationale:**
- Simplicity of implementation
- Immediate feedback to user
- No background job queue

**Impact:**
- API requests may block on email/QR generation
- User must wait for operation to complete
- No async processing

**Location:**
- `backend/services/qr_service.py`
- `backend/services/email_service.py`
- All operations synchronous

---

### 8.5.3 No Caching

**Constraint:** Currently no caching layer implemented.

**Rationale:**
- Simplicity of implementation
- Direct database queries
- No cache invalidation complexity

**Impact:**
- All queries hit database
- No performance optimization from caching
- Data always fresh (no stale cache)

**Location:**
- All service functions query database directly
- No caching middleware

---

## 8.6 Security Constraints

### 8.6.1 Password Hashing Algorithm

**Constraint:** SHA256 hashing used (not bcrypt/Argon2).

**Rationale:**
- Existing implementation
- Schema change would be required for longer hashes
- Current implementation sufficient for basic security

**Impact:**
- Less secure than modern hashing algorithms
- Consider upgrading for production
- Migration would require password reset for all users

**Location:**
- `backend/services/auth_service.py::hash_password()`
- Uses SHA256

---

### 8.6.2 CORS Configuration

**Constraint:** Currently allows all origins (`*`).

**Rationale:**
- Development convenience
- Not restricted for testing
- Should be restricted in production

**Impact:**
- Any origin can access API
- Security risk in production
- Should be restricted to frontend domain

**Location:**
- `backend/main.py`
- CORS middleware configuration

---

### 8.6.3 Secret Key Management

**Constraint:** JWT secret key stored in config file.

**Rationale:**
- Simple configuration
- File-based configuration
- Must be changed from default in production

**Impact:**
- Secret key must be protected
- Config file should not be in version control
- Should use environment variables in production

**Location:**
- `backend/config/config.ini`
- `[app] secret_key` setting

---

### 8.6.4 No Rate Limiting

**Constraint:** Currently no rate limiting on API endpoints.

**Rationale:**
- Simplicity of implementation
- Not required for small deployments
- Can be added if needed

**Impact:**
- Vulnerable to brute force attacks
- No protection against API abuse
- Should be implemented for production

**Location:**
- No rate limiting middleware
- All endpoints accessible without limits

---

## 8.7 Integration Constraints

### 8.7.1 SMTP Provider Limitations

**Constraint:** Email delivery depends on SMTP provider.

**Limitations:**
- Gmail requires App Password (not regular password)
- Rate limiting may apply
- Delivery not guaranteed
- Provider-specific configuration

**Impact:**
- Must configure SMTP correctly
- Email delivery may fail
- Provider-specific issues may occur

**Location:**
- `backend/config/config.ini`
- `[email]` section

---

### 8.7.2 Browser Compatibility

**Constraint:** Requires modern browser with camera API support.

**Limitations:**
- Older browsers may not support getUserMedia
- Some browsers require HTTPS
- Mobile browsers may have different behavior

**Impact:**
- Not all browsers supported
- Fallback to manual QR entry
- Browser-specific issues may occur

**Location:**
- `frontend/src/pages/CheckInOut.jsx`
- html5-qrcode library requirements

---

## 8.8 Deployment Constraints

### 8.8.1 Single Server Deployment

**Constraint:** Current design assumes single server deployment.

**Limitations:**
- QR files stored on server filesystem
- Single database connection
- No load balancing support

**Impact:**
- Horizontal scaling requires shared storage
- Multiple instances need shared filesystem
- Database connection pooling needed for multiple instances

---

### 8.8.2 Environment Configuration

**Constraint:** Configuration via config file, not environment variables.

**Rationale:**
- Simple file-based configuration
- Easy to modify
- Not ideal for containerized deployments

**Impact:**
- Config file must be present
- Not suitable for 12-factor app pattern
- Should use environment variables in production

**Location:**
- `backend/config/config.ini`
- Loaded via configparser

---

**End of Document 8: Design Constraints**

