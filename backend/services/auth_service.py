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


def delete_user(user_id: int, admin_user_id: int) -> bool:
    """Delete a user (admin only). Prevents self-deletion."""
    if user_id == admin_user_id:
        return False

    user = db.fetchone("SELECT username FROM Users WHERE user_id = %s", (user_id,))
    if not user:
        return False

    success = db.execute("DELETE FROM Users WHERE user_id = %s", (user_id,))
    if success:
        log_action(admin_user_id, "delete_user", f"Deleted user {user['username']} (id={user_id})")
    return success


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

from backend.database.connection import Database
from backend.utils.validator import validate_username, validate_password
from backend.utils.db_logger import log_action
from hashlib import sha256
from typing import Optional, Dict

db = Database()

def hash_password(password: str) -> str:
    """Hash password using SHA256."""
    return sha256(password.encode()).hexdigest()

def login(username: str, password: str) -> Optional[Dict]:
    """
    Authenticate user and return user info with role.
    Returns None if authentication fails.
    """
    if not validate_username(username) or not validate_password(password):
        return None
    
    password_hash = hash_password(password)
    
    sql = """
        SELECT u.user_id, u.username, r.role_name
        FROM Users u
        JOIN Roles r ON u.role_id = r.role_id
        WHERE u.username = %s AND u.password_hash = %s
    """
    
    user = db.fetchone(sql, (username, password_hash))
    
    if user:
        log_action(user['user_id'], 'login', f'User {username} logged in')
        return {
            'user_id': user['user_id'],
            'username': user['username'],
            'role': user['role_name']
        }
    
    return None

def register_user(username: str, password: str, role_name: str, admin_user_id: int) -> bool:
    """
    Register a new user. Only admin can register users.
    Returns True if successful, False otherwise.
    """
    if not validate_username(username) or not validate_password(password):
        return False
    
    if role_name not in ['admin', 'security']:
        return False
    
    # Check if username already exists
    check_sql = "SELECT user_id FROM Users WHERE username = %s"
    existing = db.fetchone(check_sql, (username,))
    if existing:
        return False
    
    # Get role_id
    role_sql = "SELECT role_id FROM Roles WHERE role_name = %s"
    role = db.fetchone(role_sql, (role_name,))
    if not role:
        return False
    
    password_hash = hash_password(password)
    
    insert_sql = """
        INSERT INTO Users (username, password_hash, role_id)
        VALUES (%s, %s, %s)
    """
    
    success = db.execute(insert_sql, (username, password_hash, role['role_id']))
    
    if success:
        log_action(admin_user_id, 'register_user', f'Admin registered user: {username} with role: {role_name}')
    
    return success

def delete_user(user_id: int, admin_user_id: int) -> bool:
    """
    Delete a user. Only admin can delete users.
    Returns True if successful, False otherwise.
    """
    # Prevent self-deletion
    if user_id == admin_user_id:
        return False
    
    # Get username for logging
    user_sql = "SELECT username FROM Users WHERE user_id = %s"
    user = db.fetchone(user_sql, (user_id,))
    if not user:
        return False
    
    delete_sql = "DELETE FROM Users WHERE user_id = %s"
    success = db.execute(delete_sql, (user_id,))
    
    if success:
        log_action(admin_user_id, 'delete_user', f'Admin deleted user: {user["username"]} (ID: {user_id})')
    
    return success

def get_user_role(user_id: int) -> Optional[str]:
    """Get user's role name."""
    sql = """
        SELECT r.role_name
        FROM Users u
        JOIN Roles r ON u.role_id = r.role_id
        WHERE u.user_id = %s
    """
    user = db.fetchone(sql, (user_id,))
    return user['role_name'] if user else None

