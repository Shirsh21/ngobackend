from django.db import models
from account.models import User
from teacher.models import Course

class Student(models.Model):
    STANDARD_CHOICES = [
        ('1', 'Class 1'),
        ('2', 'Class 2'),
        ('3', 'Class 3'),
        ('4', 'Class 4'),
        ('5', 'Class 5'),
        ('6', 'Class 6'),
        ('7', 'Class 7'),
        ('8', 'Class 8'),
        ('9', 'Class 9'),
        ('10', 'Class 10'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    student_id = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    guardian_name = models.CharField(max_length=100, null=True, blank=True)
    guardian_phone = models.CharField(max_length=15, null=True, blank=True)
    enrollment_date = models.DateField(auto_now_add=True)
    standard = models.CharField(max_length=2, choices=STANDARD_CHOICES)  
    
    courses = models.ManyToManyField(Course, through='Enrollment', related_name='students_enrolled')
        
    def __str__(self):
        return f"{self.user.name} ({self.student_id}) - Class {self.standard}"

class Enrollment(models.Model):
   
    GRADE_CHOICES = [
        ('A1', 'A1 (91-100)'),
        ('A2', 'A2 (81-90)'),
        ('B1', 'B1 (71-80)'),
        ('B2', 'B2 (61-70)'),
        ('C1', 'C1 (51-60)'),
        ('C2', 'C2 (41-50)'),
        ('D', 'D (33-40)'),
        ('E', 'E (21-32)'),
        ('F', 'F (Below 21)'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateField(auto_now_add=True)
    academic_year = models.CharField(max_length=9, default='2024-2025')
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, blank=True, null=True)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    
    class Meta:
        unique_together = ('student', 'course', 'academic_year')
    
    def __str__(self):
        return f"{self.student.user.name} - {self.course.course_name} ({self.academic_year})"
    
    
    
    
    
class Fee(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fees')
    #fee
    