from django.db import models
from django.utils import timezone
from django.conf import settings

def upload_student_photo(instance, filename):
    return f"students/{instance.admission_number or 'unknown'}/{filename}"

class StudentProfile(models.Model):
    GENDER_MALE = "M"
    GENDER_FEMALE = "F"
    GENDER_OTHER = "O"
    GENDER_CHOICES = [
        (GENDER_MALE, "Male"),
        (GENDER_FEMALE, "Female"),
        (GENDER_OTHER, "Other"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_profile")
    admission_number = models.CharField(max_length=30, unique=True)
    roll_number = models.CharField(max_length=10)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    address = models.TextField(blank=True)
    guardian_name = models.CharField(max_length=255, blank=True)
    guardian_phone = models.CharField(max_length=20, blank=True)
    classroom = models.ForeignKey("academics.ClassRoom", null=True, blank=True, on_delete=models.SET_NULL, related_name="students")
    section = models.ForeignKey("academics.Section", null=True, blank=True, on_delete=models.SET_NULL, related_name="students")
    admission_date = models.DateField(default=timezone.now)
    profile_photo = models.ImageField(upload_to=upload_student_photo, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Student Profile"
        verbose_name_plural = "Student Profiles"
        indexes = [
            models.Index(fields=["admission_number"]),
            models.Index(fields=["roll_number"]),
        ]

    def __str__(self):
        return f"{self.admission_number} - {self.user.get_full_name() or self.user.email}"
