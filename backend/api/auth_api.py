from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.services.auth_service import (
    login,
    register_user,
    deactivate_user,
    get_user_role,
    get_user_info,
)
from backend.utils.auth_dependency import get_current_user_id

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    role_name: str


@router.post("/login")
def login_endpoint(payload: LoginRequest):
    """Public login endpoint - no authentication required."""
    user = login(payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Token is now included in user dict (JWT)
    return {
        "token": user["token"],
        "user_id": user["user_id"],
        "username": user["username"],
        "role": user["role"],
        "message": "Login successful",
    }


@router.post("/register-user")
def register_user_endpoint(
    payload: RegisterRequest,
    current_user_id: int = Depends(get_current_user_id),
):
    """Admin-only endpoint to register new users."""
    role = get_user_role(current_user_id)
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")

    if not register_user(payload.username, payload.password, payload.role_name, current_user_id):
        raise HTTPException(status_code=400, detail="Unable to register user (duplicate or invalid data)")

    return {"message": f"User {payload.username} created successfully"}


@router.patch("/deactivate-user/{user_id}")
def deactivate_user_endpoint(
    user_id: int,
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Admin-only endpoint to deactivate users.
    This preserves all database records (Users and AccessLogs) for audit purposes.
    Revokes all related EmployeeQRCodes while maintaining data integrity.
    """
    role = get_user_role(current_user_id)
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")

    if not deactivate_user(user_id, current_user_id):
        raise HTTPException(status_code=400, detail="Unable to deactivate user (user not found or self-deactivation attempted)")

    return {"message": f"User {user_id} deactivated successfully. All records preserved for audit."}


@router.get("/me")
def get_current_user_endpoint(current_user_id: int = Depends(get_current_user_id)):
    """Get current authenticated user information."""
    user_info = get_user_info(current_user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user_info
