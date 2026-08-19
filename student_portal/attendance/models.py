from django.db import models
from django.utils import timezone

class Attendance(models.Model):
    STATUS_PRESENT = "P"
    STATUS_ABSENT = "A"
    STATUS_LATE = "L"
    STATUS_EXCUSED = "E"

    STATUS_CHOICES = [
        (STATUS_PRESENT, "Present"),
        (STATUS_ABSENT, "Absent"),
        (STATUS_LATE, "Late"),
        (STATUS_EXCUSED, "Excused"),
    ]

    student = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="attendance_records")
    subject = models.ForeignKey("academics.Subject", on_delete=models.CASCADE, related_name="attendance_records")
    section = models.ForeignKey("academics.Section", on_delete=models.CASCADE, related_name="attendance_records")
    date = models.DateField()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    marked_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="marked_attendance")
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "subject", "date")
        indexes = [
            models.Index(fields=["student", "date"]),
            models.Index(fields=["subject", "date"]),
            models.Index(fields=["section", "date"]),
        ]

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.date} - {self.get_status_display()}"
