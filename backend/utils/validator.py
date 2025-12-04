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

