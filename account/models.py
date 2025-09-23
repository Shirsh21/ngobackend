from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.

class UserManager(BaseUserManager):
    
    def create_user(self, email, name, role, password = None ):
        
        # check if email is present or not
        if not email:
            raise ValueError('Email is required')

        if not role:
            role = 'student'
        
        # email = self.normalize_email(email)
        
        user = self.model(
            email = self.normalize_email(email),
            name = name,
            role = role
        )
        
        user.set_password(password) # hash the password and save
        user.save(using = self._db)
        return user
    
    def create_superuser(self, email, name, password):
        
        user = self.create_user(
            email = email,
            name = name,
            password = password,
            role = 'superadmin'
        )
        
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
        
    


class User(AbstractBaseUser):

    # options for roles
    ROLE_CHOICES = [
        ('student','Student'),
        ('teacher','Teacher'),
        ('superadmin','Super Admin'),
    ]
    # custom fields 
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='student')
    email = models.EmailField(max_length=60, unique=True)
    name = models.CharField(max_length=100)

    # required fields for the user model
    username = None  # removing username as an important field from the user model
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    # username field - used for login
    USERNAME_FIELD = 'email'
    
    # required fields - required while creating an user
    REQUIRED_FIELDS = ['name']
    
    # the custom user manager to handle creation of users and superusers
    objects = UserManager() 
    
    # following functions are required for the model to run
    
    def  __str__(self):
        return self.name

    def has_perm(self, perm, obj=None):
        return self.is_staff
    
    def has_module_perms(self, app_label):
        return True
    



class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, choices=User.ROLE_CHOICES)
    password = models.CharField(max_length=128)  
    
    applied_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Student/Teacher common fields
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    previous_school = models.CharField(max_length=200, null=True, blank=True)
    
    # Student-specific fields
    guardian_name = models.CharField(max_length=100, null=True, blank=True)
    guardian_phone = models.CharField(max_length=15, null=True, blank=True)
    standard = models.CharField(max_length=10, null=True, blank=True)  # Changed from grade_level
    
    # Teacher-specific fields
    department = models.CharField(max_length=100, null=True, blank=True, 
                                 choices=[('primary', 'Primary Section'), ('secondary', 'Secondary Section')])
    
    documents = models.FileField(upload_to='application_docs/', null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"Application from {self.name} ({self.status})"