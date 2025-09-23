from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Course, CourseTeaching
from account.serializers import CourseSerializer, CourseTeachingSerializer, EnrollmentSerializer, TeacherSerializer
from student.models import Enrollment, Student
from account.permissions import IsTeacher
from django.db.models import Avg, Max, Min, Count, Q

class TeacherViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsTeacher]
    
    @action(detail=False, methods=['get'])
    def profile(self, request):
        try:
            teacher = request.user.teacher
            serializer = TeacherSerializer(teacher)
            return Response(serializer.data)
        except:
            return Response({"error": "Teacher profile not found"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'], url_path='my-courses')
    def my_courses(self, request):
        teachings = CourseTeaching.objects.filter(teacher=request.user.teacher)
        serializer = CourseTeachingSerializer(teachings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def course_performance(self, request):
        course_id = request.GET.get('course_id')
        standard = request.GET.get('standard')
        academic_year = request.GET.get('academic_year', '2024-2025')
        
        if not course_id or not standard:
            return Response({"error": "course_id and standard parameters are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not CourseTeaching.objects.filter(
            teacher=request.user.teacher,
            course_id=course_id,
            standard=standard,
            academic_year=academic_year
        ).exists():
            return Response({"error": "Not authorized to access this course"}, status=status.HTTP_403_FORBIDDEN)
        
        enrollments = Enrollment.objects.filter(
            course_id=course_id,
            student__standard=standard,
            academic_year=academic_year
        ).select_related('student__user')
        
        course = get_object_or_404(Course, id=course_id)
        
        return Response({
            'course': CourseSerializer(course).data,
            'enrollments': EnrollmentSerializer(enrollments, many=True).data
        })
    
    @action(detail=False, methods=['get'], url_path='my-students')
    def my_students(self, request):
        teachings = CourseTeaching.objects.filter(teacher=request.user.teacher)
        standards = teachings.values_list('standard', flat=True).distinct()
        course_ids = teachings.values_list('course_id', flat=True).distinct()
        
        students = Student.objects.filter(standard__in=standards).select_related('user')
        
        enrollments = Enrollment.objects.filter(
            student__in=students,
            course_id__in=course_ids
        ).select_related('student__user', 'course')
        
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='course-statistics')
    def course_statistics(self, request):
        course_code = request.GET.get('course_code')
        standard = request.GET.get('standard')
        academic_year = request.GET.get('academic_year', '2024-2025')
        
        if not course_code or not standard:
            return Response({"error": "course_code and standard parameters are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            course = Course.objects.get(course_code=course_code)
        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if not CourseTeaching.objects.filter(
            teacher=request.user.teacher,
            course=course,
            standard=standard,
            academic_year=academic_year
        ).exists():
            return Response({"error": "Not authorized to access this course"}, status=status.HTTP_403_FORBIDDEN)
        
        enrollments = Enrollment.objects.filter(
            course=course,
            student__standard=standard,
            academic_year=academic_year
        ).select_related('student__user')
        
        stats = enrollments.aggregate(
            total_students=Count('id'),
            average_marks=Avg('marks_obtained'),
            highest_marks=Max('marks_obtained'),
            lowest_marks=Min('marks_obtained'),
            pass_count=Count('id', filter=Q(marks_obtained__gte=33)),
            fail_count=Count('id', filter=Q(marks_obtained__lt=33))
        )
        
        serializer = EnrollmentSerializer(enrollments, many=True)
        
        response_data = {
            'course': CourseSerializer(course).data,
            'statistics': {
                'total_students': stats['total_students'] or 0,
                'average_marks': float(stats['average_marks'] or 0),
                'highest_marks': float(stats['highest_marks'] or 0),
                'lowest_marks': float(stats['lowest_marks'] or 0),
                'pass_count': stats['pass_count'] or 0,
                'fail_count': stats['fail_count'] or 0,
                'pass_percentage': round((stats['pass_count'] / stats['total_students'] * 100), 2) if stats['total_students'] and stats['total_students'] > 0 else 0
            },
            'student_performance': serializer.data
        }
        
        return Response(response_data)