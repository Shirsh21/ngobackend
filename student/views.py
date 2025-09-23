from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Student, Enrollment
from account.serializers import EnrollmentCreateSerializer, EnrollmentSerializer, StudentSerializer
from account.permissions import IsStudent, IsTeacher
from teacher.models import CourseTeaching

class StudentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], permission_classes=[IsStudent])
    def profile(self, request):
        try:
            student = Student.objects.get(user=request.user)
            serializer = StudentSerializer(student)
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response({"error": "Student profile not found"}, status=status.HTTP_404_NOT_FOUND)

class StudentPerformanceViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], permission_classes=[IsStudent], url_path='my-performance')
    def my_performance(self, request):
        try:
            student = Student.objects.get(user=request.user)
            enrollments = Enrollment.objects.filter(student=student)
            serializer = EnrollmentSerializer(enrollments, many=True)
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response({"error": "Student profile not found"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'], permission_classes=[IsTeacher], url_path='class-results')
    def class_results(self, request):
        standard = request.GET.get('standard')
        course_id = request.GET.get('course_id')
        academic_year = request.GET.get('academic_year', '2024-2025')
        
        if not standard or not course_id:
            return Response({"error": "standard and course_id parameters are required"}, 
                        status=status.HTTP_400_BAD_REQUEST)
        
        if not CourseTeaching.objects.filter(
            teacher=request.user.teacher,
            course_id=course_id,
            standard=standard,
            academic_year=academic_year
        ).exists():
            return Response({"error": "Not authorized to access these results. You don't teach this course to this class."}, 
                        status=status.HTTP_403_FORBIDDEN)
        
        enrollments = Enrollment.objects.filter(
            student__standard=standard,
            course_id=course_id,
            academic_year=academic_year
        ).select_related('student__user', 'course')
        
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)
    
@action(detail=True, methods=['patch', 'post'], permission_classes=[IsTeacher])
def update_marks(self, request, pk=None):
    enrollment = get_object_or_404(Enrollment, pk=pk)
    
    # Check if teacher is authorized to update these marks
    if not CourseTeaching.objects.filter(
        teacher=request.user.teacher,
        course=enrollment.course,
        standard=enrollment.student.standard,
        academic_year=enrollment.academic_year
    ).exists():
        return Response({"error": "Not authorized to update these marks"}, 
                      status=status.HTTP_403_FORBIDDEN)
    
    # Handle both PATCH (update) and POST (create marks)
    if request.method == 'POST' and enrollment.marks_obtained is not None:
        return Response({"error": "Marks already exist. Use PATCH to update."},
                      status=status.HTTP_400_BAD_REQUEST)
    
    serializer = EnrollmentSerializer(enrollment, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Marks updated successfully",
            "data": serializer.data
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[IsTeacher], url_path='student-performance')
    def student_performance(self, request):
        student_id = request.GET.get('student_id')
        
        if not student_id:
            return Response({"error": "student_id parameter is required"}, 
                        status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # FIX: Use the correct field name - student has user_id, not id
            student = Student.objects.get(user_id=student_id)
            enrollments = Enrollment.objects.filter(student=student)
            
            # Check if teacher teaches any of this student's courses
            student_standards = enrollments.values_list('student__standard', flat=True).distinct()
            authorized = CourseTeaching.objects.filter(
                teacher=request.user.teacher,
                standard__in=student_standards
            ).exists()
            
            if not authorized:
                return Response({"error": "Not authorized to view this student's performance"}, 
                            status=status.HTTP_403_FORBIDDEN)
            
            serializer = EnrollmentSerializer(enrollments, many=True)
            return Response(serializer.data)
            
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
        
# class EnrollmentViewSet(viewsets.ModelViewSet):
#     queryset = Enrollment.objects.all()
#     permission_classes = [IsAuthenticated, IsTeacher]
#     serializer_class = EnrollmentCreateSerializer
    
#     def create(self, request):
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             enrollment = serializer.save()
#             return Response(EnrollmentSerializer(enrollment).data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = EnrollmentCreateSerializer
    
    def list(self, request):
        # Simple response without related fields first
        enrollments = self.get_queryset()
        data = []
        for enrollment in enrollments:
            data.append({
                "enrollment_id": enrollment.id,
                "student": enrollment.student_id,  # Just use ID instead of name
                "course": enrollment.course_id,    # Just use ID instead of name
                "enrollment_date": enrollment.enrollment_date,
                "academic_year": enrollment.academic_year,
                "grade": enrollment.grade,
                "marks_obtained": enrollment.marks_obtained,
                "total_marks": enrollment.total_marks,

            })
        return Response(data)