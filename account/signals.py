
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Application, User
from student.models import Student
from teacher.models import Teacher

@receiver(post_save, sender=Application)
def create_user_and_profile_on_verification(sender, instance, **kwargs):
   
    if instance.status == 'verified':
        
        user = User.objects.create_user(
            email=instance.email,
            name=instance.name,
            password=instance.password,
            role=instance.role
        )
        
        
        if instance.role == 'student':
            Student.objects.create(
                user=user,
                student_id=f"STU{user.id:04d}",
                date_of_birth=instance.date_of_birth,
                address=instance.address,
                phone_number=instance.phone_number,
                guardian_name=instance.guardian_name,
                guardian_phone=instance.guardian_phone,
                standard=instance.standard
            )
        elif instance.role == 'teacher':
            Teacher.objects.create(
                user=user,
                teacher_id=f"TCH{user.id:04d}",
                date_of_birth=instance.date_of_birth,
                address=instance.address,
                phone_number=instance.phone_number,
                department=instance.department
            )