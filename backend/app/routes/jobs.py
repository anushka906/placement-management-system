from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import require_admin
from app.models import Company, Job, User
from app.schemas import JobCreate, JobRead, JobUpdate


router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("", response_model=list[JobRead])
def list_jobs(
    branch: str | None = None,
    min_package: float | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Job).options(joinedload(Job.company))
    if branch:
        query = query.filter(Job.eligible_branches.ilike(f"%{branch}%"))
    if min_package is not None:
        query = query.filter(Job.package_lpa >= min_package)
    if search:
        query = query.filter(Job.title.ilike(f"%{search}%"))
    return query.order_by(Job.created_at.desc()).all()


@router.post("", response_model=JobRead, status_code=status.HTTP_201_CREATED)
def create_job(payload: JobCreate, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    company = db.get(Company, payload.company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    job = Job(**payload.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.put("/{job_id}", response_model=JobRead)
def update_job(
    job_id: int,
    payload: JobUpdate,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    update_data = payload.model_dump(exclude_unset=True)
    if update_data.get("company_id") and not db.get(Company, update_data["company_id"]):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    for field, value in update_data.items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    db.delete(job)
    db.commit()
    return None
