import re
from typing import Optional

def validate_cnic(cnic: str) -> bool:
    """
    Validates CNIC format: XXXXX-XXXXXXX-X
    """
    pattern = r'^[0-9]{5}-[0-9]{7}-[0-9]$'
    return bool(re.match(pattern, cnic))

def validate_contact_number(contact: Optional[str]) -> bool:
    """
    Validates contact number (basic validation).
    """
    if not contact:
        return True  # Contact is optional
    # Allow digits, spaces, hyphens, plus signs
    pattern = r'^[\d\s\-\+]+$'
    return bool(re.match(pattern, contact)) and len(contact) >= 7

def validate_name(name: str) -> bool:
    """
    Validates name (should not be empty and reasonable length).
    """
    if not name or not name.strip():
        return False
    return 2 <= len(name.strip()) <= 150

def validate_username(username: str) -> bool:
    """
    Validates username format.
    """
    if not username or not username.strip():
        return False
    # Allow alphanumeric and underscore, 3-150 chars
    pattern = r'^[a-zA-Z0-9_]{3,150}$'
    return bool(re.match(pattern, username))

def validate_password(password: str) -> bool:
    """
    Validates password (minimum length requirement).
    """
    return len(password) >= 6

def validate_email(email: str) -> bool:
    """
    Validates email format using regex.
    """
    if not email or not email.strip():
        return False
    # RFC 5322 compliant email regex (simplified)
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))

def validate_positive_integer(value: int) -> bool:
    """
    Validates that an integer is positive (> 0).
    """
    return isinstance(value, int) and value > 0

def validate_id_format(id_value: int, min_value: int = 1, max_value: int = 2147483647) -> bool:
    """
    Validates ID format (positive integer within range).
    Default range: 1 to max MySQL INT value.
    """
    if not isinstance(id_value, int):
        return False
    return min_value <= id_value <= max_value

def validate_scan_status(status: str) -> bool:
    """
    Validates scan status is either 'signin' or 'signout'.
    """
    return status in ("signin", "signout")

def validate_visit_status(status: str) -> bool:
    """
    Validates visit status is one of the allowed values.
    """
    return status in ("pending", "checked_in", "checked_out", "denied")

