# Software Design Specification (SDS)
## Document 6: External Interface Design

**Version:** 1.0.0  
**Date:** 2024  
**Project:** Visitor Management System

---

## 6.1 External Dependencies

### 6.1.1 Camera Device

**Type:** Web Camera (USB or built-in)

**Interface:** HTML5 MediaDevices API (getUserMedia)

**Library:** html5-qrcode (JavaScript)

**Usage:**
- QR code scanning in browser
- Real-time video feed
- QR code detection and decoding

**Requirements:**
- Browser support for getUserMedia API
- HTTPS in production (required for camera access)
- User permission granted

**Implementation:**
- Located in `frontend/src/pages/CheckInOut.jsx`
- Requests camera permission on page load
- Supports multiple camera selection
- Handles camera errors gracefully

**Constraints:**
- Single camera device per security station
- Camera must be accessible via browser
- Requires user interaction to grant permission

---

### 6.1.2 SMTP Email Service

**Type:** SMTP Server

**Protocol:** SMTP (Simple Mail Transfer Protocol)

**Configuration:** Via `backend/config/config.ini`

**Settings:**
- SMTP server address (e.g., smtp.gmail.com)
- SMTP port (587 for TLS, 465 for SSL)
- Sender email address
- Sender password (or app password)

**Usage:**
- QR code delivery to visitors
- Late arrival alerts to employees
- Email notifications

**Implementation:**
- Located in `backend/services/qr_service.py` and `backend/services/email_service.py`
- Uses Python `smtplib` library
- Sends HTML emails with download links
- Handles email errors gracefully

**Supported Providers:**
- Gmail (with App Password)
- Outlook/Office 365
- Custom SMTP servers

**Constraints:**
- Requires valid SMTP credentials
- Email delivery not guaranteed (depends on provider)
- Rate limiting may apply

---

### 6.1.3 QR Code Library

**Backend Library:** qrcode (Python)

**Package:** qrcode[pil] 7.4.2

**Usage:**
- QR code image generation
- Error correction level: L (Low)
- Box size: 10 pixels
- Border: 4 modules

**Implementation:**
- Located in `backend/services/qr_service.py::_generate_qr_code_image()`
- Generates PNG images
- Saves to `backend/generated_qr/` directory

**Frontend Library:** qrcode.react (React component)

**Package:** qrcode.react 3.1.0

**Usage:**
- Display QR codes in browser
- Read-only display

**Implementation:**
- Located in `frontend/src/pages/EmployeeQR.jsx`
- Displays generated QR codes

**Constraints:**
- QR code data must be valid string
- File system write permissions required for backend
- QR code images stored on server (not in database)

---

### 6.1.4 Browser Camera API

**API:** MediaDevices.getUserMedia()

**Standard:** W3C Media Capture and Streams API

**Usage:**
- Access camera stream
- Capture video frames
- QR code scanning

**Library:** html5-qrcode 2.3.8

**Implementation:**
- Located in `frontend/src/pages/CheckInOut.jsx`
- Requests camera permission
- Initializes scanner with camera stream
- Processes QR code detection

**Browser Support:**
- Chrome 53+
- Firefox 36+
- Safari 11+
- Edge 12+

**Constraints:**
- Requires HTTPS in production
- User permission required
- Single camera stream per page
- May not work on all devices

---

## 6.2 REST API Endpoints

### 6.2.1 Protocol

**Protocol:** HTTP/HTTPS

**Data Format:** JSON (JavaScript Object Notation)

**Content-Type:** `application/json`

**Authentication:** JWT Bearer tokens in Authorization header

**Base URL:** Configurable via environment variable (default: `http://localhost:8000`)

---

### 6.2.2 Request Format

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Body (for POST/PATCH):**
```json
{
  "field1": "value1",
  "field2": "value2"
}
```

**Query Parameters (for GET):**
```
?param1=value1&param2=value2
```

**Path Parameters:**
```
/resource/{id}
```

---

### 6.2.3 Response Format

**Success Response (200):**
```json
{
  "field1": "value1",
  "field2": "value2"
}
```

**Error Response (4xx/5xx):**
```json
{
  "detail": "Error message"
}
```

**Status Codes:**
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 422: Unprocessable Entity
- 500: Internal Server Error

---

### 6.2.4 API Endpoints

See `docs/SDS_04_Detailed_Design.md` Section 4.2 for complete API endpoint documentation.

**Endpoint Categories:**
- Authentication (`/auth/*`)
- Visitors (`/visitor/*`)
- Visits (`/visit/*`)
- QR Codes (`/qr/*`)
- Scanning (`/scan/*`)
- Sites/Employees (`/site/*`)
- Logs (`/logs/*`)
- Alerts (`/alert/*`)
- Users (`/users/*`)
- Attendance (`/attendance/*`)

