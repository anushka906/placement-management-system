from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.models import Company, Job, User, UserRole
from app.security import hash_password


def seed_database() -> None:
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == "admin@college.edu").first()
        if not admin:
            admin = User(
                full_name="Placement Officer",
                email="admin@college.edu",
                hashed_password=hash_password("admin123"),
                role=UserRole.ADMIN,
            )
            db.add(admin)

        company = db.query(Company).filter(Company.name == "TechNova Systems").first()
        if not company:
            company = Company(
                name="TechNova Systems",
                website="https://example.com",
                industry="Software",
                location="Bengaluru",
                description="Product engineering company hiring fresh graduates.",
            )
            db.add(company)
            db.flush()

        if not db.query(Job).filter(Job.title == "Backend Developer Intern").first():
            db.add(
                Job(
                    company_id=company.id,
                    title="Backend Developer Intern",
                    job_type="Internship",
                    location="Hybrid",
                    description="Work on REST APIs, database design, and backend services.",
                    required_skills="Python, FastAPI, MySQL, SQLAlchemy",
                    min_cgpa=7.0,
                    eligible_branches="CSE, IT, ECE",
                    package_lpa=6.0,
                )
            )

        db.commit()
        print("Seed complete. Admin login: admin@college.edu / admin123")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
