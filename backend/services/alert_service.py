from datetime import datetime
from typing import Optional, Dict, List

from backend.database.connection import Database
from backend.utils.db_logger import log_action

db = Database()


def flag_visitor(visitor_id: int, reason: str, flagged_by_user_id: int) -> Optional[Dict]:
    """
    Flag a visitor for security reasons.
    Creates an alert entry in Alerts table.
    
    Args:
        visitor_id: Visitor ID to flag
        reason: Reason for flagging
        flagged_by_user_id: User ID who flagged the visitor
    
    Returns:
        Dict with alert details or None if failed
    """
    # Check if visitor exists
    visitor = db.fetchone(
        "SELECT visitor_id, full_name FROM Visitors WHERE visitor_id = %s",
        (visitor_id,)
    )
    if not visitor:
        return None
    
    # Check if visitor has active visit with QR code
    visit_qr = db.fetchone("""
        SELECT vqr.visitor_qr_id
        FROM Visits v
        INNER JOIN VisitorQRCodes vqr ON v.visit_id = vqr.visit_id
        WHERE v.visitor_id = %s
          AND vqr.status = 'active'
        ORDER BY vqr.issue_date DESC
        LIMIT 1
    """, (visitor_id,))
    
    visitor_qr_id = visit_qr['visitor_qr_id'] if visit_qr else None
    
    # Create alert
    alert_sql = """
        INSERT INTO Alerts (triggered_by, description, created_at)
        VALUES (%s, %s, %s)
    """
    description = f"Visitor {visitor['full_name']} (ID: {visitor_id}) flagged: {reason}"
    
    success = db.execute(
        alert_sql,
        (visitor_qr_id, description, datetime.now())
    )
    
    if not success:
        return None
    
    # Get inserted alert
    alert = db.fetchone("""
        SELECT alert_id, triggered_by, description, created_at
        FROM Alerts
        WHERE triggered_by = %s
        ORDER BY alert_id DESC
        LIMIT 1
    """, (visitor_qr_id,) if visitor_qr_id else (None,))
    
    # Log action
    log_action(
        flagged_by_user_id,
        'flag_visitor',
        f'Flagged visitor_id={visitor_id}: {reason}'
    )
    
    return alert


def check_visitor_flags(visitor_id: int) -> List[Dict]:
    """
    Check if a visitor has any active flags/alerts.
    
    Args:
        visitor_id: Visitor ID to check
    
    Returns:
        List of active alerts for this visitor
    """
    alerts = db.fetchall("""
        SELECT 
            a.alert_id,
            a.description,
            a.created_at,
            vqr.visit_id
        FROM Alerts a
        INNER JOIN VisitorQRCodes vqr ON a.triggered_by = vqr.visitor_qr_id
        INNER JOIN Visits v ON vqr.visit_id = v.visit_id
        WHERE v.visitor_id = %s
          AND vqr.status = 'active'
        ORDER BY a.created_at DESC
    """, (visitor_id,))
    
    return alerts


def get_flagged_visitors() -> List[Dict]:
    """Get all currently flagged visitors"""
    return db.fetchall("""
        SELECT DISTINCT
            v.visitor_id,
            v.full_name,
            v.cnic,
            a.description as flag_reason,
            a.created_at as flagged_at
        FROM Visitors v
        INNER JOIN Visits vis ON v.visitor_id = vis.visitor_id
        INNER JOIN VisitorQRCodes vqr ON vis.visit_id = vqr.visit_id
        INNER JOIN Alerts a ON vqr.visitor_qr_id = a.triggered_by
        WHERE vqr.status = 'active'
        ORDER BY a.created_at DESC
    """)

