# Visitor Management System – backend

Phase 3:

Current scope:

- Database schema and connection
- Basic authentication (users / roles)
- Visitor registration and lookup

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
│   │   └── visitor_api.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   └── schema.sql
│   ├── main.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   └── visitor_service.py
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

## Running the API

1. Ensure the database is online and seeded (steps above).
2. Start the FastAPI application:

```bash
uvicorn backend.main:app --reload
```

The server listens on `http://localhost:8000`.

Useful endpoints so far:

- `POST /auth/login`
- `POST /auth/register-user`
- `DELETE /auth/delete-user/{id}`
- `POST /visitor/add-visitor`
- `GET /visitor/search-visitor?cnic=...` or `?visitor_id=...`

---

## Notes

- Auth endpoints return a simple token in the form `user_id:role`. You can pass it as a Bearer header if needed later.
- Visitor endpoints use the `Visitors` table and expect CNIC in the database format `XXXXX-XXXXXXX-X`.

