from fastapi import APIRouter, Query, Depends, Response, HTTPException
from typing import Optional
from datetime import datetime

from backend.services.site_service import (
    get_all_sites, 
    get_all_employees, 
    get_active_employees_count,
    get_signed_in_employees,
    get_employee_status,
    get_employee_logs,
    get_all_departments,
    create_employee,
    create_site,
    calculate_employee_salary,
    export_salary_report_to_excel
)
from backend.utils.auth_dependency import get_current_user_id
from backend.services.auth_service import get_user_role
from pydantic import BaseModel

router = APIRouter(prefix="/site", tags=["site"])


@router.get("/list")
def get_sites_endpoint(current_user_id: int = Depends(get_current_user_id)):
    """Get all sites. Requires JWT authentication."""
    sites = get_all_sites()
    if sites is None:
        raise HTTPException(status_code=500, detail="Failed to fetch sites")
    return {"sites": sites}


class CreateSiteRequest(BaseModel):
    site_name: str
    address: Optional[str] = None


@router.post("/create-site")
def create_site_endpoint(
    payload: CreateSiteRequest,
    current_user_id: int = Depends(get_current_user_id),
):
    """Create a new site. Admin only."""
    # Check if current user is admin
    role = get_user_role(current_user_id)
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    
    site_id = create_site(
        payload.site_name,
        payload.address,
        current_user_id
    )
    
    if not site_id:
        raise HTTPException(status_code=400, detail="Failed to create site. Check that site_name is valid and not duplicate.")
    
    return {"message": f"Site {payload.site_name} created successfully", "site_id": site_id}


@router.get("/employees")
def get_employees_endpoint(current_user_id: int = Depends(get_current_user_id)):
    """Get all employees. Requires JWT authentication."""
    employees = get_all_employees()
    if employees is None:
        raise HTTPException(status_code=500, detail="Failed to fetch employees")
    return {"employees": employees}


@router.get("/active-employees-count")
def get_active_employees_count_endpoint(current_user_id: int = Depends(get_current_user_id)):
    """Get count of currently signed-in employees. Requires JWT authentication."""
    return {"active_employees_count": get_active_employees_count()}


@router.get("/employees/signed-in")
def get_signed_in_employees_endpoint(current_user_id: int = Depends(get_current_user_id)):
    """Get list of currently signed-in employees. Requires JWT authentication."""
    employees = get_signed_in_employees()
    if employees is None:
        raise HTTPException(status_code=500, detail="Failed to fetch signed-in employees")
    return {"employees": employees}


@router.get("/employees/{employee_id}/status")
def get_employee_status_endpoint(employee_id: int, current_user_id: int = Depends(get_current_user_id)):
    """Get current status of an employee. Requires JWT authentication."""
    status = get_employee_status(employee_id)
    if not status:
        raise HTTPException(status_code=404, detail="Employee not found")
    return status


@router.get("/employees/{employee_id}/logs")
def get_employee_logs_endpoint(employee_id: int, days: int = Query(30, ge=1, le=365), current_user_id: int = Depends(get_current_user_id)):
    """Get employee logs for last N days. Requires JWT authentication."""
    logs = get_employee_logs(employee_id, days)
    return {"logs": logs, "count": len(logs), "days": days}


@router.get("/departments")
def get_departments_endpoint(current_user_id: int = Depends(get_current_user_id)):
    """Get all departments. Requires JWT authentication."""
    return {"departments": get_all_departments()}


class CreateEmployeeRequest(BaseModel):
    name: str
    hourly_rate: float
    department_id: int


@router.post("/employees/create")
def create_employee_endpoint(
    payload: CreateEmployeeRequest,
    current_user_id: int = Depends(get_current_user_id),
):
    """Create a new employee. Admin only."""
    # Check if current user is admin
    role = get_user_role(current_user_id)
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    
    employee_id = create_employee(
        payload.name,
        payload.hourly_rate,
        payload.department_id,
        current_user_id
    )
    
    if not employee_id:
        raise HTTPException(status_code=400, detail="Failed to create employee. Check that name is valid, hourly_rate is non-negative, and department_id exists.")
    
    return {"message": f"Employee {payload.name} created successfully", "employee_id": employee_id}


@router.get("/employees/{employee_id}/salary")
def calculate_salary_endpoint(
    employee_id: int,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user_id: int = Depends(get_current_user_id),
):
    """Calculate employee salary for a date range. Admin only."""
    # Check if current user is admin
    role = get_user_role(current_user_id)
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    
    result = calculate_employee_salary(employee_id, start_date, end_date)
    
    if not result:
        raise HTTPException(status_code=404, detail="Employee not found or invalid date range")
    
    return result


@router.get("/employees/{employee_id}/salary/export")
def export_salary_report_endpoint(
    employee_id: int,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user_id: int = Depends(get_current_user_id),
):
    """Export employee salary report to Excel. Admin only."""
    # Check if current user is admin
    role = get_user_role(current_user_id)
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    
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
    excel_file = export_salary_report_to_excel(employee_id, start_date, end_date)
    
    if not excel_file:
        raise HTTPException(status_code=404, detail="Employee not found or invalid date range")
    
    # Get employee name for filename
    from backend.services.site_service import get_all_employees
    employees = get_all_employees()
    employee = next((e for e in employees if e['employee_id'] == employee_id), None)
    employee_name = employee['name'].replace(' ', '_') if employee else f"employee_{employee_id}"
    
    # Generate filename
    filename = f"salary_report_{employee_name}"
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

