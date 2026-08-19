from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied

ROLE_TEACHER = "TEACHER"
ROLE_ADMIN = "ADMIN"
ROLE_STUDENT = "STUDENT"

class RoleRequiredMixin(AccessMixin):
    allowed_roles = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if self.allowed_roles and request.user.role not in self.allowed_roles:
            raise PermissionDenied("You do not have permission to view this page.")
        return super().dispatch(request, *args, **kwargs)

class TeacherRequiredMixin(RoleRequiredMixin):
    allowed_roles = [ROLE_TEACHER, ROLE_ADMIN]

class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = [ROLE_ADMIN]

class StudentRequiredMixin(RoleRequiredMixin):
    allowed_roles = [ROLE_STUDENT]
