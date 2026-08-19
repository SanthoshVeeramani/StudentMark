from django.db import transaction
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
from datetime import timedelta
from django.core.exceptions import PermissionDenied

from .models import Attendance
from students.models import StudentProfile

def within_edit_window(attendance_obj):
    max_days = getattr(settings, "ATTENDANCE_EDIT_DAYS", 1)
    if max_days is None:
        return True
    cutoff = timezone.now() - timedelta(days=max_days)
    return attendance_obj.created_at >= cutoff

def teacher_can_mark(user, section, subject):
    if user.role == "ADMIN":
        return True
    if user.role != "TEACHER":
        return False
    if getattr(subject, "teacher_id", None) == getattr(user, "id", None):
        return True
    if getattr(section, "class_teacher_id", None) == getattr(user, "id", None):
        return True
    tp = getattr(user, "teacher_profile", None)
    if tp:
        if tp.assigned_sections.filter(pk=section.pk).exists():
            return True
        if tp.assigned_subjects.filter(pk=subject.pk).exists():
            return True
    return False

@transaction.atomic
def bulk_mark_attendance(teacher_user, section, subject, date, statuses, allow_edit=False):
    if not teacher_can_mark(teacher_user, section, subject):
        raise PermissionDenied("You are not authorized to mark attendance for this section or subject.")

    created = 0
    updated = 0
    skipped = 0
    errors = []

    students = StudentProfile.objects.filter(section=section).select_related("user")
    student_map = {s.id: s for s in students}

    existing_qs = Attendance.objects.filter(section=section, subject=subject, date=date, student_id__in=statuses.keys())
    existing_map = { (a.student_id): a for a in existing_qs }

    for student_id, status in statuses.items():
        student = student_map.get(int(student_id))
        if not student:
            skipped += 1
            continue
        existing = existing_map.get(int(student_id))
        if existing:
            if allow_edit or within_edit_window(existing):
                existing.status = status
                existing.marked_by = teacher_user
                existing.save()
                updated += 1
            else:
                skipped += 1
        else:
            Attendance.objects.create(
                student=student,
                subject=subject,
                section=section,
                date=date,
                status=status,
                marked_by=teacher_user,
            )
            created += 1

    return {"created": created, "updated": updated, "skipped": skipped, "errors": errors}

def compute_attendance_summary_for_student(student_profile, start_date, end_date, subject=None):
    qs = Attendance.objects.filter(student=student_profile, date__gte=start_date, date__lte=end_date)
    if subject:
        qs = qs.filter(subject=subject)
    total = qs.count()
    present = qs.filter(status=Attendance.STATUS_PRESENT).count()
    late = qs.filter(status=Attendance.STATUS_LATE).count()
    excused = qs.filter(status=Attendance.STATUS_EXCUSED).count()
    absent = qs.filter(status=Attendance.STATUS_ABSENT).count()

    percentage = Decimal(0)
    if total > 0:
        percentage = (Decimal(present) / Decimal(total)) * Decimal(100)

    return {
        "total_days": total,
        "present": present,
        "absent": absent,
        "late": late,
        "excused": excused,
        "percentage": percentage.quantize(Decimal("0.01")),
    }
