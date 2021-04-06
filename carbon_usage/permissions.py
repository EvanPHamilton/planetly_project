from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow a given user to see their carbon usage.
    """

    def has_object_permission(self, request, view, obj):
        # Permissions are only allowed to the owner of the snippet.
        return obj.user == request.user
