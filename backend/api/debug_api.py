from fastapi import APIRouter
from fastapi.responses import JSONResponse
from backend.database.connection import Database

router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/db-status")
def db_status():
    db = Database()
    try:
        # Try a simple query to verify connectivity
        row = db.fetchone("SELECT 1 as ok")
        if row and row.get("ok") == 1:
            return JSONResponse({"status": "ok"})
        return JSONResponse({"status": "unavailable"}, status_code=503)
    except Exception as e:
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=503)
