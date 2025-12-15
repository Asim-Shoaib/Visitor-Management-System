from typing import Optional, Dict, List
from datetime import datetime

from backend.database.connection import Database
from backend.utils.db_logger import log_action

db = Database()


def create_visit(
    visitor_id: int,
    site_id: int,
    purpose_details: Optional[str] = None,
    host_employee_id: Optional[int] = None,
    requested_by_user_id: int = None
) -> Optional[int]:
    """
    Create a new visit record.
    Returns visit_id on success, None on failure.
    """
    # Validate visitor exists
    try:
        visitor = db.fetchone("SELECT visitor_id FROM Visitors WHERE visitor_id = %s", (visitor_id,))
    except Exception as e:
        raise ValueError(f"Database error when validating visitor: {e}")
    if not visitor:
        raise ValueError("Visitor not found")

    # Validate site exists
    try:
        site = db.fetchone("SELECT site_id FROM Sites WHERE site_id = %s", (site_id,))
    except Exception as e:
        raise ValueError(f"Database error when validating site: {e}")
    if not site:
        raise ValueError("Site not found")

    # Validate host employee if provided
    if host_employee_id:
        try:
            employee = db.fetchone("SELECT employee_id FROM Employees WHERE employee_id = %s", (host_employee_id,))
        except Exception as e:
            raise ValueError(f"Database error when validating host employee: {e}")
        if not employee:
            raise ValueError("Host employee not found")
    
    # Check if visitor already has an active visit (pending or checked_in)
    try:
        active_visit = db.fetchone("""
            SELECT visit_id FROM Visits 
            WHERE visitor_id = %s AND status IN ('pending', 'checked_in')
        """, (visitor_id,))
    except Exception as e:
        raise ValueError(f"Database error when checking active visits: {e}")
    if active_visit:
        raise ValueError("Visitor already has an active visit")
    
    # Insert visit
    insert_sql = """
        INSERT INTO visits (visitor_id, site_id, host_employee_id, purpose_details, status)
        VALUES (%s, %s, %s, %s, 'pending')
    """
    try:
        success = db.execute(insert_sql, (visitor_id, site_id, host_employee_id, purpose_details))
    except Exception as e:
        # Ensure no partial data remains
        raise ValueError(f"Database error when creating visit: {e}")

    if success:
        visit = db.fetchone("SELECT visit_id FROM Visits WHERE visitor_id = %s AND site_id = %s ORDER BY visit_id DESC LIMIT 1", (visitor_id, site_id))
        if visit:
            visit_id = visit['visit_id']
            if requested_by_user_id:
                log_action(requested_by_user_id, "create_visit", f"Created visit {visit_id} for visitor {visitor_id} at site {site_id}")
            return visit_id

    raise ValueError("Failed to create visit")


def update_visit_status(
    visit_id: int,
    new_status: str,
    requested_by_user_id: int = None
) -> bool:
    """
    Update visit status with proper transition validation.
    Allowed transitions:
    - pending -> checked_in (sets checkin_time)
    - pending -> denied (no timestamps)
    - checked_in -> checked_out (sets checkout_time)
    
    Returns True on success, False on failure.
    """
    valid_statuses = ('pending', 'checked_in', 'checked_out', 'denied')
    if new_status not in valid_statuses:
        return False
    
    # Get current visit status
    visit = db.fetchone("SELECT status, checkin_time, checkout_time FROM visits WHERE visit_id = %s", (visit_id,))
    if not visit:
        return False
    
    current_status = visit['status']
    
    # Validate status transitions
    valid_transitions = {
        'pending': ('checked_in', 'denied'),
        'checked_in': ('checked_out',),
        'checked_out': (),  # Terminal state
        'denied': ()  # Terminal state
    }
    
    if new_status not in valid_transitions.get(current_status, ()):
        return False
    
    # Update status and timestamps
    now = datetime.now()
    if new_status == 'checked_in':
        update_sql = """
            UPDATE visits 
            SET status = %s, checkin_time = %s 
            WHERE visit_id = %s
        """
        success = db.execute(update_sql, (new_status, now, visit_id))
    elif new_status == 'checked_out':
        update_sql = """
            UPDATE visits 
            SET status = %s, checkout_time = %s 
            WHERE visit_id = %s
        """
        success = db.execute(update_sql, (new_status, now, visit_id))
    else:
        update_sql = """
            UPDATE visits 
            SET status = %s 
            WHERE visit_id = %s
        """
        success = db.execute(update_sql, (new_status, visit_id))
    
    if success and requested_by_user_id:
        log_action(requested_by_user_id, "update_visit_status", f"Updated visit {visit_id} from {current_status} to {new_status}")
    
    return success


def get_active_visits() -> List[Dict]:
    """
    Get all active visits (pending or checked_in status).
    Returns list of visits with visitor and site information.
    """
    visits = db.fetchall("""
        SELECT 
            v.visit_id,
            v.visitor_id,
            vis.full_name as visitor_name,
            v.site_id,
            s.site_name,
            v.host_employee_id,
            e.name as host_employee_name,
            v.purpose_details,
            v.status,
            v.checkin_time,
            v.checkout_time,
            v.issue_date
        FROM visits v
        JOIN visitors vis ON v.visitor_id = vis.visitor_id
        JOIN sites s ON v.site_id = s.site_id
        LEFT JOIN employees e ON v.host_employee_id = e.employee_id
        WHERE v.status IN ('pending', 'checked_in')
        ORDER BY v.issue_date DESC
    """)
    
    return visits if visits is not None else []
    # Ensure datetime fields are serialized as ISO strings to avoid frontend "Invalid Date" issues
    processed = []
    for v in visits or []:
        v_copy = dict(v)
        for dt_field in ('checkin_time', 'checkout_time', 'issue_date'):
            if v_copy.get(dt_field):
                try:
                    v_copy[dt_field] = v_copy[dt_field].isoformat()
                except Exception:
                    v_copy[dt_field] = None
        processed.append(v_copy)
    return processed
