from rest_framework.permissions import BasePermission, IsAuthenticated


class IsAuthenticatedOrNew(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method == "POST" or (request.user and request.user.is_authenticated)
        )

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)
