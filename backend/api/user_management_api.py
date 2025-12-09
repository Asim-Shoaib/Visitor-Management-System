from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict

from backend.services.auth_service import register_user, get_user_role
from backend.database.connection import Database
from backend.utils.auth_dependency import get_current_user_id
from backend.utils.db_logger import log_action

router = APIRouter(prefix="/users", tags=["users"])

db = Database()


class CreateUserRequest(BaseModel):
    username: str
    password: str
    role_name: str  # 'admin' or 'security'


class UserResponse(BaseModel):
    user_id: int
    username: str
    role_name: str
    created_at: str


@router.post("/create")
def create_user_endpoint(
    payload: CreateUserRequest,
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Create a new user. Admin only.
    Requires JWT authentication.
    """
    # Check if current user is admin
    current_role = get_user_role(current_user_id)
    if current_role != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can create users")
    
    success = register_user(
        payload.username,
        payload.password,
        payload.role_name,
        current_user_id
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to create user (username may already exist)")
    
    return {"message": f"User {payload.username} created successfully"}


@router.delete("/{user_id}")
def delete_user_endpoint(
    user_id: int,
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Delete (deactivate) a user. Admin only.
    Note: Actually deactivates user, preserves audit trail.
    Requires JWT authentication.
    """
    # Check if current user is admin
    current_role = get_user_role(current_user_id)
    if current_role != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can delete users")
    
    # Prevent self-deletion
    if user_id == current_user_id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    from backend.services.auth_service import deactivate_user
    success = deactivate_user(user_id, current_user_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to deactivate user")
    
    return {"message": f"User {user_id} deactivated successfully"}


@router.get("/list")
def list_users_endpoint(
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Get list of all users. Admin only.
    Requires JWT authentication.
    """
    # Check if current user is admin
    current_role = get_user_role(current_user_id)
    if current_role != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can view user list")
    
    users = db.fetchall("""
        SELECT 
            u.user_id,
            u.username,
            u.created_at,
            r.role_name
        FROM Users u
        INNER JOIN Roles r ON u.role_id = r.role_id
        ORDER BY u.created_at DESC
    """)
    
    return {"users": users, "count": len(users)}

