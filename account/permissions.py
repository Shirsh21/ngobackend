
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

class IsSuperAdmin(permissions.BasePermission):
    
    def has_permission(self, request, view):
        return request.user.role == 'superadmin'




# """
# Custom Permissions for Role-Based Access Control
# Determine what different user roles can access
# """
# from rest_framework import permissions

# class IsTeacher(permissions.BasePermission):
#     """Allows access only to teachers"""
#     def has_permission(self, request, view):
#         return request.user.role == 'teacher'

# class IsStudent(permissions.BasePermission):
#     """Allows access only to students"""
#     def has_permission(self, request, view):
#         return request.user.role == 'student'

# class IsSuperAdmin(permissions.BasePermission):
#     """Allows access only to superadmins"""
#     def has_permission(self, request, view):
#         return request.user.role == 'superadmin'

# class IsTeacherOrSuperAdmin(permissions.BasePermission):
#     """Allows access to teachers and superadmins"""
#     def has_permission(self, request, view):
#         return request.user.role in ['teacher', 'superadmin']

# class IsStudentOrTeacher(permissions.BasePermission):
#     """Allows access to students and teachers"""
#     def has_permission(self, request, view):
#         return request.user.role in ['student', 'teacher']

# class IsOwnerOrTeacher(permissions.BasePermission):
#     """
#     Object-level permission - students can access only their own data,
#     teachers can access any student's data
#     """
#     def has_object_permission(self, request, view, obj):
#         if request.user.role == 'student':
#             # Check if object belongs to the student
#             if hasattr(obj, 'user'):
#                 return obj.user == request.user
#             elif hasattr(obj, 'student'):
#                 return obj.student.user == request.user
#         elif request.user.role == 'teacher':
#             return True
#         return False