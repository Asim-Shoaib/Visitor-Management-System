from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from backend.api import auth_api, visitor_api, visit_api, qr_api, scan_api, logs_api, site_api, email_api, attendance_api, user_management_api, alert_api, reports_api

app = FastAPI(title="Visitor Management System API", version="1.0.0")

# Path to frontend build
FRONTEND_PATH = os.path.join(os.path.dirname(__file__), "static")

# Serve /assets (JS, CSS)
app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_PATH, "assets")), name="assets")

# Serve root index.html
@app.get("/", include_in_schema=False)
def serve_frontend():
    index_file = os.path.join(FRONTEND_PATH, "index.html")
    return FileResponse(index_file)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_api.router)
app.include_router(visitor_api.router)
app.include_router(visit_api.router)
app.include_router(qr_api.router)
app.include_router(scan_api.router)
app.include_router(logs_api.router)
app.include_router(site_api.router)
app.include_router(email_api.router)
app.include_router(attendance_api.router)
app.include_router(user_management_api.router)
app.include_router(alert_api.router)
app.include_router(reports_api.router)

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
