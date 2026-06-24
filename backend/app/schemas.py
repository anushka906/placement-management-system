from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models import ApplicationStatus, UserRole


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole
    full_name: str


class UserCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserRead(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}


class StudentProfileBase(BaseModel):
    roll_number: str = Field(max_length=40)
    branch: str = Field(max_length=80)
    graduation_year: int = Field(ge=2020, le=2100)
    cgpa: float = Field(ge=0, le=10)
    phone: str | None = Field(default=None, max_length=20)
    resume_url: str | None = Field(default=None, max_length=255)
    skills: str | None = None


class StudentProfileCreate(StudentProfileBase):
    pass


class StudentProfileUpdate(BaseModel):
    branch: str | None = Field(default=None, max_length=80)
    graduation_year: int | None = Field(default=None, ge=2020, le=2100)
    cgpa: float | None = Field(default=None, ge=0, le=10)
    phone: str | None = Field(default=None, max_length=20)
    resume_url: str | None = Field(default=None, max_length=255)
    skills: str | None = None


class StudentProfileRead(StudentProfileBase):
    id: int
    user_id: int
    user: UserRead

    model_config = {"from_attributes": True}


class CompanyBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    website: str | None = Field(default=None, max_length=255)
    industry: str | None = Field(default=None, max_length=100)
    location: str | None = Field(default=None, max_length=120)
    description: str | None = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    website: str | None = Field(default=None, max_length=255)
    industry: str | None = Field(default=None, max_length=100)
    location: str | None = Field(default=None, max_length=120)
    description: str | None = None


class CompanyRead(CompanyBase):
    id: int

    model_config = {"from_attributes": True}


class JobBase(BaseModel):
    company_id: int
    title: str = Field(min_length=2, max_length=140)
    job_type: str = Field(default="Full Time", max_length=60)
    location: str = Field(max_length=120)
    description: str
    required_skills: str | None = None
    min_cgpa: float = Field(default=0, ge=0, le=10)
    eligible_branches: str | None = None
    package_lpa: float | None = Field(default=None, ge=0)
    deadline: datetime | None = None


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    company_id: int | None = None
    title: str | None = Field(default=None, min_length=2, max_length=140)
    job_type: str | None = Field(default=None, max_length=60)
    location: str | None = Field(default=None, max_length=120)
    description: str | None = None
    required_skills: str | None = None
    min_cgpa: float | None = Field(default=None, ge=0, le=10)
    eligible_branches: str | None = None
    package_lpa: float | None = Field(default=None, ge=0)
    deadline: datetime | None = None


class JobRead(JobBase):
    id: int
    created_at: datetime
    company: CompanyRead

    model_config = {"from_attributes": True}


class ApplicationCreate(BaseModel):
    job_id: int
    note: str | None = None


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus


class ApplicationRead(BaseModel):
    id: int
    status: ApplicationStatus
    note: str | None
    applied_at: datetime
    updated_at: datetime
    student: StudentProfileRead
    job: JobRead

    model_config = {"from_attributes": True}


class DashboardStats(BaseModel):
    total_students: int
    total_companies: int
    total_jobs: int
    total_applications: int
    shortlisted: int
    selected: int
