from datetime import datetime, timedelta, time
from typing import Optional, Dict, List
import configparser
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from backend.database.connection import Database
from backend.utils.db_logger import log_action

db = Database()

# Late arrival threshold: 9:10 AM
LATE_THRESHOLD_TIME = time(9, 10)


def _get_config():
    """Load configuration from config.ini"""
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.ini')
    config.read(config_path)
    return config


def _send_late_alert_email(employee_name: str, employee_email: str, times_late: int, salary_estimate: float) -> bool:
    """Send email alert to admin when employee is late 3 times in 30 days"""
    try:
        config = _get_config()
        smtp_server = config.get('email', 'smtp_server')
        smtp_port = config.getint('email', 'smtp_port')
        sender_email = config.get('email', 'sender_email')
        sender_password = config.get('email', 'sender_password')
        admin_email = config.get('email', 'admin_email', fallback=sender_email)
        
        # Skip email if credentials are not configured
        if sender_email == 'your_email@gmail.com' or sender_password == 'your_password':
            # Email not configured, skip silently
            return False
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = admin_email
        msg['Subject'] = f"Late Arrival Alert: {employee_name}"
        
        body = f"""
Admin Alert: Employee Late Arrival Threshold Reached

Employee: {employee_name}
Email: {employee_email}
Late Arrivals (Last 30 Days): {times_late}
Estimated Salary (Based on Recent Scans): ${salary_estimate:.2f}

This employee has been late 3 or more times in the last 30 days.
Please review attendance records.

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
        # Log error silently (email sending failed)
        return False


def _get_employee_current_status(emp_qr_id: int) -> Optional[str]:
    """
    Determine current sign-in status from EmployeeScanLogs.
    Returns 'signin' if last scan was signin, 'signout' if last scan was signout, None if no scans.
    """
    last_scan = db.fetchone("""
        SELECT scan_status 
        FROM EmployeeScanLogs 
        WHERE emp_qr_id = %s 
        ORDER BY timestamp DESC 
        LIMIT 1
    """, (emp_qr_id,))
    
    if not last_scan:
        return None
    
    return last_scan["scan_status"]


def _is_late_checkin(scan_time: datetime) -> bool:
    """Check if check-in time is after 9:10 AM"""
    scan_time_only = scan_time.time()
    return scan_time_only > LATE_THRESHOLD_TIME


def _get_late_count_last_30_days(employee_id: int) -> int:
    """Count late check-ins in the last 30 days for an employee"""
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    # Get all signin scans for this employee in last 30 days
    scans = db.fetchall("""
        SELECT esl.timestamp
        FROM EmployeeScanLogs esl
        JOIN EmployeeQRCodes eqr ON esl.emp_qr_id = eqr.emp_qr_id
        WHERE eqr.employee_id = %s
          AND esl.scan_status = 'signin'
          AND esl.timestamp >= %s
        ORDER BY esl.timestamp
    """, (employee_id, thirty_days_ago))
    
    late_count = 0
    for scan in scans:
        if _is_late_checkin(scan["timestamp"]):
            late_count += 1
    
    return late_count


def _calculate_salary_estimate(employee_id: int) -> float:
    """
    Calculate salary estimate based on recent check-in/checkout times and hourly_rate.
    Uses last 30 days of scans.
    """
    employee = db.fetchone("SELECT hourly_rate FROM Employees WHERE employee_id = %s", (employee_id,))
    if not employee:
        return 0.0
    
    hourly_rate = float(employee["hourly_rate"])
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    # Get all scans in pairs (signin, signout) for last 30 days
    scans = db.fetchall("""
        SELECT esl.scan_status, esl.timestamp
        FROM EmployeeScanLogs esl
        JOIN EmployeeQRCodes eqr ON esl.emp_qr_id = eqr.emp_qr_id
        WHERE eqr.employee_id = %s
          AND esl.timestamp >= %s
        ORDER BY esl.timestamp
    """, (employee_id, thirty_days_ago))
    
    total_hours = 0.0
    signin_time = None
    
    for scan in scans:
        if scan["scan_status"] == "signin":
            signin_time = scan["timestamp"]
        elif scan["scan_status"] == "signout" and signin_time:
            checkout_time = scan["timestamp"]
            hours = (checkout_time - signin_time).total_seconds() / 3600.0
            total_hours += max(0, hours)  # Ensure non-negative
            signin_time = None
    
    return total_hours * hourly_rate


def scan_employee_qr(emp_qr_id: int, scan_status: str, scanned_by_user_id: int) -> Optional[Dict]:
    """
    Scan an employee QR code and record in EmployeeScanLogs.
    Determines signin/signout based on last scan status.
    Detects late arrivals and maintains late count.
    """
    if scan_status not in ("signin", "signout"):
        return None
    
    # Validate QR code exists and is active
    qr_record = db.fetchone("""
        SELECT eqr.emp_qr_id, eqr.employee_id, eqr.status, eqr.expiry_date, e.name as employee_name
        FROM EmployeeQRCodes eqr
        JOIN Employees e ON eqr.employee_id = e.employee_id
        WHERE eqr.emp_qr_id = %s
    """, (emp_qr_id,))
    
    if not qr_record:
        return None
    
    # Check if expired
    if qr_record.get("expiry_date") and datetime.now() > qr_record["expiry_date"]:
        return None
    
    if qr_record["status"] != "active":
        return None
    
    # Determine expected status based on last scan
    current_status = _get_employee_current_status(emp_qr_id)
    
    # Validate scan makes sense (can't sign in if already signed in, can't sign out if not signed in)
    if scan_status == "signin" and current_status == "signin":
        return None  # Already signed in
    if scan_status == "signout" and current_status != "signin":
        return None  # Not signed in, can't sign out
    
    # Insert scan log
    scan_time = datetime.now()
    insert_sql = """
        INSERT INTO EmployeeScanLogs (emp_qr_id, scan_status, timestamp)
        VALUES (%s, %s, %s)
    """
    success = db.execute(insert_sql, (emp_qr_id, scan_status, scan_time))
    
    if not success:
        return None
    
    employee_id = qr_record["employee_id"]
    is_late = False
    
    # Check for late arrival (only for signin)
    if scan_status == "signin":
        is_late = _is_late_checkin(scan_time)
        
        # Get late count and check if threshold reached
        late_count = _get_late_count_last_30_days(employee_id)
        
        # If this is the 3rd late arrival, send alert
        if late_count >= 3:
            salary_estimate = _calculate_salary_estimate(employee_id)
            # Try to get employee email (if available in future schema)
            employee_email = "N/A"  # Placeholder - would need email field in Employees table
            _send_late_alert_email(
                qr_record["employee_name"],
                employee_email,
                late_count,
                salary_estimate
            )
    
    # Log action
    log_action(
        scanned_by_user_id,
        "scan_employee_qr",
        f"Scanned employee QR (emp_qr_id={emp_qr_id}, employee_id={employee_id}, status={scan_status}, late={is_late})"
    )
    
    # Get the inserted scan_id
    scan_record = db.fetchone("SELECT scan_id FROM EmployeeScanLogs WHERE emp_qr_id = %s AND timestamp = %s ORDER BY scan_id DESC LIMIT 1", (emp_qr_id, scan_time))
    scan_id = scan_record["scan_id"] if scan_record else None
    
    return {
        "scan_id": scan_id,
        "emp_qr_id": emp_qr_id,
        "employee_id": employee_id,
        "employee_name": qr_record["employee_name"],
        "scan_status": scan_status,
        "timestamp": scan_time.isoformat(),
        "is_late": is_late,
        "current_status": scan_status,  # After this scan, employee is in this status
    }


def scan_visitor_qr(visitor_qr_id: int, scan_status: str, scanned_by_user_id: int) -> Optional[Dict]:
    """
    Scan a visitor QR code and record in VisitorScanLogs.
    Updates Visits.status accordingly.
    Validates QR status and expiry.
    Creates alert if QR is invalid, expired, or revoked.
    """
    if scan_status not in ("signin", "signout"):
        return None
    
    # Validate QR code exists and get visit info
    qr_record = db.fetchone("""
        SELECT vqr.visitor_qr_id, vqr.visit_id, vqr.status, vqr.expiry_date,
               v.visit_id, v.status as visit_status, v.visitor_id,
               vis.full_name as visitor_name
        FROM VisitorQRCodes vqr
        JOIN Visits v ON vqr.visit_id = v.visit_id
        JOIN Visitors vis ON v.visitor_id = vis.visitor_id
        WHERE vqr.visitor_qr_id = %s
    """, (visitor_qr_id,))
    
    if not qr_record:
        # Create alert for invalid QR
        alert_desc = f"Invalid visitor QR code scanned (visitor_qr_id={visitor_qr_id} not found)"
        db.execute("""
            INSERT INTO Alerts (triggered_by, description, created_at)
            VALUES (%s, %s, %s)
        """, (visitor_qr_id, alert_desc, datetime.now()))
        return None
    
    # Check if expired
    if qr_record["expiry_date"] and datetime.now() > qr_record["expiry_date"]:
        alert_desc = f"Expired visitor QR code scanned (visitor_qr_id={visitor_qr_id}, expired={qr_record['expiry_date']})"
        db.execute("""
            INSERT INTO Alerts (triggered_by, description, created_at)
            VALUES (%s, %s, %s)
        """, (visitor_qr_id, alert_desc, datetime.now()))
        return None
    
    # Check if revoked
    if qr_record["status"] != "active":
        alert_desc = f"Revoked/inactive visitor QR code scanned (visitor_qr_id={visitor_qr_id}, status={qr_record['status']})"
        db.execute("""
            INSERT INTO Alerts (triggered_by, description, created_at)
            VALUES (%s, %s, %s)
        """, (visitor_qr_id, alert_desc, datetime.now()))
        return None
    
    # Insert scan log
    scan_time = datetime.now()
    insert_sql = """
        INSERT INTO VisitorScanLogs (visitor_qr_id, scan_status, timestamp)
        VALUES (%s, %s, %s)
    """
    success = db.execute(insert_sql, (visitor_qr_id, scan_status, scan_time))
    
    if not success:
        return None
    
    # Update visit status based on scan
    visit_id = qr_record["visit_id"]
    current_visit_status = qr_record["visit_status"]
    new_visit_status = None
    
    if scan_status == "signin" and current_visit_status == "pending":
        new_visit_status = "checked_in"
    elif scan_status == "signout" and current_visit_status == "checked_in":
        new_visit_status = "checked_out"
    
    if new_visit_status:
        # Update visit status and timestamps
        from backend.services.visit_service import update_visit_status
        update_visit_status(
            visit_id=visit_id,
            new_status=new_visit_status,
            requested_by_user_id=scanned_by_user_id
        )
    
    # Log action
    log_action(
        scanned_by_user_id,
        "scan_visitor_qr",
        f"Scanned visitor QR (visitor_qr_id={visitor_qr_id}, visit_id={visit_id}, status={scan_status})"
    )
    
    # Get the inserted scan_id
    scan_record = db.fetchone("SELECT scan_id FROM VisitorScanLogs WHERE visitor_qr_id = %s AND timestamp = %s ORDER BY scan_id DESC LIMIT 1", (visitor_qr_id, scan_time))
    scan_id = scan_record["scan_id"] if scan_record else None
    
    return {
        "scan_id": scan_id,
        "visitor_qr_id": visitor_qr_id,
        "visit_id": visit_id,
        "visitor_name": qr_record["visitor_name"],
        "scan_status": scan_status,
        "timestamp": scan_time.isoformat(),
        "visit_status_updated": new_visit_status is not None,
        "new_visit_status": new_visit_status,
    }


def get_active_alerts() -> List[Dict]:
    """Get all active alerts from Alerts table"""
    alerts = db.fetchall("""
        SELECT a.alert_id, a.triggered_by, a.description, a.created_at,
               vqr.visit_id, v.visitor_id, vis.full_name as visitor_name
        FROM Alerts a
        LEFT JOIN VisitorQRCodes vqr ON a.triggered_by = vqr.visitor_qr_id
        LEFT JOIN Visits v ON vqr.visit_id = v.visit_id
        LEFT JOIN Visitors vis ON v.visitor_id = vis.visitor_id
        ORDER BY a.created_at DESC
    """)
    return alerts


def get_employee_late_count(employee_id: int) -> Dict:
    """Get late count for an employee in the last 30 days"""
    employee = db.fetchone("SELECT employee_id, name FROM Employees WHERE employee_id = %s", (employee_id,))
    if not employee:
        return {"error": "Employee not found"}
    
    late_count = _get_late_count_last_30_days(employee_id)
    salary_estimate = _calculate_salary_estimate(employee_id)
    
    return {
        "employee_id": employee_id,
        "employee_name": employee["name"],
        "late_count_30_days": late_count,
        "salary_estimate": salary_estimate,
        "threshold_reached": late_count >= 3,
    }


def verify_qr_code(qr_code: str, scanned_by_user_id: int) -> Optional[Dict]:
    """
    Verify a QR code and determine if it belongs to an employee or visitor.
    Returns validation status and linked information.
    """
    import logging
    logger = logging.getLogger(__name__)

    if not qr_code or not qr_code.strip():
        return None

    raw_value = qr_code
    # Normalize: strip leading/trailing whitespace and remove newline/carriage returns
    normalized = raw_value.strip()
    normalized = normalized.replace('\n', '').replace('\r', '')

    # Defensive: also remove vertical/tab control chars but preserve internal spaces and other characters
    normalized = normalized.replace('\t', '').replace('\x0b', '').replace('\x0c', '')

    # Log raw and normalized values for debugging
    logger.debug("verify_qr_code raw=%r normalized=%r", raw_value, normalized)
    
    # Check if it's an employee QR code (starts with EMP_)
    if normalized.startswith("EMP_"):
        # Use deterministic trimmed, case-sensitive matching to avoid hidden char mismatches
        sql = """
            SELECT eqr.emp_qr_id, eqr.employee_id, eqr.status, eqr.expiry_date, e.name as employee_name, eqr.code_value
            FROM EmployeeQRCodes eqr
            JOIN Employees e ON eqr.employee_id = e.employee_id
            WHERE BINARY TRIM(eqr.code_value) = BINARY %s
        """
        logger.debug("verify_qr_code executing SQL: %s params=%r", sql.strip(), (normalized,))
        qr_record = db.fetchone(sql, (normalized,))

        # If a match is found but stored value contains surrounding whitespace or control chars,
        # normalize stored value to the trimmed normalized value to clean data (one-time fix)
        try:
            if qr_record and qr_record.get('code_value') and qr_record['code_value'] != normalized:
                update_sql = "UPDATE EmployeeQRCodes SET code_value = %s WHERE emp_qr_id = %s"
                logger.info("Trimming stored EmployeeQRCodes.code_value for emp_qr_id=%s", qr_record['emp_qr_id'])
                db.execute(update_sql, (normalized, qr_record['emp_qr_id']))
                qr_record['code_value'] = normalized
        except Exception:
            logger.exception("Failed to trim stored EmployeeQRCodes.code_value")
        
        if not qr_record:
            log_action(scanned_by_user_id, "verify_qr", f"Invalid employee QR code: {raw_value!r}")
            return {
                "type": "employee",
                "status": "invalid",
                "qr_code": raw_value,
                "message": "QR code not found"
            }
        
        # Check expiry for employee QR
        if qr_record.get("expiry_date") and datetime.now() > qr_record["expiry_date"]:
            log_action(scanned_by_user_id, "verify_qr", f"Expired employee QR code: {raw_value!r}")
            return {
                "type": "employee",
                "status": "expired",
                "qr_code": raw_value,
                "employee_id": qr_record["employee_id"],
                "employee_name": qr_record["employee_name"],
                "emp_qr_id": qr_record["emp_qr_id"],
                "expiry_date": qr_record["expiry_date"].isoformat(),
                "message": "QR code has expired"
            }

        if qr_record["status"] != "active":
            log_action(scanned_by_user_id, "verify_qr", f"Revoked employee QR code: {raw_value!r}")
            return {
                "type": "employee",
                "status": "revoked",
                "qr_code": raw_value,
                "employee_id": qr_record["employee_id"],
                "employee_name": qr_record["employee_name"],
                "message": "QR code has been revoked"
            }
        
        log_action(scanned_by_user_id, "verify_qr", f"Verified employee QR code: {raw_value!r} (employee_id={qr_record['employee_id']})")
        return {
            "type": "employee",
            "status": "valid",
            "qr_code": raw_value,
            "emp_qr_id": qr_record["emp_qr_id"],
            "employee_id": qr_record["employee_id"],
            "employee_name": qr_record["employee_name"],
            "linked_id": qr_record["emp_qr_id"],
            "expiry_date": qr_record["expiry_date"].isoformat() if qr_record.get("expiry_date") else None
        }
    
    # Check if it's a visitor QR code (starts with VIS_)
    elif normalized.startswith("VIS_"):
        sql = """
            SELECT vqr.visitor_qr_id, vqr.visit_id, vqr.status, vqr.expiry_date,
                   v.visitor_id, vis.full_name as visitor_name, vqr.code_value
            FROM VisitorQRCodes vqr
            JOIN Visits v ON vqr.visit_id = v.visit_id
            JOIN Visitors vis ON v.visitor_id = vis.visitor_id
            WHERE BINARY TRIM(vqr.code_value) = BINARY %s
        """
        logger.debug("verify_qr_code executing SQL: %s params=%r", sql.strip(), (normalized,))
        qr_record = db.fetchone(sql, (normalized,))

        # Clean stored value if it contains surrounding whitespace/control chars
        try:
            if qr_record and qr_record.get('code_value') and qr_record['code_value'] != normalized:
                update_sql = "UPDATE VisitorQRCodes SET code_value = %s WHERE visitor_qr_id = %s"
                logger.info("Trimming stored VisitorQRCodes.code_value for visitor_qr_id=%s", qr_record['visitor_qr_id'])
                db.execute(update_sql, (normalized, qr_record['visitor_qr_id']))
                qr_record['code_value'] = normalized
        except Exception:
            logger.exception("Failed to trim stored VisitorQRCodes.code_value")
        
        if not qr_record:
            log_action(scanned_by_user_id, "verify_qr", f"Invalid visitor QR code: {raw_value!r}")
            return {
                "type": "visitor",
                "status": "invalid",
                "qr_code": raw_value,
                "message": "QR code not found"
            }
        
        # Check if expired
        if qr_record["expiry_date"] and datetime.now() > qr_record["expiry_date"]:
            log_action(scanned_by_user_id, "verify_qr", f"Expired visitor QR code: {raw_value!r}")
            return {
                "type": "visitor",
                "status": "expired",
                "qr_code": raw_value,
                "visitor_qr_id": qr_record["visitor_qr_id"],
                "visit_id": qr_record["visit_id"],
                "visitor_id": qr_record["visitor_id"],
                "visitor_name": qr_record["visitor_name"],
                "expiry_date": qr_record["expiry_date"].isoformat(),
                "message": "QR code has expired"
            }
        
        # Check if revoked
        if qr_record["status"] != "active":
            log_action(scanned_by_user_id, "verify_qr", f"Revoked visitor QR code: {raw_value!r}")
            return {
                "type": "visitor",
                "status": "revoked",
                "qr_code": raw_value,
                "visitor_qr_id": qr_record["visitor_qr_id"],
                "visit_id": qr_record["visit_id"],
                "visitor_id": qr_record["visitor_id"],
                "visitor_name": qr_record["visitor_name"],
                "message": "QR code has been revoked"
            }
        
        log_action(scanned_by_user_id, "verify_qr", f"Verified visitor QR code: {raw_value!r} (visit_id={qr_record['visit_id']})")
        return {
            "type": "visitor",
            "status": "valid",
            "qr_code": raw_value,
            "visitor_qr_id": qr_record["visitor_qr_id"],
            "visit_id": qr_record["visit_id"],
            "visitor_id": qr_record["visitor_id"],
            "visitor_name": qr_record["visitor_name"],
            "linked_id": qr_record["visitor_qr_id"],
            "expiry_date": qr_record["expiry_date"].isoformat() if qr_record.get("expiry_date") else None
        }
    
    # Unknown QR code format
    log_action(scanned_by_user_id, "verify_qr", f"Unknown QR code format: {raw_value!r}")
    return {
        "type": "unknown",
        "status": "invalid",
        "qr_code": raw_value,
        "message": "Unknown QR code format"
    }


def visitor_checkin(qr_code: str, scanned_by_user_id: int) -> Optional[Dict]:
    """
    Check in a visitor using their QR code.
    Updates Visits.status to 'checked_in' and sets checkin_time.
    Prevents double check-in.
    Checks for visitor flags/alerts.
    """
    # Verify QR code first
    verification = verify_qr_code(qr_code, scanned_by_user_id)
    
    if not verification or verification["type"] != "visitor":
        return None
    
    if verification["status"] != "valid":
        return {
            "success": False,
            "error": verification.get("message", "Invalid QR code"),
            "status": verification["status"]
        }
    
    visit_id = verification["visit_id"]
    visitor_id = verification.get("visitor_id")
    
    # Check for visitor flags
    if visitor_id:
        from backend.services.alert_service import check_visitor_flags
        flags = check_visitor_flags(visitor_id)
        if flags:
            return {
                "success": False,
                "error": "Visitor has active security flags",
                "alert": True,
                "flags": flags,
                "message": "SECURITY ALERT: This visitor has been flagged. Please contact security."
            }
    
    # Check current visit status
    visit = db.fetchone("""
        SELECT status, checkin_time FROM Visits WHERE visit_id = %s
    """, (visit_id,))
    
    if not visit:
        return None
    
    # Prevent double check-in
    if visit["status"] == "checked_in":
        log_action(scanned_by_user_id, "visitor_checkin", f"Attempted double check-in for visit_id={visit_id}")
        return {
            "success": False,
            "error": "Visitor is already checked in",
            "visit_id": visit_id,
            "current_status": visit["status"]
        }
    
    # Only allow check-in from pending status
    if visit["status"] != "pending":
        log_action(scanned_by_user_id, "visitor_checkin", f"Invalid status for check-in: visit_id={visit_id}, status={visit['status']}")
        return {
            "success": False,
            "error": f"Cannot check in visitor with status: {visit['status']}",
            "visit_id": visit_id,
            "current_status": visit["status"]
        }
    
    # Update visit status to checked_in
    checkin_time = datetime.now()
    update_sql = """
        UPDATE Visits
        SET status = 'checked_in', checkin_time = %s
        WHERE visit_id = %s
    """
    success = db.execute(update_sql, (checkin_time, visit_id))
    
    if not success:
        return None
    
    # Insert scan log
    visitor_qr_id = verification["visitor_qr_id"]
    scan_sql = """
        INSERT INTO VisitorScanLogs (visitor_qr_id, scan_status, timestamp)
        VALUES (%s, 'signin', %s)
    """
    db.execute(scan_sql, (visitor_qr_id, checkin_time))
    
    # Log action
    log_action(
        scanned_by_user_id,
        "visitor_checkin",
        f"Checked in visitor (visit_id={visit_id}, visitor_name={verification['visitor_name']})"
    )
    
    return {
        "success": True,
        "visit_id": visit_id,
        "visitor_name": verification["visitor_name"],
        "checkin_time": checkin_time.isoformat(),
        "status": "checked_in"
    }


def visitor_checkout(qr_code: str, scanned_by_user_id: int) -> Optional[Dict]:
    """
    Check out a visitor using their QR code.
    Updates Visits.status to 'checked_out' and sets checkout_time.
    Prevents checkout before check-in.
    """
    # Verify QR code first
    verification = verify_qr_code(qr_code, scanned_by_user_id)
    
    if not verification or verification["type"] != "visitor":
        return None
    
    if verification["status"] != "valid":
        return {
            "success": False,
            "error": verification.get("message", "Invalid QR code"),
            "status": verification["status"]
        }
    
    visit_id = verification["visit_id"]
    visitor_id = verification.get("visitor_id")
    
    # Check for visitor flags (informational, but still allow checkout)
    flags = []
    if visitor_id:
        from backend.services.alert_service import check_visitor_flags
        flags = check_visitor_flags(visitor_id)
    
    # Check current visit status
    visit = db.fetchone("""
        SELECT status, checkin_time, checkout_time FROM Visits WHERE visit_id = %s
    """, (visit_id,))
    
    if not visit:
        return None
    
    # Prevent checkout before check-in
    if visit["status"] != "checked_in":
        log_action(scanned_by_user_id, "visitor_checkout", f"Attempted checkout without check-in: visit_id={visit_id}, status={visit['status']}")
        return {
            "success": False,
            "error": f"Cannot check out visitor with status: {visit['status']}. Visitor must be checked in first.",
            "visit_id": visit_id,
            "current_status": visit["status"]
        }
    
    # Prevent double checkout
    if visit["status"] == "checked_out":
        log_action(scanned_by_user_id, "visitor_checkout", f"Attempted double checkout for visit_id={visit_id}")
        return {
            "success": False,
            "error": "Visitor is already checked out",
            "visit_id": visit_id,
            "current_status": visit["status"]
        }
    
    # Update visit status to checked_out
    checkout_time = datetime.now()
    update_sql = """
        UPDATE Visits
        SET status = 'checked_out', checkout_time = %s
        WHERE visit_id = %s
    """
    success = db.execute(update_sql, (checkout_time, visit_id))
    
    if not success:
        return None
    
    # Insert scan log
    visitor_qr_id = verification["visitor_qr_id"]
    scan_sql = """
        INSERT INTO VisitorScanLogs (visitor_qr_id, scan_status, timestamp)
        VALUES (%s, 'signout', %s)
    """
    db.execute(scan_sql, (visitor_qr_id, checkout_time))
    
    # Log action
    log_action(
        scanned_by_user_id,
        "visitor_checkout",
        f"Checked out visitor (visit_id={visit_id}, visitor_name={verification['visitor_name']})"
    )
    
    return {
        "success": True,
        "visit_id": visit_id,
        "visitor_name": verification["visitor_name"],
        "checkin_time": visit["checkin_time"].isoformat() if visit["checkin_time"] else None,
        "checkout_time": checkout_time.isoformat(),
        "status": "checked_out"
    }

