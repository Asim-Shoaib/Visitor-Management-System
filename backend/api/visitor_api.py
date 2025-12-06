from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, field_validator
from typing import Optional

from backend.services.visitor_service import add_visitor, search_visitor
from backend.services.scan_service import visitor_checkin, visitor_checkout
from backend.utils.auth_dependency import get_current_user_id
from backend.utils.validator import validate_name

router = APIRouter(prefix="/visitor", tags=["visitor"])


class AddVisitorRequest(BaseModel):
    full_name: str
    cnic: str
    contact_number: Optional[str] = None


@router.post("/add-visitor")
def add_visitor_endpoint(payload: AddVisitorRequest, current_user_id: int = Depends(get_current_user_id)):
    """Add a new visitor. Requires JWT authentication."""
    visitor_id = add_visitor(
        full_name=payload.full_name,
        cnic=payload.cnic,
        contact_number=payload.contact_number,
    )
    if not visitor_id:
        raise HTTPException(
            status_code=400,
            detail="Unable to add visitor (validation failed or CNIC already exists).",
        )
    return {"visitor_id": visitor_id}


@router.get("/search-visitor")
def search_visitor_endpoint(cnic: Optional[str] = None, visitor_id: Optional[int] = None, current_user_id: int = Depends(get_current_user_id)):
    """Search for a visitor. Requires JWT authentication."""
    if not cnic and not visitor_id:
        raise HTTPException(status_code=400, detail="Provide cnic or visitor_id.")

    visitor = search_visitor(cnic=cnic, visitor_id=visitor_id)
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found.")
    return visitor


class CheckInOutRequest(BaseModel):
    qr_code: str
    
    @field_validator('qr_code')
    @classmethod
    def validate_qr_code(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("qr_code cannot be empty")
        return v.strip()


@router.post("/checkin")
def visitor_checkin_endpoint(
    payload: CheckInOutRequest,
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Check in a visitor using their QR code.
    Requires JWT authentication.
    Updates Visits.status to 'checked_in' and sets checkin_time.
    Prevents double check-in.
    Validates QR code format before processing.
    """
    result = visitor_checkin(payload.qr_code, current_user_id)
    
    if not result:
        raise HTTPException(
            status_code=400,
            detail="Unable to check in visitor (QR code not found or invalid)"
        )
    
    if not result.get("success", False):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Check-in failed")
        )
    
    return result


@router.post("/checkout")
def visitor_checkout_endpoint(
    payload: CheckInOutRequest,
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Check out a visitor using their QR code.
    Requires JWT authentication.
    Updates Visits.status to 'checked_out' and sets checkout_time.
    Prevents checkout before check-in.
    Validates QR code format before processing.
    """
    result = visitor_checkout(payload.qr_code, current_user_id)
    
    if not result:
        raise HTTPException(
            status_code=400,
            detail="Unable to check out visitor (QR code not found or invalid)"
        )
    
    if not result.get("success", False):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Check-out failed")
        )
    
    return result


