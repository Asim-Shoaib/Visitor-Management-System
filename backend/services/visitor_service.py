from typing import Optional, Dict, List

from backend.database.connection import Database
from backend.utils.validator import (
    validate_cnic,
    validate_contact_number,
    validate_name,
)

db = Database()


def add_visitor(full_name: str, cnic: str, contact_number: Optional[str] = None) -> Optional[int]:
    """
    Insert a new visitor record.
    Returns the new visitor_id on success, otherwise None.
    """
    if not validate_name(full_name):
        raise ValueError("Invalid full name")
    if not validate_cnic(cnic):
        raise ValueError("Invalid CNIC format")
    if contact_number and not validate_contact_number(contact_number):
        raise ValueError("Invalid contact number format")

    try:
        existing = db.fetchone("SELECT visitor_id FROM Visitors WHERE cnic = %s", (cnic,))
    except Exception as e:
        raise ValueError(f"Database error when checking existing visitor: {e}")

    if existing:
        raise ValueError("Visitor with this CNIC already exists")

    insert_sql = """
        INSERT INTO Visitors (full_name, cnic, contact_number)
        VALUES (%s, %s, %s)
    """
    try:
        ok = db.execute(insert_sql, (full_name.strip(), cnic, contact_number))
    except Exception as e:
        raise ValueError(f"Database error when inserting visitor: {e}")

    if not ok:
        raise ValueError("Failed to insert visitor")

    row = db.fetchone("SELECT visitor_id FROM Visitors WHERE cnic = %s", (cnic,))
    return row["visitor_id"] if row else None


def search_visitor(*, cnic: Optional[str] = None, visitor_id: Optional[int] = None) -> Optional[Dict]:
    """
    Look up a visitor either by CNIC or by visitor_id.
    """
    row = None
    if cnic:
        row = db.fetchone("SELECT * FROM Visitors WHERE cnic = %s", (cnic,))
    if visitor_id:
        row = db.fetchone("SELECT * FROM Visitors WHERE visitor_id = %s", (visitor_id,))

    if not row:
        return None

    # Normalize datetime fields to ISO strings
    for dt_field in ('created_at',):
        if row.get(dt_field):
            try:
                row[dt_field] = row[dt_field].isoformat()
            except Exception:
                row[dt_field] = None
    return row
    return None


def list_visitors() -> List[Dict]:
    """Return all visitors (most recent first)."""
    rows = db.fetchall("SELECT * FROM Visitors ORDER BY visitor_id DESC")
    processed = []
    for r in rows or []:
        r_copy = dict(r)
        # No datetime fields currently except potential created_at
        if r_copy.get('created_at'):
            try:
                r_copy['created_at'] = r_copy['created_at'].isoformat()
            except Exception:
                r_copy['created_at'] = None
        processed.append(r_copy)
    return processed


