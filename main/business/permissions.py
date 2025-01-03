from rest_framework import permissions


class IsBusinessPermission(permissions.BasePermission):
    """Check user is business"""

    def has_permission(self, request, view):
        return request.user.is_business
