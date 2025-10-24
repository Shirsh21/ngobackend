from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator


class UserManager(BaseUserManager):
    def create_user(self, email, name, role, password=None):
        if not email:
            raise ValueError("Email is required")
        if not role:
            role = "student"

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            role=role,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(
            email=email,
            name=name,
            password=password,
            role="superadmin",
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    ROLE_CHOICES = [
        ("student", "Student"),
        ("teacher", "Teacher"),
        ("schooladmin", "School Admin"),
        ("superadmin", "Super Admin"),
    ]
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default="student")
    email = models.EmailField(max_length=60, unique=True)
    name = models.CharField(max_length=100)

    username = None
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = UserManager()

    def __str__(self):
        return self.name

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return True



class Application(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("school_verified", "School Admin Verified"),
        ("super_verified", "Super Admin Verified"),
        ("rejected", "Rejected"),
    ]
    
    STANDARD_CHOICES = [
        ("1", "Class 1"),
        ("2", "Class 2"),
        ("3", "Class 3"),
        ("4", "Class 4"),
        ("5", "Class 5"),
        ("6", "Class 6"),
        ("7", "Class 7"),
        ("8", "Class 8"),
        ("9", "Class 9"),
        ("10", "Class 10"),
    ]
    DEPT_CHOICES = [("primary", "Primary Section"), ("secondary", "Secondary Section")]
    
    # for future reference
    APPLICATION_ROLE_CHOICES = [
    ("student", "Student"),
    ("teacher", "Teacher"),
]
    #


    name = models.CharField(max_length=100)                 # full name shown in admin
    email = models.EmailField(unique=True)                  # used for account creation
    role = models.CharField(max_length=50, choices=User.ROLE_CHOICES)
    password = models.CharField(max_length=128)             # will be hashed when creating User

    applied_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    # ---------------- Admission form: Student Information ----------------
    # split name as per form (optional: we still keep `name` above for existing flows)
    first_name = models.CharField(max_length=80, blank=True)
    middle_name = models.CharField(max_length=80, blank=True)
    last_name = models.CharField(max_length=80, blank=True)

    aadhaar = models.CharField(
        max_length=12, blank=True,
        validators=[RegexValidator(r"^\d{12}$", "Aadhaar must be 12 digits")]
    )
    gender = models.CharField(max_length=16, blank=True)
    dob = models.DateField(null=True, blank=True, verbose_name="Date of Birth")
    age = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(40)])
    blood_group = models.CharField(max_length=8, blank=True)

    admission_class = models.CharField(max_length=2, choices=STANDARD_CHOICES, blank=True)  # "Class for Admission"
    previous_school = models.CharField(max_length=200, blank=True, null=True)
    transfer_certificate_provided = models.BooleanField(default=False)

    # Address (granular fields per form)
    street_name = models.CharField(max_length=120, blank=True)
    area_name = models.CharField(max_length=120, blank=True)
    city = models.CharField(max_length=80, blank=True)
    pincode = models.CharField(
        max_length=6, blank=True,
        validators=[RegexValidator(r"^\d{6}$", "Pincode must be 6 digits")]
    )

    # ---------------- Parent / Guardian Information ----------------
    father_name = models.CharField(max_length=120, blank=True)
    father_aadhaar = models.CharField(
        max_length=12, blank=True,
        validators=[RegexValidator(r"^\d{12}$", "Aadhaar must be 12 digits")]
    )
    father_occupation = models.CharField(max_length=120, blank=True)

    mother_name = models.CharField(max_length=120, blank=True)
    mother_aadhaar = models.CharField(
        max_length=12, blank=True,
        validators=[RegexValidator(r"^\d{12}$", "Aadhaar must be 12 digits")]
    )
    mother_occupation = models.CharField(max_length=120, blank=True)

    family_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # ---------------- Existing common fields (kept for compatibility) ----------------
    # Retained to avoid breaking existing APIs; you can deprecate later if desired.
    date_of_birth = models.DateField(null=True, blank=True)       # legacy
    address = models.TextField(null=True, blank=True)             # legacy
    phone_number = models.CharField(max_length=15, null=True, blank=True)  # legacy
    standard = models.CharField(max_length=10, null=True, blank=True)      # legacy (free-text)

    # Teacher-specific (when role == teacher) — kept from repo and aligned with choices
    department = models.CharField(max_length=100, choices=DEPT_CHOICES, null=True, blank=True)

    documents = models.FileField(upload_to="application_docs/", null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Application from {self.name} ({self.status})"
