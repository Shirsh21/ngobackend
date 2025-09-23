from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Application
from student.models import Student, Enrollment
from teacher.models import Teacher, Course, CourseTeaching

class UserLoginSerializer(serializers.Serializer):
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            user = authenticate(email=email, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("User account is disabled.")
                return user
            raise serializers.ValidationError("Invalid email or password.")
        raise serializers.ValidationError("Must include 'email' and 'password'.")

class ApplicationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Application
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
            'status': {'read_only': True},
            'applied_on': {'read_only': True}
        }

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role', 'date_joined']

class StudentSerializer(serializers.ModelSerializer):
   
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Student
        fields = '__all__'

class TeacherSerializer(serializers.ModelSerializer):
   
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Teacher
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
  
    class Meta:
        model = Course
        fields = '__all__'

class CourseTeachingSerializer(serializers.ModelSerializer):

    teacher_name = serializers.CharField(source='teacher.user.name', read_only=True)
    course_name = serializers.CharField(source='course.course_name', read_only=True)
    
    class Meta:
        model = CourseTeaching
        fields = '__all__'

class EnrollmentSerializer(serializers.ModelSerializer):
    
    student_name = serializers.CharField(source='student.user.name', read_only=True)
    course_name = serializers.CharField(source='course.course_name', read_only=True)
    
    class Meta:
        model = Enrollment
        fields = '__all__'

# class EnrollmentSerializer(serializers.ModelSerializer):
#     student_name = serializers.CharField(source='student.user.name', read_only=True)
#     course_name = serializers.CharField(source='course.course_name', read_only=True)
    
#     class Meta:
#         model = Enrollment
#         fields = ['id', 'student', 'student_name', 'course', 'course_name', 
#                  'enrollment_date', 'academic_year', 'grade', 'marks_obtained', 
#                  'total_marks', 'attendance_percentage', 'status']
#         extra_kwargs = {
#             'id': {'read_only': True}
#         }
        
class EnrollmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['student', 'course', 'academic_year', 'marks_obtained', 'total_marks', 'grade']