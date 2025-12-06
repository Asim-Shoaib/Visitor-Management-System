# Setup and Installation Guide

## Prerequisites

### Required Software

1. **Python 3.8+**
   - Download from: https://www.python.org/downloads/
   - Verify installation: `python --version`

2. **Node.js 18+ and npm**
   - Download from: https://nodejs.org/
   - Verify installation: `node --version` and `npm --version`

3. **MySQL 8.0+**
   - Download from: https://dev.mysql.com/downloads/mysql/
   - Verify installation: `mysql --version`

4. **Git** (optional, for cloning repository)
   - Download from: https://git-scm.com/downloads

---

## Backend Setup

### 1. Install Python Dependencies

Navigate to the project root directory:

```bash
pip install -r requirements.txt
```

**Required packages:**
- `mysql-connector-python` - MySQL database connector
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `qrcode[pil]` - QR code generation
- `PyJWT` - JWT token handling
- `openpyxl` - Excel file generation
- `email-validator` - Email validation

### 2. Database Configuration

#### Create Database

1. Start MySQL server
2. Open MySQL command line or MySQL Workbench
3. Run the schema file:

```bash
mysql -u root -p < backend/database/schema.sql
```

Or manually execute the SQL in `backend/database/schema.sql`

#### Initialize Database

Run the setup script:

```bash
mysql -u root -p < setup_database.sql
```

This will:
- Insert default roles (admin, security)
- Create default admin user (username: `admin`, password: `admin123`)
- Insert sample department and site

### 3. Configure Backend

Edit `backend/config/config.ini`:

```ini
[database]
host = localhost
port = 3306
user = root
password = your_mysql_password
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

**Important Notes:**
- Change `secret_key` to a secure random string for production
- For Gmail, use an App Password (not your regular password)
- Update `base_url` for production deployment

### 4. Create QR Code Directory

Create the directory for storing QR code images:

```bash
mkdir backend/generated_qr
```

Or the system will create it automatically on first QR generation.

### 5. Run Backend

**Development mode:**
```bash
cd backend
python main.py
```

Or using uvicorn directly:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`

**Verify backend:**
- Health check: `http://localhost:8000/health`
- API docs: `http://localhost:8000/docs`

---

## Frontend Setup

### 1. Install Node Dependencies

Navigate to the frontend directory:

```bash
cd frontend
npm install
```

**Required packages:**
- `react` - UI framework
- `react-dom` - React DOM renderer
- `react-router-dom` - Client-side routing
- `axios` - HTTP client
- `react-toastify` - Toast notifications
- `qrcode.react` - QR code display component
- `html5-qrcode` - QR code scanner

### 2. Configure Frontend

Create `.env` file in `frontend/` directory (optional):

```env
VITE_API_URL=http://localhost:8000
```

If not set, defaults to `http://localhost:8000`

### 3. Run Frontend

**Development mode:**
```bash
npm run dev
```

Frontend will be available at: `http://localhost:3000`

**Build for production:**
```bash
npm run build
```

This creates a `dist/` folder with production build.

---

## Full Stack Setup (Production)

### 1. Build Frontend

```bash
cd frontend
npm run build
```

### 2. Copy Frontend Build to Backend

```bash
# Windows
xcopy /E /I frontend\dist backend\static

# Linux/Mac
cp -r frontend/dist/* backend/static/
```

### 3. Run Backend (Serves Frontend)

```bash
cd backend
python main.py
```

Now the backend serves both API and frontend from `http://localhost:8000`

---

## Verification

### 1. Backend Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy"}
```

### 2. Database Connection

Check backend logs for "Connected to MySQL successfully" (if logging enabled).

### 3. Frontend Access

Open browser: `http://localhost:3000` (dev) or `http://localhost:8000` (production)

### 4. Login Test

- Username: `admin`
- Password: `admin123`

---

## Troubleshooting

### Backend Issues

**Database Connection Error:**
- Verify MySQL is running
- Check `config.ini` database credentials
- Ensure database `Visitor_Management_System` exists

**Import Errors:**
- Verify all packages installed: `pip list`
- Reinstall requirements: `pip install -r requirements.txt --force-reinstall`

**Port Already in Use:**
- Change port in `main.py` or kill process using port 8000
- Windows: `netstat -ano | findstr :8000`
- Linux/Mac: `lsof -i :8000`

### Frontend Issues

**API Connection Error:**
- Verify backend is running
- Check `VITE_API_URL` in `.env` file
- Check browser console for CORS errors

**Build Errors:**
- Clear node_modules: `rm -rf node_modules && npm install`
- Clear cache: `npm cache clean --force`

**Port Already in Use:**
- Change port in `vite.config.js` or kill process using port 3000

### Database Issues

**Schema Errors:**
- Ensure MySQL version is 8.0+
- Check for existing tables that might conflict
- Drop database and recreate: `DROP DATABASE Visitor_Management_System;`

**Permission Errors:**
- Verify MySQL user has CREATE, INSERT, UPDATE, DELETE, SELECT permissions
- Check MySQL user privileges

---

## Development Workflow

### Backend Development

1. Make changes to Python files
2. Backend auto-reloads (if using `--reload` flag)
3. Test endpoints via `http://localhost:8000/docs`

### Frontend Development

1. Make changes to React files
2. Frontend auto-reloads with Hot Module Replacement (HMR)
3. Test in browser at `http://localhost:3000`

### Database Changes

1. Update `backend/database/schema.sql`
2. Apply changes manually or via migration script
3. **Note:** Do not modify schema in production without backup

---

## Production Deployment

See `docs/DEPLOYMENT.md` for detailed production deployment instructions.

**Quick Production Setup:**

1. Set environment-specific config in `config.ini`
2. Change `secret_key` to secure random string
3. Update CORS origins in `main.py` (restrict to your domain)
4. Build frontend: `npm run build`
5. Copy build to `backend/static/`
6. Use production WSGI server (gunicorn, uvicorn workers)
7. Set up reverse proxy (Nginx)
8. Configure SSL/TLS

---

## Default Credentials

**Initial Admin User:**
- Username: `admin`
- Password: `admin123`

**⚠️ IMPORTANT:** Change default password immediately after first login in production!

---

## Next Steps

1. **Change Default Password:** Login and update admin password
2. **Configure Email:** Update SMTP settings in `config.ini`
3. **Add Departments:** Create departments via admin panel
4. **Add Sites:** Create sites via admin panel
5. **Create Users:** Add security personnel via User Management
6. **Create Employees:** Add employees via Employee Management
7. **Generate QR Codes:** Generate employee QR codes for attendance

---

## Additional Resources

- API Documentation: `docs/API_REFERENCE.md`
- System Overview: `docs/SYSTEM_OVERVIEW.md`
- Deployment Guide: `docs/DEPLOYMENT.md`
- Software Design Spec: `docs/SDS.md`

