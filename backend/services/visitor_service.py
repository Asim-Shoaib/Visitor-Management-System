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
        return None
    if not validate_cnic(cnic):
        return None
    if contact_number and not validate_contact_number(contact_number):
        return None

    existing = db.fetchone("SELECT visitor_id FROM Visitors WHERE cnic = %s", (cnic,))
    if existing:
        return None

    insert_sql = """
        INSERT INTO Visitors (full_name, cnic, contact_number)
        VALUES (%s, %s, %s)
    """
    ok = db.execute(insert_sql, (full_name.strip(), cnic, contact_number))
    if not ok:
        return None

    row = db.fetchone("SELECT visitor_id FROM Visitors WHERE cnic = %s", (cnic,))
    return row["visitor_id"] if row else None


def search_visitor(*, cnic: Optional[str] = None, visitor_id: Optional[int] = None) -> Optional[Dict]:
    """
    Look up a visitor either by CNIC or by visitor_id.
    """
    if cnic:
        return db.fetchone("SELECT * FROM Visitors WHERE cnic = %s", (cnic,))
    if visitor_id:
        return db.fetchone("SELECT * FROM Visitors WHERE visitor_id = %s", (visitor_id,))
    return None


def list_visitors() -> List[Dict]:
    """Return all visitors (most recent first)."""
    return db.fetchall("SELECT * FROM Visitors ORDER BY visitor_id DESC")


