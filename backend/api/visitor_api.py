from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.services.visitor_service import add_visitor, search_visitor

router = APIRouter(prefix="/visitor", tags=["visitor"])


class AddVisitorRequest(BaseModel):
    full_name: str
    cnic: str
    contact_number: Optional[str] = None


@router.post("/add-visitor")
def add_visitor_endpoint(payload: AddVisitorRequest):
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
def search_visitor_endpoint(cnic: Optional[str] = None, visitor_id: Optional[int] = None):
    if not cnic and not visitor_id:
        raise HTTPException(status_code=400, detail="Provide cnic or visitor_id.")

    visitor = search_visitor(cnic=cnic, visitor_id=visitor_id)
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found.")
    return visitor


