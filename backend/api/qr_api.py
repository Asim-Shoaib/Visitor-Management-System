from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from typing import Optional

from backend.services.qr_service import (
    generate_employee_qr,
    generate_visitor_qr,
    get_visitor_qr_file,
)
from backend.utils.auth_dependency import get_current_user_id

router = APIRouter(prefix="/qr", tags=["qr"])


class GenerateEmployeeQRRequest(BaseModel):
    employee_id: int


class GenerateVisitorQRRequest(BaseModel):
    visit_id: int
    recipient_email: EmailStr


@router.post("/generate-employee")
def generate_employee_qr_endpoint(
    payload: GenerateEmployeeQRRequest,
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Generate a permanent QR code for an employee.
    Requires authentication.
    Maps to EmployeeQRCodes table.
    """
    result = generate_employee_qr(payload.employee_id, current_user_id)
    
    if not result:
        raise HTTPException(
            status_code=400,
            detail="Unable to generate employee QR code (employee not found or generation failed)"
        )
    
    return {
        "emp_qr_id": result["emp_qr_id"],
        "code_value": result["code_value"],
        "employee_id": result["employee_id"],
        "employee_name": result["employee_name"],
        "message": "Employee QR code generated successfully"
    }


@router.post("/generate-visitor")
def generate_visitor_qr_endpoint(
    payload: GenerateVisitorQRRequest,
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Generate a temporary QR code for a visitor visit.
    Requires authentication.
    Maps to VisitorQRCodes table.
    Emails the QR code as a downloadable link to the recipient.
    """
    result = generate_visitor_qr(payload.visit_id, payload.recipient_email, current_user_id)
    
    if not result:
        raise HTTPException(
            status_code=400,
            detail="Unable to generate visitor QR code (visit not found or generation failed)"
        )
    
    return {
        "visitor_qr_id": result["visitor_qr_id"],
        "code_value": result["code_value"],
        "visit_id": result["visit_id"],
        "visitor_name": result["visitor_name"],
        "download_url": result["download_url"],
        "expiry_date": result["expiry_date"],
        "email_sent": result["email_sent"],
        "message": "Visitor QR code generated successfully"
    }


@router.get("/download/{visitor_qr_id}")
def download_visitor_qr_endpoint(visitor_qr_id: int):
    """
    Download a visitor QR code image by visitor_qr_id.
    Public endpoint (no authentication required).
    Validates that the QR code is active and not expired.
    """
    file_path = get_visitor_qr_file(visitor_qr_id)
    
    if not file_path:
        raise HTTPException(
            status_code=404,
            detail="QR code not found, expired, or revoked"
        )
    
    return FileResponse(
        file_path,
        media_type="image/png",
        filename=f"visitor_qr_{visitor_qr_id}.png"
    )

