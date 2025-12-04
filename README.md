# Visitor Management System – Phase 2 (Authentication)

Phase 1 **and** Phase 2:

1. **Phase 1:** Database schema, connection layer, configuration, and shared utilities.
2. **Phase 2:** Authentication service, FastAPI endpoints (`/auth/login`, `/auth/register-user`, `/auth/delete-user/{id}`), and a minimal FastAPI application you can start locally.

Later phases (visitor management, QR code features, frontend, etc.)

---

## Project Structure (Phase 1–2)

```
visitor_management_system/
├── backend/
│   ├── __init__.py
│   ├── config/
│   │   └── config.ini
│   ├── api/
│   │   ├── __init__.py
│   │   └── auth_api.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   └── schema.sql
│   ├── main.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── auth_service.py
│   └── utils/
│       ├── __init__.py
│       ├── auth_dependency.py
│       ├── db_logger.py
│       └── validator.py
├── requirements.txt
├── setup_database.sql
└── README.md
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

### 3. Configure Database Credentials

Edit `backend/config/config.ini` and set your MySQL connection parameters:

```ini
[database]
host = localhost
port = 3306
user = root
password = your_password
database = Visitor_Management_System
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

`requirements.txt` currently includes:
- `mysql-connector-python`
- `fastapi`
- `uvicorn`
- `pydantic`

### 5. Test the Database Connection

Use the `Database` class in `backend/database/connection.py` to open a connection and run queries:

```python
from backend.database.connection import Database

db = Database()
result = db.fetchone("SELECT COUNT(*) AS users FROM Users")
print(result)
```

---

## Running the Authentication API

1. Ensure the database is online and seeded (steps above).
2. Start the FastAPI application:

```bash
uvicorn backend.main:app --reload
```

This launches the API on `http://localhost:8000`.

### Endpoints

| Method | Endpoint                 | Description                                     |
| ------ | ------------------------ | ----------------------------------------------- |
| POST   | `/auth/login`            | Returns token + user info                       |
| POST   | `/auth/register-user`    | Admin-only user creation                        |
| DELETE | `/auth/delete-user/{id}` | Admin-only deletion (cannot delete yourself)    |

Authentication uses a simple bearer token: `Bearer <user_id>:<role>`.  
Use the `token` returned from `/auth/login` in the `Authorization` header for admin-only endpoints.

---

## Included Utilities & Services

### `backend/utils/validator.py`
- CNIC validation (format `XXXXX-XXXXXXX-X`)
- Contact number validation (basic length and character checks)
- Name validation (length + non-empty)
- Username/password validators for future use

### `backend/utils/db_logger.py`
- Inserts action logs into the `AccessLogs` table.
- Provides a reusable `log_action` helper that can be used by later services.

### `backend/utils/db_logger.py`
- Inserts action logs into the `AccessLogs` table.
- Provides a reusable `log_action` helper that can be used by later services.

### `backend/services/auth_service.py`
- Password hashing (SHA256)
- Login, register, delete operations
- Role lookups and action logging

---

## Next Steps (Beyond Phase 2)

Visitor management, QR code flows, scanning, logs/export, email notifications, and the React frontend.