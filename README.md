Student Attendance and Marksheet Portal

This repository contains a Django-based Student Attendance and Marksheet Portal.

Features implemented:
- Custom User model with roles (ADMIN, TEACHER, STUDENT)
- Attendance app with bulk marking, edit-window, permission checks
- Examinations app with configurable GradeScale, mark entry, locks
- PDF marksheet generation (ReportLab)
- Docker + Docker Compose for production deployment (Postgres, Gunicorn, Nginx)

Quick start (development):
1. Copy .env.example to .env and adjust settings
2. python -m venv venv && .\venv\Scripts\Activate.ps1
3. pip install -r requirements.txt
4. python manage.py migrate
5. python manage.py createsuperuser --email admin@example.com
6. python manage.py runserver

Docker (production-like):
- docker-compose up --build

Demo credentials (seeded by seed_data if used):
- Admin: admin@example.com / AdminPass123
- Teacher: teacher@example.com / TeacherPass123
- Students: student1@example.com / Student1Pass123, student2@example.com / Student2Pass123

For full implementation details, consult the project documentation in this repo.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
