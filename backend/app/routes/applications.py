from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_current_user, require_admin, require_student
from app.models import Application, ApplicationStatus, Job, StudentProfile, User, UserRole
from app.schemas import ApplicationCreate, ApplicationRead, ApplicationStatusUpdate


router = APIRouter(prefix="/applications", tags=["Applications"])


@router.get("", response_model=list[ApplicationRead])
def list_applications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = (
        db.query(Application)
        .options(
            joinedload(Application.student).joinedload(StudentProfile.user),
            joinedload(Application.job).joinedload(Job.company),
        )
        .order_by(Application.applied_at.desc())
    )

    if current_user.role == UserRole.STUDENT:
        profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
        if not profile:
            return []
        query = query.filter(Application.student_id == profile.id)

    return query.all()


@router.post("", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
def apply_to_job(
    payload: ApplicationCreate,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Create your student profile first")

    job = db.get(Job, payload.job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    if profile.cgpa < job.min_cgpa:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You do not meet the CGPA criteria")

    application = Application(student_id=profile.id, job_id=payload.job_id, note=payload.note)
    db.add(application)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already applied to this job") from exc

    db.refresh(application)
    return application


@router.patch("/{application_id}/status", response_model=ApplicationRead)
def update_application_status(
    application_id: int,
    payload: ApplicationStatusUpdate,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    application = db.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    application.status = ApplicationStatus(payload.status)
    db.commit()
    db.refresh(application)
    return application
