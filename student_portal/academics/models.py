from django.db import models

class AcademicYear(models.Model):
    name = models.CharField(max_length=50, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return self.name

class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"

    def __str__(self):
        return f"{self.name} ({self.code})" if self.code else self.name

class ClassRoom(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="classrooms")
    semester = models.CharField(max_length=30, blank=True)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="classrooms")

    def __str__(self):
        return f"{self.name} - {self.academic_year.name}"

class Section(models.Model):
    name = models.CharField(max_length=50)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name="sections")
    class_teacher = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="class_sections")

    class Meta:
        unique_together = ("name", "classroom")

    def __str__(self):
        return f"{self.classroom.name} - {self.name}"

class Subject(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, blank=True)
    maximum_marks = models.DecimalField(max_digits=6, decimal_places=2, default=100)
    pass_marks = models.DecimalField(max_digits=6, decimal_places=2, default=35)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name="subjects")
    teacher = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, related_name="subjects", null=True, blank=True)

    class Meta:
        unique_together = ("name", "classroom")

    def __str__(self):
        return f"{self.name} ({self.classroom.name})"
