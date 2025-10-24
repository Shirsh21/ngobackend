
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Application, User
# from student.models import Student
# from teacher.models import Teacher

# @receiver(post_save, sender=Application)
# def create_user_and_profile_on_verification(sender, instance, **kwargs):
   
#     if instance.status == 'verified':
        
#         user = User.objects.create_user(
#             email=instance.email,
#             name=instance.name,
#             password=instance.password,
#             role=instance.role
#         )
        
        
#         if instance.role == 'student':
#             Student.objects.create(
#                 user=user,
#                 student_id=f"STU{user.id:04d}",
#                 date_of_birth=instance.date_of_birth,
#                 address=instance.address,
#                 phone_number=instance.phone_number,
#                 guardian_name=instance.guardian_name,
#                 guardian_phone=instance.guardian_phone,
#                 standard=instance.standard
#             )
#         elif instance.role == 'teacher':
#             Teacher.objects.create(
#                 user=user,
#                 teacher_id=f"TCH{user.id:04d}",
#                 date_of_birth=instance.date_of_birth,
#                 address=instance.address,
#                 phone_number=instance.phone_number,
#                 department=instance.department
#             )






# account/signals.py
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from account.models import Application, User  # adjust if your Application/User live elsewhere
from student.models import Student
from teacher.models import Teacher

# --- Helpers ---

def _get(instance, attr, default=None):
    """Safe getattr that returns default if attr missing or value is empty string."""
    val = getattr(instance, attr, default)
    if val in ("", None):
        return default
    return val

def _build_full_address(instance):
    """
    Prefer granular fields if present; otherwise fall back to legacy Application.address.
    """
    street = _get(instance, "street_name", "")
    area = _get(instance, "area_name", "")
    city = _get(instance, "city", "")
    pin = _get(instance, "pincode", "")

    parts = [p for p in [street, area, city, pin] if p]
    if parts:
        return ", ".join(parts)
    return _get(instance, "address", None)

def _generate_student_id(user_id: int) -> str:
    return f"STU{user_id:04d}"

def _generate_teacher_id(user_id: int) -> str:
    return f"TCH{user_id:04d}"


# --- Track old status so we only act on transitions ---
@receiver(pre_save, sender=Application)
def _capture_old_status(sender, instance: Application, **kwargs):
    if instance.pk:
        try:
            prev = Application.objects.get(pk=instance.pk)
            instance._old_status = prev.status
        except Application.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None



@receiver(post_save, sender=Application)
def _create_user_and_profile_on_verify(sender, instance, created: bool, **kwargs):
    old = getattr(instance, "_old_status", None)
    # fire ONLY when moving to 'super_verified'
    if created or instance.status != "super_verified" or old == "super_verified":
        return


    # If a User exists with this email, don't recreate; use it.
    UserModel = get_user_model()
    user = UserModel.objects.filter(email=instance.email).first()
    if not user:
        # Application.password may be raw; create_user will hash it.
        user = UserModel.objects.create_user(
            email=instance.email,
            name=_get(instance, "name", f"User {instance.email}"),
            role=instance.role,
            password=instance.password,
        )

    # STUDENT
    if instance.role == "student":
        if not Student.objects.filter(user=user).exists():
            # Standard: prefer admissions admission_class; fallback to legacy standard
            admission_class = _get(instance, "admission_class", None)
            standard = admission_class or _get(instance, "standard", None) or "1"  # safe fallback

            # Build addresses and copy fields
            full_address = _build_full_address(instance)

            Student.objects.create(
                user=user,
                student_id=_generate_student_id(user.id),

                # original required field
                standard=standard,

                # original fields
                date_of_birth=_get(instance, "dob", _get(instance, "date_of_birth", None)),
                address=full_address,
                phone_number=_get(instance, "phone_number", None),
                guardian_name=_get(instance, "guardian_name", None),
                guardian_phone=_get(instance, "guardian_phone", None),

                # new admissions-aligned fields (optional)
                first_name=_get(instance, "first_name", ""),
                middle_name=_get(instance, "middle_name", ""),
                last_name=_get(instance, "last_name", ""),
                aadhaar=_get(instance, "aadhaar", ""),
                gender=_get(instance, "gender", ""),
                dob=_get(instance, "dob", None),  # kept separate; primary is date_of_birth above
                age=_get(instance, "age", None),
                blood_group=_get(instance, "blood_group", ""),

                admission_class=admission_class or "",
                previous_school=_get(instance, "previous_school", ""),
                transfer_certificate_provided=bool(_get(instance, "transfer_certificate_provided", False)),

                street_name=_get(instance, "street_name", ""),
                area_name=_get(instance, "area_name", ""),
                city=_get(instance, "city", ""),
                pincode=_get(instance, "pincode", ""),

                father_name=_get(instance, "father_name", ""),
                father_aadhaar=_get(instance, "father_aadhaar", ""),
                father_occupation=_get(instance, "father_occupation", ""),

                mother_name=_get(instance, "mother_name", ""),
                mother_aadhaar=_get(instance, "mother_aadhaar", ""),
                mother_occupation=_get(instance, "mother_occupation", ""),

                family_income=_get(instance, "family_income", None),
            )

    # TEACHER
    elif instance.role == "teacher":
        if not Teacher.objects.filter(user=user).exists():
            Teacher.objects.create(
                user=user,
                teacher_id=_generate_teacher_id(user.id),

                # keep legacy teacher fields if you have them (address/phone/hire_date set by model defaults)
                address=_get(instance, "address", None),
                phone_number=_get(instance, "phone_number", None),
                department=_get(instance, "department", "primary"),

                # map admissions-common if present (all optional)
                first_name=_get(instance, "first_name", ""),
                middle_name=_get(instance, "middle_name", ""),
                last_name=_get(instance, "last_name", ""),
                aadhaar=_get(instance, "aadhaar", ""),
                gender=_get(instance, "gender", ""),
                date_of_birth=_get(instance, "dob", _get(instance, "date_of_birth", None)),

                street_name=_get(instance, "street_name", ""),
                area_name=_get(instance, "area_name", ""),
                city=_get(instance, "city", ""),
                pincode=_get(instance, "pincode", ""),
            )
