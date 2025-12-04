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
