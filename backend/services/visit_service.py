from datetime import datetime
from typing import List, Dict, Optional

from backend.database.connection import Database
from backend.utils.db_logger import log_action

db = Database()


def _validate_visit_status_transition(current_status: str, new_status: str) -> bool:
    """
    Enforce allowed status transitions for Visits.

    Allowed:
    - pending -> checked_in
    - pending -> denied
    - checked_in -> checked_out

    No other transitions are currently allowed.
    """
    allowed = {
        "pending": {"checked_in", "denied"},
        "checked_in": {"checked_out"},
        "checked_out": set(),
        "denied": set(),
    }
    return new_status in allowed.get(current_status, set())


def create_visit(
    *,
    visitor_id: int,
    site_id: int,
    purpose_details: Optional[str],
    host_employee_id: Optional[int],
    requested_by_user_id: int,
) -> Optional[int]:
    """
    Create a new visit record in Visits table.

    - visitor_id and site_id must exist (FK integrity).
    - host_employee_id is optional but, if provided, must exist.
    - Initial status is 'pending'.
    """
    # Check visitor exists
    visitor = db.fetchone(
        "SELECT visitor_id FROM Visitors WHERE visitor_id = %s", (visitor_id,)
    )
    if not visitor:
        return None

    # Check site exists
    site = db.fetchone("SELECT site_id FROM Sites WHERE site_id = %s", (site_id,))
    if not site:
        return None

    # Check host employee if provided
    if host_employee_id is not None:
        host = db.fetchone(
            "SELECT employee_id FROM Employees WHERE employee_id = %s",
            (host_employee_id,),
        )
        if not host:
            return None

    insert_sql = """
        INSERT INTO Visits (visitor_id, site_id, host_employee_id, purpose_details, status)
        VALUES (%s, %s, %s, %s, 'pending')
    """
    ok = db.execute(
        insert_sql,
        (visitor_id, site_id, host_employee_id, purpose_details),
    )
    if not ok:
        return None

    row = db.fetchone(
        """
        SELECT visit_id
        FROM Visits
        WHERE visitor_id = %s
        ORDER BY visit_id DESC
        LIMIT 1
        """,
        (visitor_id,),
    )
    visit_id = row["visit_id"] if row else None

    if visit_id is not None:
        log_action(
            requested_by_user_id,
            "create_visit",
            f"Created visit {visit_id} for visitor {visitor_id} at site {site_id}",
        )

    return visit_id


def update_visit_status(
    *,
    visit_id: int,
    new_status: str,
    requested_by_user_id: int,
) -> bool:
    """
    Update a visit's status and maintain timestamps:

    - pending -> checked_in : sets checkin_time (if not already set)
    - checked_in -> checked_out : sets checkout_time (if not already set)
    - pending -> denied : leaves timestamps null
    """
    if new_status not in ("pending", "checked_in", "checked_out", "denied"):
        return False

    visit = db.fetchone(
        "SELECT status, checkin_time, checkout_time FROM Visits WHERE visit_id = %s",
        (visit_id,),
    )
    if not visit:
        return False

    current_status = visit["status"]
    if not _validate_visit_status_transition(current_status, new_status):
        return False

    now = datetime.now()
    checkin_time = visit["checkin_time"]
    checkout_time = visit["checkout_time"]

    if current_status == "pending" and new_status == "checked_in":
        checkin_time = checkin_time or now
    elif current_status == "checked_in" and new_status == "checked_out":
        checkout_time = checkout_time or now

    update_sql = """
        UPDATE Visits
        SET status = %s,
            checkin_time = %s,
            checkout_time = %s
        WHERE visit_id = %s
    """
    ok = db.execute(update_sql, (new_status, checkin_time, checkout_time, visit_id))
    if ok:
        log_action(
            requested_by_user_id,
            "update_visit_status",
            f"Updated visit {visit_id} status from {current_status} to {new_status}",
        )
    return ok


def get_active_visits() -> List[Dict]:
    """
    Return all visits that are currently active (pending or checked_in),
    along with basic visitor and site information.
    """
    sql = """
        SELECT
            v.visit_id,
            v.status,
            v.checkin_time,
            v.checkout_time,
            v.issue_date,
            vs.full_name AS visitor_name,
            vs.cnic AS visitor_cnic,
            s.site_name,
            s.address,
            v.host_employee_id
        FROM Visits v
        JOIN Visitors vs ON v.visitor_id = vs.visitor_id
        JOIN Sites s ON v.site_id = s.site_id
        WHERE v.status IN ('pending', 'checked_in')
        ORDER BY v.issue_date DESC, v.visit_id DESC
    """
    return db.fetchall(sql)


