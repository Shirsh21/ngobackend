from django.db import models
from account.models import User

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    teacher_id = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    hire_date = models.DateField(auto_now_add=True)
    department = models.CharField(max_length=100, choices=[('primary', 'Primary Section'), ('secondary', 'Secondary Section')])
    
    def __str__(self):
        return f"{self.user.name} ({self.teacher_id})"

class Course(models.Model):
    
    course_code = models.CharField(max_length=10, unique=True)
    course_name = models.CharField(max_length=100)  
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    teachers = models.ManyToManyField(Teacher, through='CourseTeaching', related_name='courses_taught')
    
    def __str__(self):
        return f"{self.course_name}"

class CourseTeaching(models.Model):
    
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
    
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    
    standard = models.CharField(max_length=2, choices=STANDARD_CHOICES)
    
    academic_year = models.CharField(max_length=9, default='2024-2025')
    is_class_teacher = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('teacher', 'course', 'standard', 'academic_year')
    
    def __str__(self):
        return f"{self.teacher.user.name} teaches {self.course.course_name} to Class {self.standard}"