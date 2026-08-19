from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied
from .models import ExamSubject, Mark, GradeScale
from django.db.models import Sum, F, DecimalField

def validate_mark_values(marks_obtained, internal_marks, practical_marks, max_marks):
    try:
        mo = Decimal(marks_obtained or 0)
        im = Decimal(internal_marks or 0)
        pm = Decimal(practical_marks or 0)
    except InvalidOperation:
        raise ValidationError("Marks must be numeric values.")

    if mo < 0 or im < 0 or pm < 0:
        raise ValidationError("Marks cannot be negative.")
    total = mo + im + pm
    if max_marks is not None and total > Decimal(max_marks):
        raise ValidationError(f"Total marks ({total}) cannot exceed maximum marks ({max_marks}).")
    return mo, im, pm

@transaction.atomic
def enter_mark(entered_by, examination, student_profile, subject, marks_obtained, internal_marks=0, practical_marks=0, remarks=""):
    if examination.is_published and entered_by.role != "ADMIN":
        raise PermissionDenied("Marks are locked for this examination. Only admin can modify.")

    exam_sub = ExamSubject.objects.filter(examination=examination, subject=subject).first()
    max_marks = getattr(exam_sub, "maximum_marks", getattr(subject, "maximum_marks", None))
    mo, im, pm = validate_mark_values(marks_obtained, internal_marks, practical_marks, max_marks)

    mark_obj, created = Mark.objects.update_or_create(
        examination=examination,
        student=student_profile,
        subject=subject,
        defaults={
            "marks_obtained": mo,
            "internal_marks": im,
            "practical_marks": pm,
            "remarks": remarks or "",
            "entered_by": entered_by,
        }
    )
    return mark_obj, created

def compute_student_result_for_examination(examination, student_profile):
    marks = Mark.objects.filter(examination=examination, student=student_profile).select_related("subject")
    total_obtained = sum([m.total_marks for m in marks], Decimal(0))
    exam_subjects = ExamSubject.objects.filter(examination=examination)
    max_total = sum([es.maximum_marks for es in exam_subjects], Decimal(0))
    percentage = Decimal(0)
    if max_total > 0:
        percentage = (Decimal(total_obtained) / Decimal(max_total)) * Decimal(100)

    scales = GradeScale.objects.filter(is_active=True).order_by("-lower_bound")
    grade = None
    for s in scales:
        if percentage >= s.lower_bound and percentage <= s.upper_bound:
            grade = s.name
            break
    if not grade:
        grade = "F"

    failed_subjects = []
    for m in marks:
        es = exam_subjects.filter(subject=m.subject).first()
        pass_marks = es.pass_marks if es else getattr(m.subject, "pass_marks", 0)
        if Decimal(m.total_marks) < Decimal(pass_marks):
            failed_subjects.append(m.subject.name)

    is_pass = len(failed_subjects) == 0

    return {
        "total_obtained": Decimal(total_obtained).quantize(Decimal("0.01")),
        "max_total": Decimal(max_total).quantize(Decimal("0.01")),
        "percentage": Decimal(percentage).quantize(Decimal("0.01")),
        "grade": grade,
        "is_pass": is_pass,
        "failed_subjects": failed_subjects,
        "marks": marks,
    }

def compute_rank_list_for_examination(examination, top_n=None):
    from django.db.models import Sum
    marks_agg = Mark.objects.filter(examination=examination).values("student").annotate(total=Sum(F("marks_obtained") + F("internal_marks") + F("practical_marks"), output_field=DecimalField()))
    results = []
    for entry in marks_agg:
        student_id = entry["student"]
        total = entry["total"] or Decimal(0)
        from students.models import StudentProfile
        sp = StudentProfile.objects.filter(id=student_id).first()
        exam_subjects = ExamSubject.objects.filter(examination=examination)
        max_total = sum([es.maximum_marks for es in exam_subjects], Decimal(0))
        percentage = (Decimal(total) / max_total) * Decimal(100) if max_total > 0 else Decimal(0)
        scales = GradeScale.objects.filter(is_active=True).order_by("-lower_bound")
        grade = next((s.name for s in scales if percentage >= s.lower_bound and percentage <= s.upper_bound), "F")
        results.append({"student": sp, "total": Decimal(total).quantize(Decimal("0.01")), "percentage": percentage.quantize(Decimal("0.01")), "grade": grade})

    results.sort(key=lambda r: (r["total"], r["percentage"]), reverse=True)
    rank = 0
    last_total = None
    for idx, r in enumerate(results, start=1):
        if last_total is None or r["total"] != last_total:
            rank = idx
            last_total = r["total"]
        r["rank"] = rank
    if top_n:
        return results[:top_n]
    return results
