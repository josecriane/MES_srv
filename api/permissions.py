from rest_framework import permissions
import models

"""
Custom permission to only allow owners of an object to edit it.
"""
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.owner == request.user

class IsOwnerOrIsTheSameDevice(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user:
            return True

        if request.data.get("uid", None) == obj.uid:
            return True

        return False

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class Always(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return True

    def has_permission(self, request, view):
        return True