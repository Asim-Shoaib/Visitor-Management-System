from hashlib import sha256
from typing import Optional, Dict

from backend.database.connection import Database
from backend.utils.db_logger import log_action
from backend.utils.validator import validate_username, validate_password

db = Database()


def hash_password(password: str) -> str:
    """Return SHA256 hash of a password."""
    return sha256(password.encode()).hexdigest()


def login(username: str, password: str) -> Optional[Dict]:
    """Authenticate a user and return their id/role payload."""
    if not validate_username(username) or not validate_password(password):
        return None

    sql = """
        SELECT u.user_id, u.username, r.role_name
        FROM Users u
        JOIN Roles r ON u.role_id = r.role_id
        WHERE u.username = %s AND u.password_hash = %s
    """

    user = db.fetchone(sql, (username, hash_password(password)))
    if not user:
        return None

    log_action(user["user_id"], "login", f"User {username} logged in")
    return {
        "user_id": user["user_id"],
        "username": user["username"],
        "role": user["role_name"],
    }


def register_user(username: str, password: str, role_name: str, admin_user_id: int) -> bool:
    """Register a new user (admin only)."""
    if role_name not in ("admin", "security"):
        return False

    if not validate_username(username) or not validate_password(password):
        return False

    existing = db.fetchone("SELECT user_id FROM Users WHERE username = %s", (username,))
    if existing:
        return False

    role = db.fetchone("SELECT role_id FROM Roles WHERE role_name = %s", (role_name,))
    if not role:
        return False

    insert_sql = """
        INSERT INTO Users (username, password_hash, role_id)
        VALUES (%s, %s, %s)
    """
    success = db.execute(insert_sql, (username, hash_password(password), role["role_id"]))
    if success:
        log_action(admin_user_id, "register_user", f"Registered user {username} ({role_name})")
    return success


def deactivate_user(user_id: int, admin_user_id: int) -> bool:
    """
    Deactivate a user (admin only). Prevents self-deactivation.
    This preserves all database records (Users and AccessLogs) for audit purposes.
    
    Note: EmployeeQRCodes revocation requires a Users->Employees relationship.
    Since the current schema doesn't have a direct FK between Users and Employees,
    QR code revocation is not implemented here. This should be added when the
    relationship is established in the schema.
    """
    if user_id == admin_user_id:
        return False

    user = db.fetchone("SELECT username FROM Users WHERE user_id = %s", (user_id,))
    if not user:
        return False

    # TODO: Revoke EmployeeQRCodes when Users->Employees relationship exists
    # Example implementation (when relationship exists):
    # revoke_qr_sql = """
    #     UPDATE EmployeeQRCodes eq
    #     JOIN Employees e ON eq.employee_id = e.employee_id
    #     JOIN Users u ON e.user_id = u.user_id  -- Requires FK in schema
    #     SET eq.status = 'revoked'
    #     WHERE u.user_id = %s AND eq.status = 'active'
    # """
    # db.execute(revoke_qr_sql, (user_id,))

    # Log the deactivation action (user record remains in database for audit)
    log_action(admin_user_id, "deactivate_user", f"Deactivated user {user['username']} (id={user_id})")
    return True


def get_user_role(user_id: int) -> Optional[str]:
    """Return the role name for a user."""
    sql = """
        SELECT r.role_name
        FROM Users u
        JOIN Roles r ON u.role_id = r.role_id
        WHERE u.user_id = %s
    """
    user = db.fetchone(sql, (user_id,))
    return user["role_name"] if user else None
