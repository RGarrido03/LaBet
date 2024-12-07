from rest_framework.permissions import BasePermission


class IsAuthenticatedOrNew(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method == "POST" or (request.user and request.user.is_authenticated)
        )
