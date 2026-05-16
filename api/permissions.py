from rest_framework import permissions


class IsStaffUser(permissions.BasePermission):
    """Allow access only to staff users."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class IsStaffOrOwner(permissions.BasePermission):
    """Allow staff users, or object owners for non-staff users."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_staff:
            return True

        owner_fields = ('recorded_by_id', 'created_by_id')
        for field_name in owner_fields:
            if hasattr(obj, field_name) and getattr(obj, field_name) == user.id:
                return True
        return False
