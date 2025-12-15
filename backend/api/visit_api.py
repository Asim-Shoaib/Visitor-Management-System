from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.services.visit_service import (
    create_visit,
    update_visit_status,
    get_active_visits,
)
from backend.utils.auth_dependency import get_current_user_id

router = APIRouter(prefix="/visit", tags=["visit"])


class CreateVisitRequest(BaseModel):
    visitor_id: int
    site_id: int
    purpose_details: Optional[str] = None
    host_employee_id: Optional[int] = None


class UpdateStatusRequest(BaseModel):
    status: str


@router.post("/create-visit")
def create_visit_endpoint(
    payload: CreateVisitRequest,
    current_user_id: int = Depends(get_current_user_id),
):
    # Handle empty string for host_employee_id
    host_employee_id = payload.host_employee_id
    if host_employee_id == "" or host_employee_id == 0:
        host_employee_id = None
    
    try:
        visit_id = create_visit(
            visitor_id=payload.visitor_id,
            site_id=payload.site_id,
            purpose_details=payload.purpose_details,
            host_employee_id=host_employee_id,
            requested_by_user_id=current_user_id,
        )
        return {"visit_id": visit_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


@router.patch("/update-status/{visit_id}")
def update_status_endpoint(
    visit_id: int,
    payload: UpdateStatusRequest,
    current_user_id: int = Depends(get_current_user_id),
):
    ok = update_visit_status(
        visit_id=visit_id,
        new_status=payload.status,
        requested_by_user_id=current_user_id,
    )
    if not ok:
        raise HTTPException(
            status_code=400,
            detail="Unable to update status (invalid status or transition, or visit not found).",
        )
    return {"message": "Visit status updated successfully"}


@router.get("/active-visits")
def active_visits_endpoint(current_user_id: int = Depends(get_current_user_id)):
    """Get all active visits. Requires JWT authentication."""
    return get_active_visits()



