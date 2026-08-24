# Placement Management System

A full-stack campus placement portal for managing student profiles, companies,
job opportunities, and applications from a single dashboard.

## Features

- Student registration and admin login
- JWT-based authentication
- Role-based access control
- Student profile management
- Company management for admins
- Job posting and search
- Student job applications
- Application status tracking: applied, shortlisted, rejected, selected
- Admin dashboard stats
- Alembic migration setup for MySQL

## Tech Stack

```text
Frontend: HTML, CSS, JavaScript
Backend: FastAPI
Database: MySQL
ORM: SQLAlchemy
Migrations: Alembic
Auth: JWT
```

## User Roles

- **Students** can register, maintain their academic profile, browse jobs, apply,
  and track application progress.
- **Admins** can manage companies and job openings, review applications, update
  application statuses, and monitor placement statistics.

## API Overview

| Module | Endpoints |
| --- | --- |
| Authentication | `/api/auth/register`, `/api/auth/login`, `/api/auth/me` |
| Students | `/api/students`, `/api/students/me` |
| Companies | `/api/companies` |
| Jobs | `/api/jobs` |
| Applications | `/api/applications` |
| Dashboard | `/api/admin/stats` |

## Project Structure

```text
placement-management-system/
  backend/
    app/
      routes/
      config.py
      database.py
      dependencies.py
      main.py
      models.py
      schemas.py
      security.py
      seed.py
    alembic/
    alembic.ini
    requirements.txt
    .env.example
  frontend/
    index.html
    styles.css
    app.js
```

## Setup

Create a MySQL database:

```sql
CREATE DATABASE placement_db;
```

Create and activate a virtual environment from the `backend` folder:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy the environment file:

```bash
copy .env.example .env
```

Update `.env` with your MySQL username and password:

```text
DATABASE_URL=mysql+pymysql://root:your_mysql_password@localhost:3306/placement_db
JWT_SECRET_KEY=replace-with-a-long-random-secret
```

Run migrations:

```bash
alembic upgrade head
```

Seed the demo admin, companies, jobs, and student records:

```bash
python -m app.seed
```

Start the app:

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

## Demo Login

If you run the seed script:

```text
Admin email: admin@college.edu
Admin password: admin123
```

Students can register from the UI and then create their profile. Admin access is created through the seed script so users cannot self-register as admins.
