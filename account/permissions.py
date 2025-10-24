
from rest_framework import permissions

class IsTeacher(permissions.BasePermission):
    
    def has_permission(self, request, view):
        return request.user.role == 'teacher' 

class IsStudent(permissions.BasePermission):
    
    def has_permission(self, request, view):
        return request.user.role == 'student'
    
class IsTeacherorSuperAdmin(permissions.BasePermission):
    
    def has_permission(self, request, view):
        return request.user.role in ['teacher', 'superadmin']

# class IsSuperAdmin(permissions.BasePermission):
    
#     def has_permission(self, request, view):
#         return request.user.role == 'superadmin'

class IsSchoolAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, "role", "") == "schooladmin")

class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, "role", "") == "superadmin")
