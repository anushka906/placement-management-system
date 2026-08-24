from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import OperationalError

from app.config import get_settings
from app.routes import admin, applications, auth, companies, jobs, students


settings = get_settings()

app = FastAPI(title=settings.app_name)


@app.exception_handler(OperationalError)
async def database_connection_error(_request, _error):
    return JSONResponse(
        status_code=503,
        content={
            "detail": (
                "Database connection failed. Check the MySQL username and password "
                "in backend/.env, then restart the server."
            )
        },
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(students.router, prefix="/api")
app.include_router(companies.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(applications.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


frontend_dir = Path(__file__).resolve().parents[2] / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": settings.app_name}


@app.get("/")
def serve_frontend():
    index_file = frontend_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": settings.app_name}
