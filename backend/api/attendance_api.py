from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.services.scan_service import verify_qr_code, scan_employee_qr
from backend.utils.auth_dependency import get_current_user_id

router = APIRouter(prefix="/attendance", tags=["attendance"])


class ScanRequest(BaseModel):
    qr_code: str


@router.post("/scan")
def attendance_scan_endpoint(
    payload: ScanRequest,
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Scan employee QR code for attendance (check-in/check-out).
    Validates employee, toggles signed_in status, inserts timestamp.
    Requires JWT authentication.
    """
    # Verify QR code
    verification = verify_qr_code(payload.qr_code, current_user_id)
    
    if not verification or verification.get('type') != 'employee':
        raise HTTPException(
            status_code=400,
            detail="Invalid QR code or not an employee QR code"
        )
    
    if verification.get('status') != 'valid':
        raise HTTPException(
            status_code=400,
            detail=f"QR code is {verification.get('status')}"
        )
    
    # Get employee QR ID
    emp_qr_id = verification.get('linked_id')
    if not emp_qr_id:
        raise HTTPException(status_code=400, detail="Could not identify employee QR")
    
    # Determine current status (check last scan)
    from backend.database.connection import Database
    db = Database()
    last_scan = db.fetchone("""
        SELECT scan_status, timestamp
        FROM EmployeeScanLogs
        WHERE emp_qr_id = %s
        ORDER BY timestamp DESC
        LIMIT 1
    """, (emp_qr_id,))
    
    # Toggle status
    if last_scan and last_scan['scan_status'] == 'signin':
        new_status = 'signout'
    else:
        new_status = 'signin'
    
    # Perform scan
    result = scan_employee_qr(emp_qr_id, new_status, current_user_id)
    
    if not result:
        raise HTTPException(status_code=400, detail="Failed to process attendance scan")
    
    return {
        "status": "checked_in" if new_status == "signin" else "checked_out",
        "time": result.get('timestamp'),
        "employee": {
            "id": result.get('employee_id'),
            "name": result.get('employee_name'),
            "dept": "Unknown"  # Would need to join with Departments
        }
    }

