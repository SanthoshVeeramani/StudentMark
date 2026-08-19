from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class Examination(models.Model):
    name = models.CharField(max_length=255)
    academic_year = models.ForeignKey("academics.AcademicYear", on_delete=models.PROTECT, related_name="examinations")
    classroom = models.ForeignKey("academics.ClassRoom", on_delete=models.PROTECT, related_name="examinations")
    start_date = models.DateField()
    end_date = models.DateField()
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.academic_year})"

class ExamSubject(models.Model):
    examination = models.ForeignKey(Examination, on_delete=models.CASCADE, related_name="exam_subjects")
    subject = models.ForeignKey("academics.Subject", on_delete=models.PROTECT, related_name="exam_subjects")
    exam_date = models.DateField()
    maximum_marks = models.DecimalField(max_digits=6, decimal_places=2, default=100)
    pass_marks = models.DecimalField(max_digits=6, decimal_places=2, default=35)

    class Meta:
        unique_together = ("examination", "subject")

    def __str__(self):
        return f"{self.subject} - {self.examination.name}"

class GradeScale(models.Model):
    name = models.CharField(max_length=10, help_text="Grade label, e.g., A+, A, B+")
    lower_bound = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    upper_bound = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Lower order shows first in admin")

    class Meta:
        ordering = ["-lower_bound"]

    def __str__(self):
        return f"{self.name}: {self.lower_bound}-{self.upper_bound}"

class Mark(models.Model):
    examination = models.ForeignKey(Examination, on_delete=models.CASCADE, related_name="marks")
    student = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="marks")
    subject = models.ForeignKey("academics.Subject", on_delete=models.PROTECT)
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    internal_marks = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    practical_marks = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    remarks = models.TextField(blank=True)
    entered_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="entered_marks")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("examination", "student", "subject")
        indexes = [
            models.Index(fields=["examination", "student"]),
            models.Index(fields=["subject", "student"]),
        ]

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.examination.name}"

    @property
    def total_marks(self):
        return (self.marks_obtained or Decimal(0)) + (self.internal_marks or Decimal(0)) + (self.practical_marks or Decimal(0))

    def get_exam_subject(self):
        return getattr(self, "_cached_exam_subject", None) or ExamSubject.objects.filter(examination=self.examination, subject=self.subject).first()

    @property
    def maximum_marks(self):
        es = self.get_exam_subject()
        if es:
            return es.maximum_marks
        return getattr(self.subject, "maximum_marks", Decimal(100))

    @property
    def pass_marks(self):
        es = self.get_exam_subject()
        if es:
            return es.pass_marks
        return getattr(self.subject, "pass_marks", Decimal(0))

    @property
    def percentage(self):
        max_marks = Decimal(self.maximum_marks or 0)
        if max_marks == 0:
            return Decimal(0)
        return (Decimal(self.total_marks) / max_marks) * Decimal(100)

    def is_pass(self):
        return Decimal(self.total_marks) >= Decimal(self.pass_marks or 0)

    def compute_grade(self):
        from .models import GradeScale
        percent = Decimal(self.percentage or 0)
        scales = GradeScale.objects.filter(is_active=True).order_by("-lower_bound")
        for s in scales:
            if percent >= s.lower_bound and percent <= s.upper_bound:
                return s.name
        return "F"
