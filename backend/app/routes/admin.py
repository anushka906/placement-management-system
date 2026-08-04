from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.models import Application, ApplicationStatus, Company, Job, StudentProfile, User
from app.schemas import DashboardStats


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats", response_model=DashboardStats)
def dashboard_stats(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return DashboardStats(
        total_students=db.query(StudentProfile).count(),
        total_companies=db.query(Company).count(),
        total_jobs=db.query(Job).count(),
        total_applications=db.query(Application).count(),
        shortlisted=db.query(Application).filter(Application.status == ApplicationStatus.SHORTLISTED).count(),
        selected=db.query(Application).filter(Application.status == ApplicationStatus.SELECTED).count(),
    )
