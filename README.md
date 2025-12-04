# Visitor Management System – Phase 1

Phase 1:

1. **Database schema** that matches the required specification exactly.
2. **Database connection infrastructure** for connecting to MySQL.
3. **Configuration** files that store connection details in `config.ini`.
4. **Core utility helpers** (validation + database logging) used across future phases.

---

## Project Structure (Phase 1 Only)

```
visitor_management_system/
├── backend/
│   ├── __init__.py
│   ├── config/
│   │   └── config.ini
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   └── schema.sql
│   └── utils/
│       ├── __init__.py
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

### 5. Test the Database Connection

Use the `Database` class in `backend/database/connection.py` to open a connection and run queries:

```python
from backend.database.connection import Database

db = Database()
result = db.fetchone("SELECT COUNT(*) AS users FROM Users")
print(result)
```

---

## Included Utilities

### `backend/utils/validator.py`
- CNIC validation (format `XXXXX-XXXXXXX-X`)
- Contact number validation (basic length and character checks)
- Name validation (length + non-empty)
- Username/password validators for future use

### `backend/utils/db_logger.py`
- Inserts action logs into the `AccessLogs` table.
- Provides a reusable `log_action` helper that can be used by later services.

---

## Next Steps (Beyond Phase 1)

All higher-level layers—services, APIs, frontend, QR features, email