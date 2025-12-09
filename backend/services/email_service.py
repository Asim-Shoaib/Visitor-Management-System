import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from typing import Optional, Dict, List
import os
import configparser

from backend.database.connection import Database
from backend.utils.db_logger import log_action

db = Database()

# Load email config
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), '../config/config.ini'))


def _get_email_config() -> Optional[Dict]:
    """Get email configuration from config.ini"""
    try:
        return {
            'smtp_server': config.get('email', 'smtp_server', fallback=None),
            'smtp_port': config.getint('email', 'smtp_port', fallback=587),
            'sender_email': config.get('email', 'sender_email', fallback=None),
            'sender_password': config.get('email', 'sender_password', fallback=None),
            'admin_email': config.get('email', 'admin_email', fallback=None),
        }
    except:
        return None


def send_qr_code_email(recipient_email: str, visitor_id: int, qr_code_data: str, requested_by_user_id: int) -> Dict:
    """
    Generate QR code, convert to PNG, and email as attachment.
    
    Args:
        recipient_email: Email address to send to
        visitor_id: Visitor ID for logging
        qr_code_data: QR code data string
        requested_by_user_id: User ID requesting the email
    
    Returns:
        Dict with success status and message
    """
    email_config = _get_email_config()
    if not email_config or not email_config.get('smtp_server'):
        return {
            'success': False,
            'message': 'Email configuration not found. Please configure SMTP settings in config.ini'
        }
    
    try:
        import qrcode
        from io import BytesIO
        
        # Generate QR code image
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_code_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to bytes
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Create email
        msg = MIMEMultipart()
        msg['From'] = email_config['sender_email']
        msg['To'] = recipient_email
        msg['Subject'] = 'Visitor QR Code - Visitor Management System'
        
        # Email body
        body = f"""
        Dear Visitor,
        
        Please find your QR code attached to this email.
        
        QR Code Data: {qr_code_data}
        Visitor ID: {visitor_id}
        
        Please present this QR code at the reception for check-in.
        
        Best regards,
        Visitor Management System
        """
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach QR code image
        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(img_buffer.read())
        encoders.encode_base64(attachment)
        attachment.add_header(
            'Content-Disposition',
            f'attachment; filename=visitor_qr_{visitor_id}.png'
        )
        msg.attach(attachment)
        
        # Send email
        server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
        server.starttls()
        server.login(email_config['sender_email'], email_config['sender_password'])
        server.send_message(msg)
        server.quit()
        
        # Log action
        log_action(
            requested_by_user_id,
            'send_qr_email',
            f'Sent QR code email to {recipient_email} for visitor_id={visitor_id}'
        )
        
        return {
            'success': True,
            'message': f'QR code email sent successfully to {recipient_email}'
        }
        
    except Exception as e:
        log_action(
            requested_by_user_id,
            'send_qr_email_failed',
            f'Failed to send QR email: {str(e)}'
        )
        return {
            'success': False,
            'message': f'Failed to send email: {str(e)}'
        }


