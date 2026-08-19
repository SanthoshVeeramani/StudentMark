from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User, ROLE_ADMIN, ROLE_TEACHER, ROLE_STUDENT
from academics.models import AcademicYear, Department, ClassRoom, Section, Subject
from students.models import StudentProfile
from examinations.models import Examination, ExamSubject
from examinations.models import GradeScale
from examinations.services import enter_mark

class Command(BaseCommand):
    help = "Seed initial demo data"

    def handle(self, *args, **options):
        if not User.objects.filter(email="admin@example.com").exists():
            admin = User.objects.create_superuser(email="admin@example.com", password="AdminPass123")
            self.stdout.write("Created admin admin@example.com / AdminPass123")
        else:
            admin = User.objects.get(email="admin@example.com")
            self.stdout.write("Admin exists")

        teacher_user, created = User.objects.get_or_create(email="teacher@example.com", defaults={
            "first_name": "Demo", "last_name": "Teacher", "role": ROLE_TEACHER, "is_active": True
        })
        if created:
            teacher_user.set_password("TeacherPass123")
            teacher_user.save()
            self.stdout.write("Created teacher teacher@example.com / TeacherPass123")

        student_users = []
        for i in range(1, 3):
            email = f"student{i}@example.com"
            user, created = User.objects.get_or_create(email=email, defaults={"role": ROLE_STUDENT, "first_name": f"Student{i}"})
            if created:
                user.set_password(f"Student{i}Pass123")
                user.save()
            student_users.append(user)

        ay, _ = AcademicYear.objects.get_or_create(name="2026-2027", defaults={"start_date": "2026-06-01", "end_date": "2027-05-31", "is_current": True})
        dept, _ = Department.objects.get_or_create(name="Science", code="SCI")
        classroom, _ = ClassRoom.objects.get_or_create(name="BSc CS", department=dept, semester="1", academic_year=ay)
        section, _ = Section.objects.get_or_create(name="A", classroom=classroom, class_teacher=teacher_user)
        subjects = []
        for name in ["Mathematics", "Programming", "Database"]:
            subj, _ = Subject.objects.get_or_create(name=name, classroom=classroom, defaults={"maximum_marks": 100, "pass_marks": 35, "teacher": teacher_user})
            subjects.append(subj)

        for idx, user in enumerate(student_users, start=1):
            sp, _ = StudentProfile.objects.get_or_create(user=user, defaults={
                "admission_number": f"ADM{100+idx}",
                "roll_number": str(idx),
                "classroom": classroom,
                "section": section,
            })

        exam, _ = Examination.objects.get_or_create(name="Midterm 1", academic_year=ay, classroom=classroom, start_date=ay.start_date, end_date=ay.end_date)
        for subj in subjects:
            es, _ = ExamSubject.objects.get_or_create(examination=exam, subject=subj, defaults={"exam_date": ay.start_date, "maximum_marks": 100, "pass_marks": 35})

        if not GradeScale.objects.exists():
            GradeScale.objects.bulk_create([
                GradeScale(name="A+", lower_bound=90, upper_bound=100, is_active=True),
                GradeScale(name="A", lower_bound=80, upper_bound=89.99, is_active=True),
                GradeScale(name="B+", lower_bound=70, upper_bound=79.99, is_active=True),
                GradeScale(name="B", lower_bound=60, upper_bound=69.99, is_active=True),
                GradeScale(name="C", lower_bound=50, upper_bound=59.99, is_active=True),
                GradeScale(name="D", lower_bound=40, upper_bound=49.99, is_active=True),
                GradeScale(name="F", lower_bound=0, upper_bound=39.99, is_active=True),
            ])
            self.stdout.write("Created default grade scales.")

        students = StudentProfile.objects.filter(classroom=classroom)
        if students.exists():
            for subj in subjects:
                enter_mark(admin, exam, students[0], subj, 78, 10, 0)

        self.stdout.write(self.style.SUCCESS("Demo data seeded."))
