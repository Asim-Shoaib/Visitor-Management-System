import qrcode
import os
import uuid
import configparser
from datetime import datetime, timedelta
from typing import Optional, Dict
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from backend.database.connection import Database
from backend.utils.db_logger import log_action
import logging

logger = logging.getLogger(__name__)

db = Database()


def _get_config():
    """Load configuration from config.ini"""
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.ini')
    config.read(config_path)
    return config


def _ensure_qr_directory():
    """Ensure the QR code storage directory exists"""
    qr_dir = os.path.join(os.path.dirname(__file__), '..', 'generated_qr')
    Path(qr_dir).mkdir(parents=True, exist_ok=True)
    return qr_dir


def _generate_qr_code_image(data: str, filepath: str) -> bool:
    """Generate a QR code image and save it to filepath"""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(filepath)
        return True
    except Exception as e:
        # Error generating QR code - return None
        return False


def _send_email_with_qr_link(recipient_email: str, visitor_name: str, download_url: str, expiry_date: datetime) -> bool:
    """Send email with QR code download link"""
    try:
        config = _get_config()
        smtp_server = config.get('email', 'smtp_server')
        smtp_port = config.getint('email', 'smtp_port')
        sender_email = config.get('email', 'sender_email')
        sender_password = config.get('email', 'sender_password')
        
        # Skip email if credentials are not configured
        if sender_email == 'your_email@gmail.com' or sender_password == 'your_password':
            # Email not configured, skip silently
            return False
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = "Visitor QR Code - Visitor Management System"
        
        body = f"""
Hello {visitor_name},

Your visitor QR code has been generated and is ready for download.

Download Link: {download_url}

Click the link above or copy and paste it into your browser to download your QR code.

This QR code will expire on: {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}

Please download and present this QR code at the security checkpoint.

Best regards,
Visitor Management System
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        # Error sending email - return False
        return False


def generate_employee_qr(employee_id: int, requested_by_user_id: int) -> Optional[Dict]:
    """
    Generate a permanent QR code for an employee.
    Maps to EmployeeQRCodes table.
    Returns dict with emp_qr_id, code_value, file_path, or None on failure.
    """
    # Validate employee exists
    try:
        employee = db.fetchone("SELECT employee_id, name FROM Employees WHERE employee_id = %s", (employee_id,))
    except Exception as e:
        logger.exception("DB error fetching employee for QR generation")
        return None

    if not employee:
        return None
    
    # Generate unique code value
    code_value = f"EMP_{employee_id}_{uuid.uuid4().hex[:12]}"
    
    # Check for duplicate code_value (shouldn't happen, but safety check)
    try:
        existing = db.fetchone("SELECT emp_qr_id FROM EmployeeQRCodes WHERE code_value = %s", (code_value,))
    except Exception as e:
        logger.exception("DB error checking duplicate employee QR code")
        return None

    if existing:
        return None  # Retry would be needed, but for now return None
    
    # Generate QR code image
    qr_dir = _ensure_qr_directory()
    filename = f"emp_{employee_id}_{code_value}.png"
    filepath = os.path.join(qr_dir, filename)
    
    if not _generate_qr_code_image(code_value, filepath):
        return None
    
    # Insert into EmployeeQRCodes (permanent, no expiry_date)
    insert_sql = """
        INSERT INTO EmployeeQRCodes (code_value, employee_id, issue_date, expiry_date, status)
        VALUES (%s, %s, %s, NULL, 'active')
    """
    issue_date = datetime.now()
    try:
        success = db.execute(insert_sql, (code_value, employee_id, issue_date))
    except Exception as e:
        logger.exception("DB error inserting employee QR code")
        success = False
    
    if not success:
        # Clean up file if DB insert failed
        try:
            os.remove(filepath)
        except:
            pass
        return None
    
    # Get the inserted emp_qr_id
    try:
        qr_record = db.fetchone("SELECT emp_qr_id, issue_date, expiry_date, status FROM EmployeeQRCodes WHERE code_value = %s", (code_value,))
    except Exception as e:
        logger.exception("DB error fetching inserted employee QR record")
        return None

    if not qr_record:
        return None
    
    # Log action
    log_action(
        requested_by_user_id,
        "generate_employee_qr",
        f"Generated employee QR code for employee_id={employee_id} (emp_qr_id={qr_record['emp_qr_id']})"
    )
    
    return {
        "emp_qr_id": qr_record["emp_qr_id"],
        "code_value": code_value,
        "file_path": filepath,
        "employee_id": employee_id,
        "employee_name": employee["name"],
        "issue_date": qr_record["issue_date"].isoformat() if qr_record.get("issue_date") else None,
        "expiry_date": qr_record["expiry_date"].isoformat() if qr_record.get("expiry_date") else None,
        "status": qr_record.get("status", "active")
    }


def generate_visitor_qr(visit_id: int, recipient_email: str, requested_by_user_id: int) -> Optional[Dict]:
    """
    Generate a temporary QR code for a visitor visit.
    Maps to VisitorQRCodes table.
    Emails the QR code as a downloadable link.
    Returns dict with visitor_qr_id, code_value, download_url, or None on failure.
    """
    # First, check if visit exists (without JOIN to get better error info)
    visit_check = db.fetchone("SELECT visit_id, visitor_id, status FROM Visits WHERE visit_id = %s", (visit_id,))
    
    if not visit_check:
        log_action(
            requested_by_user_id,
            "generate_visitor_qr_failed",
            f"Visit not found: visit_id={visit_id}"
        )
        return None
    
    # Check if visit status allows QR generation (should be pending or checked_in)
    if visit_check["status"] not in ("pending", "checked_in"):
        log_action(
            requested_by_user_id,
            "generate_visitor_qr_failed",
            f"Visit status does not allow QR generation: visit_id={visit_id}, status={visit_check['status']}"
        )
        return None
    
    # Now get full visit info with visitor details
    visit = db.fetchone("""
        SELECT v.visit_id, v.visitor_id, v.site_id, v.status, vis.full_name, vis.contact_number
        FROM Visits v
        JOIN Visitors vis ON v.visitor_id = vis.visitor_id
        WHERE v.visit_id = %s
    """, (visit_id,))
    
    if not visit:
        log_action(
            requested_by_user_id,
            "generate_visitor_qr_failed",
            f"Visitor not found for visit: visit_id={visit_id}, visitor_id={visit_check['visitor_id']}"
        )
        return None
    
    # Check if there's already an active QR code for this visit
    try:
        existing_qr = db.fetchone("""
            SELECT visitor_qr_id, code_value, status, expiry_date
            FROM VisitorQRCodes
            WHERE visit_id = %s AND status = 'active'
            ORDER BY issue_date DESC
            LIMIT 1
        """, (visit_id,))
    except Exception as e:
        logger.exception("DB error checking existing visitor QR")
        return None
    
    if existing_qr:
        # Check if existing QR is expired
        if existing_qr["expiry_date"] and datetime.now() > existing_qr["expiry_date"]:
            # Mark old QR as expired and continue to create new one
            db.execute(
                "UPDATE VisitorQRCodes SET status = 'expired' WHERE visitor_qr_id = %s",
                (existing_qr["visitor_qr_id"],)
            )
        else:
            # Return existing active QR code info instead of creating duplicate
            log_action(
                requested_by_user_id,
                "generate_visitor_qr_existing",
                f"Using existing active QR code for visit_id={visit_id}, visitor_qr_id={existing_qr['visitor_qr_id']}"
            )
            
            # Construct download URL for existing QR
            download_path = f"/qr/download/{existing_qr['visitor_qr_id']}"
            config = _get_config()
            try:
                base_url = config.get('app', 'base_url', fallback='')
                if base_url:
                    download_url = f"{base_url.rstrip('/')}{download_path}"
                else:
                    download_url = download_path
            except:
                download_url = download_path
            
            return {
                "visitor_qr_id": existing_qr["visitor_qr_id"],
                "code_value": existing_qr["code_value"],
                "visit_id": visit_id,
                "visitor_name": visit["full_name"],
                "download_url": download_url,
                "expiry_date": existing_qr["expiry_date"].isoformat() if existing_qr["expiry_date"] else None,
                "email_sent": False,  # Email already sent for this QR
                "existing": True,
            }
    
    # Get expiry hours from config
    config = _get_config()
    expiry_hours = config.getint('app', 'qr_code_expiry_hours', fallback=24)
    issue_date = datetime.now()
    expiry_date = issue_date + timedelta(hours=expiry_hours)
    
    # Generate unique code value
    code_value = f"VIS_{visit_id}_{uuid.uuid4().hex[:12]}"
    
    # Check for duplicate code_value (retry if collision)
    existing = db.fetchone("SELECT visitor_qr_id FROM VisitorQRCodes WHERE code_value = %s", (code_value,))
    if existing:
        # Retry with new UUID (very unlikely but handle it)
        code_value = f"VIS_{visit_id}_{uuid.uuid4().hex[:12]}"
        existing = db.fetchone("SELECT visitor_qr_id FROM VisitorQRCodes WHERE code_value = %s", (code_value,))
        if existing:
            log_action(
                requested_by_user_id,
                "generate_visitor_qr_failed",
                f"Code value collision after retry for visit_id={visit_id}"
            )
            return None
    
    # Generate QR code image
    qr_dir = _ensure_qr_directory()
    filename = f"vis_{visit_id}_{code_value}.png"
    filepath = os.path.join(qr_dir, filename)
    
    if not _generate_qr_code_image(code_value, filepath):
        log_action(
            requested_by_user_id,
            "generate_visitor_qr_failed",
            f"Failed to generate QR code image for visit_id={visit_id}"
        )
        return None
    
    # Insert into VisitorQRCodes (temporary, with expiry_date NOT NULL)
    insert_sql = """
        INSERT INTO VisitorQRCodes (code_value, visit_id, issue_date, expiry_date, status)
        VALUES (%s, %s, %s, %s, 'active')
    """
    try:
        success = db.execute(insert_sql, (code_value, visit_id, issue_date, expiry_date))
    except Exception as e:
        logger.exception("DB error inserting visitor QR code")
        success = False
    
    if not success:
        log_action(
            requested_by_user_id,
            "generate_visitor_qr_failed",
            f"Failed to insert QR code into database for visit_id={visit_id}, code_value={code_value}"
        )
        # Clean up file if DB insert failed
        try:
            os.remove(filepath)
        except:
            pass
        return None
    
    # Get the inserted visitor_qr_id
    qr_record = db.fetchone("SELECT visitor_qr_id FROM VisitorQRCodes WHERE code_value = %s", (code_value,))
    if not qr_record:
        log_action(
            requested_by_user_id,
            "generate_visitor_qr_failed",
            f"QR code inserted but could not retrieve visitor_qr_id for visit_id={visit_id}, code_value={code_value}"
        )
        return None
    
    # Construct download URL
    # Note: This is a relative path. The client should prepend the base API URL.
    # Example: If API is at http://localhost:8000, full URL would be http://localhost:8000/qr/download/{visitor_qr_id}
    download_path = f"/qr/download/{qr_record['visitor_qr_id']}"
    
    # Try to get base URL from config, otherwise use relative path
    config = _get_config()
    try:
        base_url = config.get('app', 'base_url', fallback='')
        if base_url:
            download_url = f"{base_url.rstrip('/')}{download_path}"
        else:
            download_url = download_path
    except:
        download_url = download_path
    
    # Send email with download link
    email_sent = _send_email_with_qr_link(
        recipient_email,
        visit["full_name"],
        download_url,
        expiry_date
    )
    
    # Log action
    log_action(
        requested_by_user_id,
        "generate_visitor_qr",
        f"Generated visitor QR code for visit_id={visit_id} (visitor_qr_id={qr_record['visitor_qr_id']}), email_sent={email_sent}"
    )
    
    return {
        "visitor_qr_id": qr_record["visitor_qr_id"],
        "code_value": code_value,
        "file_path": filepath,
        "visit_id": visit_id,
        "visitor_name": visit["full_name"],
        "download_url": download_url,
        "download_path": download_path,  # Relative path for API clients
        "issue_date": issue_date.isoformat(),
        "expiry_date": expiry_date.isoformat(),
        "email_sent": email_sent,
    }


def debug_visit_info(visit_id: int) -> Optional[Dict]:
    """
    Debug function to check visit and visitor information.
    Helps diagnose QR generation issues.
    """
    # Check visit exists
    visit = db.fetchone("SELECT * FROM Visits WHERE visit_id = %s", (visit_id,))
    if not visit:
        return {"error": f"Visit {visit_id} not found"}
    
    # Check visitor exists
    visitor = db.fetchone("SELECT * FROM Visitors WHERE visitor_id = %s", (visit["visitor_id"],))
    if not visitor:
        return {
            "error": f"Visitor {visit['visitor_id']} not found for visit {visit_id}",
            "visit": visit
        }
    
    # Check existing QR codes
    qr_codes = db.fetchall(
        "SELECT * FROM VisitorQRCodes WHERE visit_id = %s ORDER BY issue_date DESC",
        (visit_id,)
    )
    
    # Check if JOIN works
    visit_with_visitor = db.fetchone("""
        SELECT v.visit_id, v.visitor_id, v.status, vis.full_name, vis.visitor_id as v_visitor_id
        FROM Visits v
        JOIN Visitors vis ON v.visitor_id = vis.visitor_id
        WHERE v.visit_id = %s
    """, (visit_id,))
    
    return {
        "visit": visit,
        "visitor": visitor,
        "existing_qr_codes": qr_codes,
        "can_generate_qr": visit["status"] in ("pending", "checked_in"),
        "join_test": visit_with_visitor is not None,
        "join_result": visit_with_visitor,
    }


def get_visitor_qr_file(visitor_qr_id: int) -> Optional[str]:
    """
    Get the file path for a visitor QR code by visitor_qr_id.
    Validates that the QR code exists and is active.
    Returns file path or None if not found/invalid.
    """
    qr_record = db.fetchone("""
        SELECT vqr.code_value, vqr.visit_id, vqr.status, vqr.expiry_date
        FROM VisitorQRCodes vqr
        WHERE vqr.visitor_qr_id = %s
    """, (visitor_qr_id,))
    
    if not qr_record:
        return None
    
    # Check if expired
    if qr_record["expiry_date"] and datetime.now() > qr_record["expiry_date"]:
        return None
    
    # Check if revoked
    if qr_record["status"] != "active":
        return None
    
    # Construct file path
    qr_dir = _ensure_qr_directory()
    filename = f"vis_{qr_record['visit_id']}_{qr_record['code_value']}.png"
    filepath = os.path.join(qr_dir, filename)
    
    # Check if file exists
    if not os.path.exists(filepath):
        return None
    
    return filepath


def get_employee_qr_file(emp_qr_id: int) -> Optional[str]:
    """
    Get the file path for an employee QR code by emp_qr_id.
    Validates that the QR code exists and is active.
    Returns file path or None if not found/invalid.
    """
    qr_record = db.fetchone("""
        SELECT eqr.code_value, eqr.employee_id, eqr.status
        FROM EmployeeQRCodes eqr
        WHERE eqr.emp_qr_id = %s
    """, (emp_qr_id,))
    
    if not qr_record:
        return None
    
    # Check if revoked (employee QR codes are permanent, no expiry check needed)
    if qr_record["status"] != "active":
        return None
    
    # Construct file path
    qr_dir = _ensure_qr_directory()
    filename = f"emp_{qr_record['employee_id']}_{qr_record['code_value']}.png"
    filepath = os.path.join(qr_dir, filename)
    
    # Check if file exists
    if not os.path.exists(filepath):
        return None
    
    return filepath
