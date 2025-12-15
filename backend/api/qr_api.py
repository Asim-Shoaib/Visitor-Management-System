from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional

from backend.services.qr_service import (
    generate_employee_qr,
    generate_visitor_qr,
    get_visitor_qr_file,
    get_employee_qr_file,
    debug_visit_info,
)
from backend.utils.auth_dependency import get_current_user_id
from backend.utils.validator import validate_email, validate_id_format

router = APIRouter(prefix="/qr", tags=["qr"])


class GenerateEmployeeQRRequest(BaseModel):
    employee_id: int
    
    @field_validator('employee_id')
    @classmethod
    def validate_employee_id(cls, v: int) -> int:
        if not validate_id_format(v):
            raise ValueError("employee_id must be a positive integer")
        return v


class GenerateVisitorQRRequest(BaseModel):
    visit_id: int
    recipient_email: str
    
    @field_validator('visit_id')
    @classmethod
    def validate_visit_id(cls, v: int) -> int:
        if not validate_id_format(v):
            raise ValueError("visit_id must be a positive integer")
        return v
    
    @field_validator('recipient_email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not validate_email(v):
            raise ValueError("Invalid email format")
        return v.strip().lower()


@router.post("/generate-employee")
def generate_employee_qr_endpoint(
    payload: GenerateEmployeeQRRequest,
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Generate a permanent QR code for an employee.
    Requires JWT authentication.
    Maps to EmployeeQRCodes table.
    Validates employee_id format before processing.
    """
    # Additional validation (Pydantic handles basic format, but we double-check)
    if not validate_id_format(payload.employee_id):
        raise HTTPException(
            status_code=422,
            detail="Invalid employee_id format. Must be a positive integer."
        )
    
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
        "issue_date": result.get("issue_date"),
        "expiry_date": result.get("expiry_date"),
        "status": result.get("status", "active"),
        "message": "Employee QR code generated successfully"
    }


@router.post("/generate-visitor")
def generate_visitor_qr_endpoint(
    payload: GenerateVisitorQRRequest,
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Generate a temporary QR code for a visitor visit.
    Requires JWT authentication.
    Maps to VisitorQRCodes table.
    Emails the QR code as a downloadable link to the recipient.
    Validates visit_id and recipient_email format before processing.
    """
    # Additional validation (Pydantic handles basic format, but we double-check)
    if not validate_id_format(payload.visit_id):
        raise HTTPException(
            status_code=422,
            detail="Invalid visit_id format. Must be a positive integer."
        )
    
    if not validate_email(payload.recipient_email):
        raise HTTPException(
            status_code=422,
            detail="Invalid email format. Please provide a valid email address."
        )
    
    try:
        result = generate_visitor_qr(payload.visit_id, payload.recipient_email, current_user_id)
    except Exception as e:
        # Log the exception for debugging
        # Error generating visitor QR
        raise HTTPException(
            status_code=500,
            detail=f"Internal error generating visitor QR code: {str(e)}"
        )
    
    if not result:
        raise HTTPException(
            status_code=400,
            detail="Unable to generate visitor QR code. Possible reasons: visit not found, visitor not found, visit status does not allow QR generation, or QR generation failed. Check AccessLogs for details."
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


@router.get("/debug/visit/{visit_id}")
def debug_visit_endpoint(
    visit_id: int,
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Debug endpoint to check visit and visitor information.
    Requires JWT authentication.
    Helps diagnose QR generation issues.
    """
    if not validate_id_format(visit_id):
        raise HTTPException(
            status_code=422,
            detail="Invalid visit_id format. Must be a positive integer."
        )
    
    result = debug_visit_info(visit_id)
    
    if not result:
        raise HTTPException(status_code=500, detail="Debug function returned no result")
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@router.get("/download/employee/{emp_qr_id}")
def download_employee_qr_endpoint(emp_qr_id: int):
    """
    Download an employee QR code image by emp_qr_id.
    Public endpoint (no authentication required).
    Validates emp_qr_id format and that the QR code is active.
    """
    # Validate ID format
    if not validate_id_format(emp_qr_id):
        raise HTTPException(
            status_code=422,
            detail="Invalid emp_qr_id format. Must be a positive integer."
        )
    
    file_path = get_employee_qr_file(emp_qr_id)
    
    if not file_path:
        raise HTTPException(
            status_code=404,
            detail="QR code not found or revoked"
        )
    
    return FileResponse(
        file_path,
        media_type="image/png",
        filename=f"employee_qr_{emp_qr_id}.png"
    )


@router.get("/download/{visitor_qr_id}")
def download_visitor_qr_endpoint(visitor_qr_id: int):
    """
    Download a visitor QR code image by visitor_qr_id.
    Also checks employee QR codes if visitor QR not found (backward compatibility).
    Public endpoint (no authentication required).
    Validates visitor_qr_id format and that the QR code is active and not expired.
    """
    # Validate ID format
    if not validate_id_format(visitor_qr_id):
        raise HTTPException(
            status_code=422,
            detail="Invalid visitor_qr_id format. Must be a positive integer."
        )
    
    # Try visitor QR code first
    file_path = get_visitor_qr_file(visitor_qr_id)
    
    # If not found, try as employee QR code (backward compatibility)
    if not file_path:
        file_path = get_employee_qr_file(visitor_qr_id)
        if file_path:
            return FileResponse(
                file_path,
                media_type="image/png",
                filename=f"employee_qr_{visitor_qr_id}.png"
            )
    
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

