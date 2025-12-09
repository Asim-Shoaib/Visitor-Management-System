from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional

from backend.services.email_service import send_qr_code_email, check_and_send_late_alerts
from backend.utils.auth_dependency import get_current_user_id

router = APIRouter(prefix="/email", tags=["email"])


class SendQRRequest(BaseModel):
    email: EmailStr
    visitor_id: int
    qr_code_data: str


class AlertLateRequest(BaseModel):
    employee_id: Optional[int] = None  # If None, checks all employees


@router.post("/send-qr")
def send_qr_email_endpoint(
    payload: SendQRRequest,
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Send QR code as email attachment.
    Requires JWT authentication.
    """
    result = send_qr_code_email(
        payload.email,
        payload.visitor_id,
        payload.qr_code_data,
        current_user_id
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])
    
    return result


@router.post("/alert-late")
def alert_late_endpoint(
    payload: AlertLateRequest,
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Check for late arrivals and send alerts to admin.
    Evaluates check-in times (after 9:00 AM, 3+ times in last 7 days).
    Requires JWT authentication (admin only recommended).
    """
    result = check_and_send_late_alerts(current_user_id)
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])
    
    return result

