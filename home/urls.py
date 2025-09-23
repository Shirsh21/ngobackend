"""
URL configuration for home project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
"""
URL Configuration - Maps URLs to views
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from account.views import AuthViewSet, AdminViewSet
from student.views import EnrollmentViewSet, StudentPerformanceViewSet
from teacher.views import TeacherViewSet

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from account.views import AuthViewSet, AdminViewSet
from student.views import EnrollmentViewSet, StudentPerformanceViewSet
from teacher.views import TeacherViewSet

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'admin', AdminViewSet, basename='admin')
router.register(r'student-performance', StudentPerformanceViewSet, basename='student-performance')
router.register(r'teacher', TeacherViewSet, basename='teacher')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollments')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]