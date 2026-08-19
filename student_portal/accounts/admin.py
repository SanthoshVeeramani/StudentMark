from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, TeacherProfile

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ("email", "get_full_name", "role", "is_staff", "is_active", "created_at")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("email", "password")} ),
        ("Personal info", {"fields": ("first_name", "last_name", "phone_number", "profile_image")} ),
        ("Permissions", {"fields": ("role", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")} ),
        ("Important dates", {"fields": ("created_at", "updated_at")} ),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "role"),
        }),
    )

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "employee_id", "department", "designation", "joining_date")
    search_fields = ("user__email", "user__first_name", "user__last_name", "employee_id")
    list_filter = ("department",)
    filter_horizontal = ("assigned_subjects", "assigned_sections")
    readonly_fields = ("created_at", "updated_at")
