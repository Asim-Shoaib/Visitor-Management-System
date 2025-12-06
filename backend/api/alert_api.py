from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.services.alert_service import flag_visitor, get_flagged_visitors
from backend.utils.auth_dependency import get_current_user_id

router = APIRouter(prefix="/alerts", tags=["alerts"])


class FlagVisitorRequest(BaseModel):
    visitor_id: int
    reason: str


@router.post("/flag")
def flag_visitor_endpoint(
    payload: FlagVisitorRequest,
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Flag a visitor for security reasons.
    Creates an alert entry.
    Requires JWT authentication.
    """
    alert = flag_visitor(
        payload.visitor_id,
        payload.reason,
        current_user_id
    )
    
    if not alert:
        raise HTTPException(
            status_code=400,
            detail="Failed to flag visitor (visitor not found or database error)"
        )
    
    return {
        "success": True,
        "message": "Visitor flagged successfully",
        "alert": alert
    }


@router.get("/flagged-visitors")
def get_flagged_visitors_endpoint(
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Get all currently flagged visitors.
    Requires JWT authentication.
    """
    visitors = get_flagged_visitors()
    return {"visitors": visitors, "count": len(visitors)}

