from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from typing import List, Dict

from backend.services.scan_service import (
    scan_employee_qr,
    scan_visitor_qr,
    get_active_alerts,
    get_employee_late_count,
)
from backend.utils.auth_dependency import get_current_user_id
from backend.utils.validator import validate_id_format, validate_scan_status

router = APIRouter(prefix="/scan", tags=["scan"])


class ScanEmployeeRequest(BaseModel):
    emp_qr_id: int
    scan_status: str  # "signin" or "signout"
    
    @field_validator('emp_qr_id')
    @classmethod
    def validate_emp_qr_id(cls, v: int) -> int:
        if not validate_id_format(v):
            raise ValueError("emp_qr_id must be a positive integer")
        return v
    
    @field_validator('scan_status')
    @classmethod
    def validate_scan_status(cls, v: str) -> str:
        if not validate_scan_status(v):
            raise ValueError("scan_status must be 'signin' or 'signout'")
        return v


class ScanVisitorRequest(BaseModel):
    visitor_qr_id: int
    scan_status: str  # "signin" or "signout"
    
    @field_validator('visitor_qr_id')
    @classmethod
    def validate_visitor_qr_id(cls, v: int) -> int:
        if not validate_id_format(v):
            raise ValueError("visitor_qr_id must be a positive integer")
        return v
    
    @field_validator('scan_status')
    @classmethod
    def validate_scan_status(cls, v: str) -> str:
        if not validate_scan_status(v):
            raise ValueError("scan_status must be 'signin' or 'signout'")
        return v


@router.post("/employee")
def scan_employee_endpoint(
    payload: ScanEmployeeRequest,
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Scan an employee QR code.
    Requires JWT authentication.
    Inserts record into EmployeeScanLogs.
    Detects late arrivals (> 9:10 AM).
    Sends email alert if employee is late 3+ times in 30 days.
    Validates emp_qr_id and scan_status format before processing.
    """
    # Additional validation (Pydantic handles basic format, but we double-check)
    if not validate_id_format(payload.emp_qr_id):
        raise HTTPException(
            status_code=422,
            detail="Invalid emp_qr_id format. Must be a positive integer."
        )
    
    if not validate_scan_status(payload.scan_status):
        raise HTTPException(
            status_code=422,
            detail="Invalid scan_status. Must be 'signin' or 'signout'."
        )
    
    result = scan_employee_qr(payload.emp_qr_id, payload.scan_status, current_user_id)
    
    if not result:
        raise HTTPException(
            status_code=400,
            detail="Unable to scan employee QR (QR not found, inactive, or invalid scan status)"
        )
    
    return result


@router.post("/visitor")
def scan_visitor_endpoint(
    payload: ScanVisitorRequest,
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Scan a visitor QR code.
    Requires JWT authentication.
    Inserts record into VisitorScanLogs.
    Updates Visits.status accordingly.
    Creates alert if QR is invalid, expired, or revoked.
    Validates visitor_qr_id and scan_status format before processing.
    """
    # Additional validation (Pydantic handles basic format, but we double-check)
    if not validate_id_format(payload.visitor_qr_id):
        raise HTTPException(
            status_code=422,
            detail="Invalid visitor_qr_id format. Must be a positive integer."
        )
    
    if not validate_scan_status(payload.scan_status):
        raise HTTPException(
            status_code=422,
            detail="Invalid scan_status. Must be 'signin' or 'signout'."
        )
    
    result = scan_visitor_qr(payload.visitor_qr_id, payload.scan_status, current_user_id)
    
    if not result:
        raise HTTPException(
            status_code=400,
            detail="Unable to scan visitor QR (QR not found, expired, revoked, or invalid scan status)"
        )
    
    return result


@router.get("/alerts")
def get_alerts_endpoint(
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Get all active alerts.
    Requires JWT authentication.
    Returns alerts from Alerts table with visitor information.
    """
    alerts = get_active_alerts()
    return {"alerts": alerts, "count": len(alerts)}


@router.get("/employee/late-count/{employee_id}")
def get_employee_late_count_endpoint(
    employee_id: int,
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Get late arrival count for an employee in the last 30 days.
    Requires JWT authentication.
    Includes salary estimate based on recent scans.
    Validates employee_id format before processing.
    """
    if not validate_id_format(employee_id):
        raise HTTPException(
            status_code=422,
            detail="Invalid employee_id format. Must be a positive integer."
        )
    
    result = get_employee_late_count(employee_id)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

