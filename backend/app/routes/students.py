from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_current_user, require_admin, require_student
from app.models import StudentProfile, User
from app.schemas import StudentProfileCreate, StudentProfileRead, StudentProfileUpdate


router = APIRouter(prefix="/students", tags=["Students"])


@router.get("", response_model=list[StudentProfileRead])
def list_students(
    branch: str | None = None,
    min_cgpa: float | None = None,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(StudentProfile).options(joinedload(StudentProfile.user))
    if branch:
        query = query.filter(StudentProfile.branch.ilike(f"%{branch}%"))
    if min_cgpa is not None:
        query = query.filter(StudentProfile.cgpa >= min_cgpa)
    return query.order_by(StudentProfile.cgpa.desc()).all()


@router.get("/me", response_model=StudentProfileRead)
def my_profile(current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    profile = (
        db.query(StudentProfile)
        .options(joinedload(StudentProfile.user))
        .filter(StudentProfile.user_id == current_user.id)
        .first()
    )
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not created")
    return profile


@router.post("/me", response_model=StudentProfileRead, status_code=status.HTTP_201_CREATED)
def create_my_profile(
    payload: StudentProfileCreate,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    existing_profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if existing_profile:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Profile already exists")

    profile = StudentProfile(user_id=current_user.id, **payload.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.put("/me", response_model=StudentProfileRead)
def update_my_profile(
    payload: StudentProfileUpdate,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not created")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile
