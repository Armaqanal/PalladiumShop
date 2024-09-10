from django.contrib.auth.mixins import UserPassesTestMixin


class RoleBasedPermissionMixin(UserPassesTestMixin):
    allowed_roles = []
    allow_view_only = False

    def test_func(self):
        user = self.request.user

        if not (user.is_authenticated and hasattr(user, 'vendor')):
            return False

        if user.vendor.role in self.allowed_roles:
            return True

        if self.allow_view_only and user.vendor.role == user.vendor.Roles.OPERATOR:
            return self.request.method in ['GET']

        return False
