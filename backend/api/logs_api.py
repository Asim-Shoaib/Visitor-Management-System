from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from typing import Optional, List, Dict

from backend.services.logs_service import get_access_logs, export_access_logs_to_excel
from backend.utils.auth_dependency import get_current_user_id

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("/access")
def get_access_logs_endpoint(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    action: Optional[str] = Query(None, description="Action type filter"),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Get access logs with optional filters.
    Requires JWT authentication.
    Returns up to 1000 most recent logs.
    """
    # Validate date formats if provided
    if start_date:
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid start_date format. Use YYYY-MM-DD")
    
    if end_date:
        try:
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid end_date format. Use YYYY-MM-DD")
    
    logs = get_access_logs(start_date, end_date, action)
    
    return {
        "logs": logs,
        "count": len(logs),
        "filters": {
            "start_date": start_date,
            "end_date": end_date,
            "action": action
        }
    }


@router.get("/export")
def export_access_logs_endpoint(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    action: Optional[str] = Query(None, description="Action type filter"),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Export access logs to Excel format (.xlsx).
    Requires JWT authentication.
    Returns an Excel file with filtered logs.
    """
    # Validate date formats if provided
    if start_date:
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid start_date format. Use YYYY-MM-DD")
    
    if end_date:
        try:
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid end_date format. Use YYYY-MM-DD")
    
    # Generate Excel file
    excel_file = export_access_logs_to_excel(start_date, end_date, action)
    
    # Generate filename with date range
    filename = "access_logs"
    if start_date and end_date:
        filename += f"_{start_date}_to_{end_date}"
    elif start_date:
        filename += f"_from_{start_date}"
    elif end_date:
        filename += f"_until_{end_date}"
    filename += ".xlsx"
    
    return Response(
        content=excel_file.read(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

