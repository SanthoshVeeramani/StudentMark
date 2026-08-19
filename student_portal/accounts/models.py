from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.core.validators import RegexValidator
from django.conf import settings

ROLE_ADMIN = "ADMIN"
ROLE_TEACHER = "TEACHER"
ROLE_STUDENT = "STUDENT"

ROLE_CHOICES = [
    (ROLE_ADMIN, "Admin"),
    (ROLE_TEACHER, "Teacher"),
    (ROLE_STUDENT, "Student"),
]


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        if "role" not in extra_fields:
            extra_fields["role"] = ROLE_STUDENT
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("role", ROLE_ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


def upload_profile_image(instance, filename):
    return f"profile_images/user_{instance.id}/{filename}"


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, blank=False)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, validators=[
        RegexValidator(r'^\+?\d{7,15}$', 'Enter a valid phone number.')
    ])
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_STUDENT)
    profile_image = models.ImageField(upload_to=upload_profile_image, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["role"]),
        ]

    def __str__(self):
        return f"{self.get_full_name() or self.email}"

    def get_full_name(self):
        return " ".join(filter(None, [self.first_name, self.last_name]))

    def get_short_name(self):
        return self.first_name or self.email


def upload_teacher_photo(instance, filename):
    return f"teachers/{instance.employee_id or instance.user.id}/{filename}"


class TeacherProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="teacher_profile")
    employee_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    department = models.ForeignKey("academics.Department", on_delete=models.SET_NULL, null=True, blank=True, related_name="teachers")
    designation = models.CharField(max_length=150, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    profile_photo = models.ImageField(upload_to=upload_teacher_photo, null=True, blank=True)
    assigned_subjects = models.ManyToManyField("academics.Subject", blank=True, related_name="assigned_teachers")
    assigned_sections = models.ManyToManyField("academics.Section", blank=True, related_name="assigned_teachers")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Teacher Profile"
        verbose_name_plural = "Teacher Profiles"
        indexes = [
            models.Index(fields=["employee_id"]),
        ]

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.email} ({self.employee_id or 'no-id'})"
