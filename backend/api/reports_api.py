from fastapi import APIRouter, Depends, Query, Response, HTTPException
from typing import Optional
from datetime import datetime

from backend.services.logs_service import export_access_logs_to_excel
from backend.utils.auth_dependency import get_current_user_id

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/export")
def export_reports_endpoint(
    from_date: Optional[str] = Query(None, alias="from", description="Start date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, alias="to", description="End date (YYYY-MM-DD)"),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Export access logs to Excel format.
    Requires JWT authentication.
    Returns an Excel file with filtered logs.
    """
    # Validate date formats if provided
    if from_date:
        try:
            datetime.strptime(from_date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid 'from' date format. Use YYYY-MM-DD")
    
    if to_date:
        try:
            datetime.strptime(to_date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid 'to' date format. Use YYYY-MM-DD")
    
    # Generate Excel file
    excel_file = export_access_logs_to_excel(from_date, to_date, None)
    
    # Generate filename with date range
    filename = "access_logs"
    if from_date and to_date:
        filename += f"_{from_date}_to_{to_date}"
    elif from_date:
        filename += f"_from_{from_date}"
    elif to_date:
        filename += f"_until_{to_date}"
    filename += ".xlsx"
    
    return Response(
        content=excel_file.read(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

