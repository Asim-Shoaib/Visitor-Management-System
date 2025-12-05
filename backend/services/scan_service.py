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
            print("Email not configured. Skipping late alert email.")
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
        print(f"Error sending late alert email: {e}")
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
        SELECT eqr.emp_qr_id, eqr.employee_id, eqr.status, e.name as employee_name
        FROM EmployeeQRCodes eqr
        JOIN Employees e ON eqr.employee_id = e.employee_id
        WHERE eqr.emp_qr_id = %s
    """, (emp_qr_id,))
    
    if not qr_record:
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

