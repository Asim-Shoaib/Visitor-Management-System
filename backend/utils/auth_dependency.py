from fastapi import Header, HTTPException
from typing import Optional


def get_current_user_id(authorization: Optional[str] = Header(default=None)) -> int:
    """
    Extract the user_id from a simple Bearer token.
    The token format is: Bearer <user_id>:<role>
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")

    try:
        token = authorization.replace("Bearer ", "")
        user_id_str = token.split(":")[0]
        return int(user_id_str)
    except (ValueError, IndexError):
        raise HTTPException(status_code=401, detail="Invalid authorization token")

from fastapi import HTTPException, Header
from typing import Optional
import configparser
import os

def get_secret_key():
    """Get secret key from config."""
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.ini')
    config.read(config_path)
    return config.get('app', 'secret_key', fallback='your-secret-key-here')

def get_current_user_id(authorization: Optional[str] = Header(None)) -> int:
    """
    Extract user_id from JWT token in Authorization header.
    For simplicity, we'll use a simple token format: user_id:role
    In production, use proper JWT tokens.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    try:
        # Simple token format: "Bearer user_id:role"
        # In production, decode JWT token
        token = authorization.replace("Bearer ", "")
        user_id = int(token.split(":")[0])
        return user_id
    except:
        raise HTTPException(status_code=401, detail="Invalid authorization token")

# For now, we'll use a simpler approach - pass user_id in request body or header
# This is a placeholder - in production, implement proper JWT authentication

