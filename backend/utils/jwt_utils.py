import jwt
import configparser
import os
from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import HTTPException

# JWT token expiration: 24 hours
TOKEN_EXPIRATION_HOURS = 24


def _get_secret_key() -> str:
    """Load JWT secret key from config.ini"""
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.ini')
    config.read(config_path)
    secret_key = config.get('app', 'secret_key', fallback='your-secret-key-here')
    
    if secret_key == 'your-secret-key-here':
        # Use a default secret for development (should be changed in production)
        secret_key = 'default-secret-key-change-in-production'
    
    return secret_key


def generate_jwt_token(user_id: int, username: str, role: str) -> str:
    """
    Generate a JWT token for a user.
    Token includes user_id, username, role, and expiration.
    """
    secret_key = _get_secret_key()
    expiration = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRATION_HOURS)
    
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "exp": expiration,
        "iat": datetime.utcnow(),
    }
    
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token


def verify_jwt_token(token: str) -> Optional[Dict]:
    """
    Verify and decode a JWT token.
    Returns payload dict if valid, None if invalid.
    """
    secret_key = _get_secret_key()
    
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_user_from_token(token: str) -> Optional[Dict]:
    """
    Extract user information from JWT token.
    Returns dict with user_id, username, role, or None if invalid.
    """
    payload = verify_jwt_token(token)
    if not payload:
        return None
    
    return {
        "user_id": payload.get("user_id"),
        "username": payload.get("username"),
        "role": payload.get("role"),
    }

