from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import auth_api, visitor_api, visit_api, qr_api, scan_api


app = FastAPI(title="Visitor Management System API", version="0.7.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_api.router)
app.include_router(visitor_api.router)
app.include_router(visit_api.router)
app.include_router(qr_api.router)
app.include_router(scan_api.router)


@app.get("/")
def root():
    return {"message": "Visitor Management System API", "version": "0.7.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
