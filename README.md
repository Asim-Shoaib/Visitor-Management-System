## Visitor Management System – backend

Phase 5:

Current scope:

- Database schema and connection
- Basic authentication (users / roles)
- Visitor registration and lookup
- Visit management (create/update/active list)
- QR code generation (employee & visitor) with email delivery

---

## Project Structure

```
visitor_management_system/
├── backend/
│   ├── __init__.py
│   ├── config/
│   │   └── config.ini
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth_api.py
│   │   ├── visitor_api.py
│   │   ├── visit_api.py
│   │   └── qr_api.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   └── schema.sql
│   ├── main.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── visitor_service.py
│   │   ├── visit_service.py
│   │   └── qr_service.py
│   └── utils/
│       ├── __init__.py
│       ├── auth_dependency.py
│       ├── db_logger.py
│       └── validator.py
├── requirements.txt
├── setup_database.sql
├── README.md
└── backend/generated_qr/  (generated QR code images, gitignored)
```

---

## Getting Started

### 1. Create the Database & Tables

```bash
mysql -u root -p < backend/database/schema.sql
```

This script creates the `Visitor_Management_System` database and all required tables.

### 2. (Optional) Insert Seed Data

```bash
mysql -u root -p < setup_database.sql
```

This inserts the mandatory roles plus a sample admin user (`admin` / `admin123`) and placeholder records for departments, sites, and employees.

### 3. Configure Database Credentials and Email

Edit `backend/config/config.ini` and set your MySQL connection parameters and email settings:

```ini
[database]
host = localhost
port = 3306
user = root
password = your_password
database = Visitor_Management_System

[email]
smtp_server = smtp.gmail.com
smtp_port = 587
sender_email = your_email@gmail.com
sender_password = your_password

[app]
secret_key = your-secret-key-here
qr_code_expiry_hours = 24
```

**Note**: For Gmail, you may need to use an "App Password" instead of your regular password. Email functionality will be skipped if credentials are not configured.

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

`requirements.txt` currently includes:
- `mysql-connector-python`
- `fastapi`
- `uvicorn`
- `pydantic`
- `qrcode[pil]` (QR code generation)
- `email-validator` (email validation)

### 5. Test the Database Connection

Use the `Database` class in `backend/database/connection.py` to open a connection and run queries:

```python
from backend.database.connection import Database

db = Database()
result = db.fetchone("SELECT COUNT(*) AS users FROM Users")
print(result)
```

---

## Running the API

1. Ensure the database is online and seeded (steps above).
2. Start the FastAPI application:

```bash
uvicorn backend.main:app --reload
```

The server listens on `http://localhost:8000`.

---

## Implemented Features (Phase 1–5)

- **Database foundation (Phase 1)**
  - MySQL schema in `backend/database/schema.sql` (must not be modified).
  - Connection helper in `backend/database/connection.py`.
  - CNIC / username / password / name / contact validators in `backend/utils/validator.py`.
  - Access logging helper in `backend/utils/db_logger.py` (writes to `AccessLogs`).

- **Authentication system (Phase 2)**
  - Users & roles backed by `Users` and `Roles` tables.
  - Simple token format returned on login: `user_id:role`.
  - `Authorization: Bearer <user_id>:<role>` header is parsed by `backend/utils/auth_dependency.py`.
  - Auth actions logged into `AccessLogs` via `log_action`.
  - User deactivation (not deletion) preserves all records for audit purposes.

- **Visitor CRUD (Phase 3)**
  - Visitor registration and lookup mapped to `Visitors` table.
  - CNIC format enforced in code (`validator.validate_cnic`) and by DB `CHECK` constraint.
  - Duplicate `cnic` prevented via DB `UNIQUE` and pre-insert check.

- **Visit management (Phase 4)**
  - Visit creation mapped to `Visits`:
    - Validates `visitor_id` ∈ `Visitors`, `site_id` ∈ `Sites`.
    - `host_employee_id` is optional but, if provided, must exist in `Employees`.
    - New visits start with status `pending`.
  - Visit status updates enforce allowed transitions:
    - `pending → checked_in` (sets `checkin_time`).
    - `pending → denied` (no timestamps).
    - `checked_in → checked_out` (sets `checkout_time`).
  - Active visits query:
    - Returns `pending` and `checked_in` visits with joined visitor and site data.
  - All visit actions are logged to `AccessLogs` with the requesting `user_id`.