def send_late_arrival_alert(employee_id: int, late_count: int, salary_estimate: float, requested_by_user_id: int) -> Dict:
    """
    Send late arrival alert email to admin.
    Evaluates check-in times and detects late behavior.
    
    Args:
        employee_id: Employee ID
        late_count: Number of late arrivals
        salary_estimate: Estimated salary
        requested_by_user_id: User ID requesting the alert
    
    Returns:
        Dict with success status and message
    """
    email_config = _get_email_config()
    if not email_config or not email_config.get('admin_email'):
        return {
            'success': False,
            'message': 'Admin email not configured'
        }
    
    try:
        # Get employee details
        employee = db.fetchone(
            "SELECT name, department_id FROM Employees WHERE employee_id = %s",
            (employee_id,)
        )
        if not employee:
            return {
                'success': False,
                'message': 'Employee not found'
            }
        
        # Get department name
        dept = db.fetchone(
            "SELECT name FROM Departments WHERE department_id = %s",
            (employee['department_id'],)
        )
        dept_name = dept['name'] if dept else 'Unknown'
        
        # Create email
        msg = MIMEMultipart()
        msg['From'] = email_config['sender_email']
        msg['To'] = email_config['admin_email']
        msg['Subject'] = f'Late Arrival Alert - Employee {employee["name"]}'
        
        body = f"""
        Late Arrival Alert
        
        Employee Details:
        - Name: {employee['name']}
        - ID: {employee_id}
        - Department: {dept_name}
        
        Late Arrival Statistics:
        - Late arrivals in last 7 days: {late_count}
        - Estimated salary impact: ${salary_estimate:.2f}
        
        Action Required:
        Please review this employee's attendance record.
        
        Generated by Visitor Management System
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
        server.starttls()
        server.login(email_config['sender_email'], email_config['sender_password'])
        server.send_message(msg)
        server.quit()
        
        # Log action
        log_action(
            requested_by_user_id,
            'send_late_alert',
            f'Sent late arrival alert for employee_id={employee_id}, late_count={late_count}'
        )
        
        return {
            'success': True,
            'message': f'Late arrival alert sent to admin for employee {employee["name"]}'
        }
        
    except Exception as e:
        log_action(
            requested_by_user_id,
            'send_late_alert_failed',
            f'Failed to send late alert: {str(e)}'
        )
        return {
            'success': False,
            'message': f'Failed to send alert: {str(e)}'
        }


def check_and_send_late_alerts(requested_by_user_id: int) -> Dict:
    """
    Check all employees for late arrivals (after 9:00 AM, 3+ times in last 7 days)
    and send alerts.
    
    Returns:
        Dict with summary of alerts sent
    """
    try:
        # Get employees with 3+ late arrivals in last 7 days
        late_employees = db.fetchall("""
            SELECT 
                e.employee_id,
                e.name,
                COUNT(*) as late_count
            FROM Employees e
            INNER JOIN EmployeeQRCodes eqr ON e.employee_id = eqr.employee_id
            INNER JOIN EmployeeScanLogs esl ON eqr.emp_qr_id = esl.emp_qr_id
            WHERE esl.scan_status = 'signin'
              AND TIME(esl.timestamp) > '09:00:00'
              AND DATE(esl.timestamp) >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            GROUP BY e.employee_id, e.name
            HAVING late_count >= 3
        """)
        
        alerts_sent = []
        for emp in late_employees:
            # Calculate salary estimate
            salary_result = db.fetchone("""
                SELECT 
                    e.hourly_rate,
                    SUM(TIMESTAMPDIFF(HOUR, 
                        (SELECT timestamp FROM EmployeeScanLogs 
                         WHERE emp_qr_id = eqr.emp_qr_id 
                           AND scan_status = 'signin' 
                           AND DATE(timestamp) = DATE(esl.timestamp)
                         ORDER BY timestamp ASC LIMIT 1),
                        (SELECT timestamp FROM EmployeeScanLogs 
                         WHERE emp_qr_id = eqr.emp_qr_id 
                           AND scan_status = 'signout' 
                           AND DATE(timestamp) = DATE(esl.timestamp)
                         ORDER BY timestamp DESC LIMIT 1)
                    )) as total_hours
                FROM Employees e
                INNER JOIN EmployeeQRCodes eqr ON e.employee_id = eqr.employee_id
                INNER JOIN EmployeeScanLogs esl ON eqr.emp_qr_id = esl.emp_qr_id
                WHERE e.employee_id = %s
                  AND esl.scan_status = 'signin'
                  AND TIME(esl.timestamp) > '09:00:00'
                  AND DATE(esl.timestamp) >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                GROUP BY e.employee_id, e.hourly_rate
            """, (emp['employee_id'],))
            
            salary_estimate = 0.0
            if salary_result and salary_result.get('total_hours'):
                salary_estimate = (salary_result['total_hours'] or 0) * (salary_result['hourly_rate'] or 0)
            
            # Send alert
            result = send_late_arrival_alert(
                emp['employee_id'],
                emp['late_count'],
                salary_estimate,
                requested_by_user_id
            )
            
            if result['success']:
                alerts_sent.append({
                    'employee_id': emp['employee_id'],
                    'employee_name': emp['name'],
                    'late_count': emp['late_count']
                })
        
        return {
            'success': True,
            'alerts_sent': len(alerts_sent),
            'employees': alerts_sent,
            'message': f'Late arrival alerts sent for {len(alerts_sent)} employee(s)'
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to check late arrivals: {str(e)}'
        }

