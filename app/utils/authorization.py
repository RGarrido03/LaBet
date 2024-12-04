from rest_framework.permissions import BasePermission


class HasChartsIncluded(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.tier.charts_included)


class IsAuthenticatedOrNew(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method == "POST" or (request.user and request.user.is_authenticated)
        )
