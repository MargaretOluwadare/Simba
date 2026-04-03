from rest_framework.permissions import BasePermission


class IsVendor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == "vendor"


class IsRider(BasePermission):
    def has_permission(self, request):
        return request.user.is_authenticated and request.user.user_type == "rider"


class IsAdmin(BasePermission):
    def has_permission(self, request):
        return request.user.is_authenticated and request.user.user_type == "admin"

class IsValidUser(BasePermission):
    """
    Allows access only to valid users
    """
    
    message = 'Your account is not validated'
    
    def has_permission(self, request, view):
        user = request.user
        return bool(user and getattr(user, 'is_valid', False))