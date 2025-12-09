from fastapi import Header, HTTPException
from typing import Optional

from backend.utils.jwt_utils import get_user_from_token


def get_current_user_id(authorization: Optional[str] = Header(default=None)) -> int:
    """
    Extract the user_id from a JWT Bearer token.
    Accepts "Bearer <token>" (preferred) or a raw token value.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")

    try:
        token = authorization
        if authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "").strip()
        token = token.strip()

        user_info = get_user_from_token(token)
        if not user_info:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        return user_info["user_id"]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid authorization token: {str(e)}")


def get_current_user(authorization: Optional[str] = Header(default=None)) -> dict:
    """
    Extract full user information from a JWT Bearer token.
    Accepts "Bearer <token>" (preferred) or a raw token value.
    Returns dict with user_id, username, and role.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")

    try:
        token = authorization
        if authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "").strip()
        token = token.strip()

        user_info = get_user_from_token(token)
        
        if not user_info:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        return user_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid authorization token: {str(e)}")