---

## 6.3 Database Interface

### 6.3.1 Database Protocol

**Type:** MySQL 8.0+

**Protocol:** MySQL Protocol

**Driver:** mysql-connector-python 8.2.0

**Connection:** Persistent connection via Database class

**Connection Pooling:** Single connection (not pooled)

---

### 6.3.2 Query Method

**Type:** Parameterized queries

**Format:**
```python
db.execute("SELECT * FROM Table WHERE id = %s", (id_value,))
db.fetchone("SELECT * FROM Table WHERE id = %s", (id_value,))
db.fetchall("SELECT * FROM Table WHERE id = %s", (id_value,))
```

**Benefits:**
- SQL injection prevention
- Type safety
- Automatic escaping

---

### 6.3.3 Transaction Management

**Current Implementation:**
- No explicit transaction management
- Each query executes independently
- Auto-commit mode

**Future Consideration:**
- Implement transactions for multi-step operations
- Rollback on errors

---

## 6.4 File System Interface

### 6.4.1 QR Code Storage

**Directory:** `backend/generated_qr/`

**File Format:** PNG images

**Naming Convention:**
- Employee QR: `emp_{emp_qr_id}.png`
- Visitor QR: `visitor_{visitor_qr_id}.png`

**Permissions:**
- Write permission required
- Read permission for download endpoint

**Implementation:**
- Directory created automatically if not exists
- Files stored on server filesystem
- Not stored in database (only file path)

---

### 6.4.2 Excel Export Files

**Format:** Excel (.xlsx)

**Library:** openpyxl 3.1.2

**Generation:**
- Created in memory (BytesIO)
- Streamed directly to HTTP response
- Not saved to filesystem

**Implementation:**
- Located in `backend/services/logs_service.py` and `backend/services/site_service.py`
- Generated on-demand
- Includes formatting and styling

---

## 6.5 HTTP Protocols

### 6.5.1 CORS (Cross-Origin Resource Sharing)

**Current Configuration:**
- Allows all origins (`*`)
- Allows all methods (GET, POST, PUT, DELETE, PATCH)
- Allows all headers

**Location:** `backend/main.py`

**Production Recommendation:**
- Restrict to specific frontend domain
- Limit allowed methods
- Limit allowed headers

---

### 6.5.2 Content Security

**HTTPS:**
- Required in production for camera access
- Recommended for all environments
- JWT tokens transmitted over HTTPS

**Token Security:**
- Tokens stored in localStorage (frontend)
- Tokens sent in Authorization header
- Tokens expire after 24 hours

---

## 6.6 Integration Points

### 6.6.1 Frontend-Backend Integration

**Protocol:** HTTP/REST

**Data Format:** JSON

**Base URL:** Configurable via `VITE_API_URL` environment variable

**Authentication:** JWT Bearer tokens

**Error Handling:**
- Network errors caught and displayed
- 401 errors trigger logout
- Other errors displayed as toast notifications

---

### 6.6.2 Backend-Database Integration

**Protocol:** MySQL Protocol

**Connection:** Persistent via Database class

**Query Execution:**
- Synchronous queries
- Parameterized for security
- Error handling for connection failures

---

### 6.6.3 Email Integration

**Protocol:** SMTP

**Library:** Python smtplib (standard library)

**Configuration:** Via config.ini

**Usage:**
- QR code delivery
- Late arrival alerts
- Error handling for email failures

---

## 6.7 External Service Dependencies

### 6.7.1 Email Service Provider

**Dependencies:**
- SMTP server availability
- Valid email credentials
- Network connectivity

**Failure Handling:**
- Email errors logged
- QR code generation continues even if email fails
- User notified of email status

---

### 6.7.2 Browser APIs

**Dependencies:**
- getUserMedia API support
- LocalStorage support
- Fetch API support
- Modern JavaScript features (ES6+)

**Fallback:**
- Manual QR code entry if camera unavailable
- Error messages for unsupported browsers

---

## 6.8 Data Exchange Formats

### 6.8.1 JSON

**Usage:** All API requests and responses

**Encoding:** UTF-8

**Structure:**
- Objects: `{ "key": "value" }`
- Arrays: `[ "item1", "item2" ]`
- Nested structures supported

---

### 6.8.2 Multipart Form Data

**Usage:** Not currently used (all data sent as JSON)

**Future Consideration:**
- File uploads (if implemented)
- Image uploads (if implemented)

---

### 6.8.3 Binary Data

**Usage:**
- QR code image downloads (PNG)
- Excel file exports (.xlsx)

**Content-Type:**
- PNG: `image/png`
- Excel: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`

**Delivery:**
- Direct file download
- Content-Disposition header for filename

---

**End of Document 6: External Interface Design**

