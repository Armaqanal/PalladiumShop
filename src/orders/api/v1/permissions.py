from rest_framework import permissions

class IsStaffUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff


class IsCustomerUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'is_customer') and request.user.is_customer


class IsSuperUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj=None):
        return request.user.is_superuser

