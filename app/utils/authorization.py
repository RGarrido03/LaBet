from typing import override

from rest_framework.permissions import BasePermission


class IsAuthenticatedOrNew(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method == "POST" or (request.user and request.user.is_authenticated)
        )


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class IsAdminOrNew(IsAdmin):
    @override
    def has_permission(self, request, view):
        return super().has_permission(request, view) or request.method == "POST"