- **QR Code Management (Phase 5)**
  - Employee QR generation (permanent):
    - Maps to `EmployeeQRCodes` table.
    - QR codes stored as PNG files in `backend/generated_qr/`.
    - No expiry date (permanent QR codes).
    - Status defaults to `active`.
  - Visitor QR generation (temporary):
    - Maps to `VisitorQRCodes` table.
    - Linked to a valid `visit_id` from `Visits`.
    - Expiry date set based on `qr_code_expiry_hours` config (default 24 hours).
    - QR codes emailed as downloadable links (not base64/inline).
    - Status defaults to `active`.
  - QR code download:
    - Public endpoint to download visitor QR code images.
    - Validates QR code is active and not expired.
  - All QR generation actions logged to `AccessLogs`.

---

## API Endpoints (Phase 1–5)

- **Auth (`/auth`, Phase 2)**
  - `POST /auth/login`
  - `POST /auth/register-user` (admin only; requires `Authorization` header)
  - `PATCH /auth/deactivate-user/{user_id}` (admin only; requires `Authorization` header)
    - Deactivates a user while preserving all database records (Users and AccessLogs) for audit purposes.
    - Prevents self-deactivation.
    - Logs the deactivation action to `AccessLogs`.

- **Visitors (`/visitor`, Phase 3)**
  - `POST /visitor/add-visitor`
  - `GET /visitor/search-visitor?cnic=...` or `?visitor_id=...`

- **Visits (`/visit`, Phase 4)**
  - `POST /visit/create-visit`
    - Requires `Authorization: Bearer <user_id>:<role>`.
    - Body: `{ "visitor_id": int, "site_id": int, "purpose_details": str | null, "host_employee_id": int | null }`.
  - `PATCH /visit/update-status/{visit_id}`
    - Requires `Authorization: Bearer <user_id>:<role>`.
    - Body: `{ "status": "pending" | "checked_in" | "checked_out" | "denied" }`.
    - Enforces described status transition rules.
  - `GET /visit/active-visits`
    - Public read endpoint returning pending / checked-in visits with visitor + site info.

- **QR Codes (`/qr`, Phase 5)**
  - `POST /qr/generate-employee`
    - Requires `Authorization: Bearer <user_id>:<role>`.
    - Body: `{ "employee_id": int }`.
    - Returns `emp_qr_id`, `code_value`, `employee_id`, `employee_name`.
    - Generates permanent QR code for employee (no expiry).
  - `POST /qr/generate-visitor`
    - Requires `Authorization: Bearer <user_id>:<role>`.
    - Body: `{ "visit_id": int, "recipient_email": "email@example.com" }`.
    - Returns `visitor_qr_id`, `code_value`, `visit_id`, `visitor_name`, `download_url`, `expiry_date`, `email_sent`.
    - Generates temporary QR code for visitor visit (with expiry).
    - Emails QR code as downloadable link to recipient.
  - `GET /qr/download/{visitor_qr_id}`
    - Public endpoint (no authentication required).
    - Returns PNG image file of visitor QR code.
    - Validates QR code is active and not expired.

---

## Notes

- **Tokens**: auth endpoints still return a simple token in the form `user_id:role`. Pass it as a Bearer header for protected endpoints.
- **CNIC format**: Visitor endpoints use the `Visitors` table and expect CNIC in the database format `XXXXX-XXXXXXX-X`.
- **Schema**: `backend/database/schema.sql` defines all tables and must remain the single source of truth for the DB structure (no in-app schema changes).
- **User management**: Users are never deleted from the database. The `PATCH /auth/deactivate-user/{user_id}` endpoint deactivates users while preserving all records (Users and AccessLogs) for audit purposes.
- **QR codes**: QR code images are stored in `backend/generated_qr/` directory (gitignored). Employee QR codes are permanent (no expiry), while visitor QR codes have configurable expiry (default 24 hours). Visitor QR codes are emailed as downloadable links, not embedded as base64.
- **Email configuration**: Email functionality requires SMTP credentials in `config.ini`. If not configured, QR generation will succeed but email sending will be skipped (logged in response).

