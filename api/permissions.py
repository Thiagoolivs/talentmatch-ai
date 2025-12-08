from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsCompanyUser(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_company()


class IsCandidateUser(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_candidate()


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin_user()


class IsCompanyOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_company()
    
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if hasattr(obj, 'company'):
            return obj.company == request.user
        return request.user.is_company()


class IsCandidateOrCompanyOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_candidate() and obj.candidate == request.user:
            return True
        if request.user.is_company() and obj.job.company == request.user:
            return True
        if request.user.is_admin_user():
            return True
        return False
