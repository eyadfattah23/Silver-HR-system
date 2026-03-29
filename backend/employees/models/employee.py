#!/usr/bin/env python3
"""
Custom User model (employee) and manager using phone number as primary login field.
Supports Egyptian phone numbers via `phonenumbers`.
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models
import phonenumbers
import uuid
import re
from datetime import date


# =============================================================================
# Enums / Choices
# =============================================================================

class Gender(models.TextChoices):
    MALE = 'male', 'Male'
    FEMALE = 'female', 'Female'


class MilitaryStatus(models.TextChoices):
    TEMPORARY_EXEMPTION = 'temporary_exemption', 'Temporary Exemption'
    PERMANENT_EXEMPTION = 'permanent_exemption', 'Permanent Exemption'
    EVASION = 'evasion', 'Evasion'
    POSTPONED = 'postponed', 'Postponed'
    COMPLETED = 'completed', 'Completed'
    NOT_APPLICABLE = 'not_applicable', 'Not Applicable'  # for females
    OTHER = 'other', 'Other'


class MaritalStatus(models.TextChoices):
    SINGLE = 'single', 'Single'
    MARRIED = 'married', 'Married'


class EmploymentType(models.TextChoices):
    FULL_TIME = 'full_time', 'Full Time'
    PART_TIME = 'part_time', 'Part Time'
    CONTRACTOR = 'contractor', 'Contractor'
    INTERN = 'intern', 'Intern'


class EmploymentState(models.TextChoices):
    ACTIVE = 'active', 'Active'
    SUSPENDED = 'suspended', 'Suspended'
    TERMINATED = 'terminated', 'Terminated'
    ON_LEAVE = 'on_leave', 'On Leave'


# =============================================================================
# Validators
# =============================================================================

def validate_egyptian_phone_number(value):
    """Validate that the phone number is a valid Egyptian phone number with +20 country code."""
    if not value:
        return

    # Egyptian phone numbers should start with +20
    if not value.startswith('+20'):
        raise ValidationError(
            'Phone number must be an Egyptian number starting with +20 country code.'
        )

    try:
        parsed_number = phonenumbers.parse(value, None)
        if not phonenumbers.is_valid_number(parsed_number):
            raise ValidationError('Invalid phone number format.')
        if parsed_number.country_code != 20:
            raise ValidationError(
                'Phone number must be an Egyptian number (+20).')
    except phonenumbers.NumberParseException:
        raise ValidationError('Invalid phone number format.')


def validate_egyptian_national_id(value):
    """Validate Egyptian National ID format (14 digits with valid structure)."""
    if not value:
        return

    # Egyptian NID is exactly 14 digits
    if not re.match(r'^\d{14}$', value):
        raise ValidationError(
            'Egyptian National ID must be exactly 14 digits.'
        )

    # First digit must be 2 (1900s) or 3 (2000s)
    century_digit = value[0]
    if century_digit not in ('2', '3'):
        raise ValidationError(
            'Invalid Egyptian National ID: first digit must be 2 or 3.'
        )

    # Validate birth date components
    year = int(value[1:3])
    month = int(value[3:5])
    day = int(value[5:7])

    if month < 1 or month > 12:
        raise ValidationError('Invalid Egyptian National ID: invalid month.')

    if day < 1 or day > 31:
        raise ValidationError('Invalid Egyptian National ID: invalid day.')

    # Try to create a valid date
    full_year = 1900 + year if century_digit == '2' else 2000 + year
    try:
        date(full_year, month, day)
    except ValueError:
        raise ValidationError(
            'Invalid Egyptian National ID: invalid birth date.')


def extract_dob_from_nid(nid):
    """Extract date of birth from Egyptian National ID."""
    if not nid or len(nid) != 14:
        return None

    century_digit = nid[0]
    if century_digit not in ('2', '3'):
        return None

    year = int(nid[1:3])
    month = int(nid[3:5])
    day = int(nid[5:7])

    full_year = 1900 + year if century_digit == '2' else 2000 + year

    try:
        return date(full_year, month, day)
    except ValueError:
        return None


def extract_gender_from_nid(nid):
    """Extract gender from Egyptian National ID (13th digit: odd = male, even = female)."""
    if not nid or len(nid) != 14:
        return None

    gender_digit = int(nid[12])  # 13th digit (0-indexed: 12)
    return Gender.MALE if gender_digit % 2 == 1 else Gender.FEMALE


# =============================================================================
# Employee Manager
# =============================================================================

class EmployeeManager(BaseUserManager):
    """Custom manager for Employee model using phone_number1 as the unique identifier."""

    def create_user(self, phone_number1, password=None, **extra_fields):
        """Create and return a regular user with the given phone number and password."""
        if not phone_number1:
            raise ValueError('The Phone Number field must be set')

        user = self.model(phone_number1=phone_number1, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number1, password=None, **extra_fields):
        """Create and return a superuser with the given phone number and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number1, password, **extra_fields)


# =============================================================================
# Employee Model
# =============================================================================

class Employee(AbstractUser):
    """Custom User model that uses phone number as the primary login field.
    
    Phone number (+20xxxxxxxxxx) is the unique identifier for authentication.
    """
    # Remove username and email fields from AbstractUser
    username = None
    email = None
    last_name = None   # Not used, replaced by second/third/fourth_name

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # ==========================================================================
    # Unique identifiers
    # ==========================================================================
    phone_number1 = models.CharField(
        max_length=13,
        unique=True,
        verbose_name="Primary Phone Number",
        validators=[validate_egyptian_phone_number],
        help_text='Egyptian phone with +20 prefix: +201xxxxxxxxx, used as unique identifier and for auth'
    )
    phone_number2 = models.CharField(
        max_length=13,
        blank=True,
        null=True,
        verbose_name="Secondary Phone Number",
        help_text='Optional alternative number'
    )
    fingerprint_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        help_text='Format: FP{CityCode}{DeptCode}{Gender}{DeviceID}, e.g., FPCaITF138'
    )
    national_id = models.CharField(
        max_length=14,
        unique=True,
        blank=True,
        null=True,
        validators=[validate_egyptian_national_id],
        help_text='Egyptian National ID (14 digits)'
    )

    # ==========================================================================
    # Personal info (Arabic names)
    # ==========================================================================
    first_name = models.CharField(max_length=50, help_text='First name in Arabic')
    second_name = models.CharField(max_length=50, help_text='Father name in Arabic')
    third_name = models.CharField(max_length=50, help_text='Grandfather name in Arabic')
    fourth_name = models.CharField(max_length=50, help_text='Family name in Arabic')

    date_of_birth = models.DateField(verbose_name="Date of Birth")
    gender = models.CharField(max_length=10, choices=Gender.choices)
    address = models.TextField(blank=True, null=True, help_text='Optional residential address')
    marital_status = models.CharField(
        max_length=10,
        choices=MaritalStatus.choices,
        default=MaritalStatus.SINGLE
    )
    military_status = models.CharField(max_length=20, choices=MilitaryStatus.choices)

    # ==========================================================================
    # Employment info
    # ==========================================================================
    department = models.ForeignKey(
        'core.Department',
        on_delete=models.PROTECT,
        related_name='employees',
        null=True,
        blank=True
    )
    job_title = models.ForeignKey(
        'employees.JobTitle',
        on_delete=models.PROTECT,
        related_name='employees',
        null=True,
        blank=True
    )
    
    # ManyToMany relationship to Role through EmployeeRole
    roles = models.ManyToManyField(
        'permissions.Role',
        through='permissions.EmployeeRole',
        through_fields=('employee', 'role'),
        related_name='employees',
        blank=True
    )
    
    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME
    )
    employment_state = models.CharField(
        max_length=20,
        choices=EmploymentState.choices,
        default=EmploymentState.ACTIVE
    )
    hire_date = models.DateField(verbose_name="Hire Date")

    # ==========================================================================
    # Salary
    # ==========================================================================
    current_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Current salary (latest)'
    )

    # ==========================================================================
    # Attendance
    # ==========================================================================
    is_attendance_exempt = models.BooleanField(
        default=False,
        help_text='If true, attendance policies do not apply'
    )

    # ==========================================================================
    # Notes
    # ==========================================================================
    notes = models.TextField(blank=True, null=True)

    # ==========================================================================
    # Timestamps and audit
    # ==========================================================================
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_employees',
        help_text='Who created this record'
    )
    updated_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_employees',
        help_text='Who last updated this record'
    )

    objects = EmployeeManager()

    USERNAME_FIELD = 'phone_number1'
    REQUIRED_FIELDS = ['first_name', 'second_name', 'third_name', 'fourth_name',
                       'date_of_birth', 'gender', 'military_status', 'hire_date']

    class Meta:
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        indexes = [
            models.Index(fields=['phone_number1']),
            models.Index(fields=['fingerprint_id']),
            models.Index(fields=['national_id']),
            models.Index(fields=['employment_state']),
            models.Index(fields=['department']),
            models.Index(fields=['department', 'employment_state']),
        ]

    def clean(self):
        """Validate national_id format."""
        super().clean()
        if self.national_id:
            validate_egyptian_national_id(self.national_id)

    def save(self, *args, **kwargs):
        """Override save to extract data from NID if provided."""
        # Extract data from NID before saving
        if self.national_id:
            # Extract DOB if not provided
            if not self.date_of_birth:
                extracted_dob = extract_dob_from_nid(self.national_id)
                if extracted_dob:
                    self.date_of_birth = extracted_dob

            # Extract gender if not provided
            if not self.gender:
                extracted_gender = extract_gender_from_nid(self.national_id)
                if extracted_gender:
                    self.gender = extracted_gender

        super().save(*args, **kwargs)

    @property
    def full_name(self):
        """Return full name (all four parts)."""
        return f"{self.first_name} {self.second_name} {self.third_name} {self.fourth_name}"

    def get_full_name(self):
        """Return the full name (Django User compatibility)."""
        return self.full_name

    def get_short_name(self):
        """Return the first name (Django User compatibility)."""
        return self.first_name

    def __str__(self):
        return f"{self.first_name} {self.fourth_name} ({self.phone_number1})"
    
    # ==========================================================================
    # Role & Permission helpers
    # ==========================================================================
    
    def get_active_roles(self, city=None, branch=None, department=None):
        """
        Return all active roles for this employee, optionally filtered by scope.
        If scope parameters are provided, only returns roles that apply to that scope.
        """
        from permissions.models import EmployeeRole
        
        qs = EmployeeRole.objects.filter(
            employee=self,
            is_active=True,
            role__is_active=True
        ).select_related('role', 'city', 'branch', 'department')
        
        if city or branch or department:
            # Filter by scope - need to check each role's applicability
            role_ids = [
                er.role_id for er in qs 
                if er.applies_to(city=city, branch=branch, department=department)
            ]
            return self.roles.filter(id__in=role_ids, is_active=True)
        
        return self.roles.filter(
            employee_roles__is_active=True,
            is_active=True
        ).distinct()
    
    def has_role(self, role_name, city=None, branch=None, department=None):
        """Check if this employee has a specific role, optionally within a scope."""
        return self.get_active_roles(
            city=city, branch=branch, department=department
        ).filter(name=role_name).exists()
    
    def has_permission(self, permission_code, city=None, branch=None, department=None):
        """
        Check if this employee has a specific permission.
        Checks role-based permissions, extra permissions, and delegated permissions.
        """
        # Check role-based permissions
        roles = self.get_active_roles(city=city, branch=branch, department=department)
        for role in roles:
            if role.has_permission(permission_code):
                return True
        
        # Check extra permissions
        extra_perms = self.get_extra_permissions(city=city, branch=branch, department=department)
        if extra_perms.filter(code=permission_code).exists():
            return True
        
        # Check delegated permissions
        delegated_perms = self.get_delegated_permissions(city=city, branch=branch, department=department)
        if delegated_perms.filter(code=permission_code).exists():
            return True
        
        return False
    
    def has_resource_action(self, resource, action, city=None, branch=None, department=None):
        """
        Check if this employee has permission for a specific resource and action.
        Checks role-based permissions, extra permissions, and delegated permissions.
        """
        # Check role-based permissions
        roles = self.get_active_roles(city=city, branch=branch, department=department)
        for role in roles:
            if role.has_resource_action(resource, action):
                return True
        
        # Check extra permissions
        extra_perms = self.get_extra_permissions(city=city, branch=branch, department=department)
        if extra_perms.filter(resource=resource, action=action).exists():
            return True
        
        # Check delegated permissions
        delegated_perms = self.get_delegated_permissions(city=city, branch=branch, department=department)
        if delegated_perms.filter(resource=resource, action=action).exists():
            return True
        
        return False
    
    def get_all_permissions(self, city=None, branch=None, department=None):
        """
        Return all permissions this employee has across all their active roles,
        extra permissions, and delegated permissions.
        """
        from permissions.models import Permission
        
        # Get role-based permissions
        roles = self.get_active_roles(city=city, branch=branch, department=department)
        role_permissions = Permission.objects.filter(
            roles__in=roles,
            role_permissions__is_active=True,
            is_active=True
        )
        
        # Get extra permissions
        extra_permissions = self.get_extra_permissions(city=city, branch=branch, department=department)
        
        # Get delegated permissions
        delegated_permissions = self.get_delegated_permissions(city=city, branch=branch, department=department)
        
        # Combine and return distinct
        return (role_permissions | extra_permissions | delegated_permissions).distinct()
    
    def get_extra_permissions(self, city=None, branch=None, department=None):
        """
        Return all active extra permissions for this employee, optionally filtered by scope.
        Excludes expired permissions.
        """
        from permissions.models import EmployeeExtraPermission, Permission
        from django.utils import timezone
        
        qs = EmployeeExtraPermission.objects.filter(
            employee=self,
            is_active=True,
            permission__is_active=True
        ).filter(
            # Not expired (null or future)
            models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=timezone.now())
        ).select_related('permission', 'city', 'branch', 'department')
        
        if city or branch or department:
            # Filter by scope - need to check each permission's applicability
            perm_ids = [
                ep.permission_id for ep in qs 
                if ep.applies_to(city=city, branch=branch, department=department)
            ]
            return Permission.objects.filter(id__in=perm_ids, is_active=True)
        
        return Permission.objects.filter(
            employee_extra_permissions__employee=self,
            employee_extra_permissions__is_active=True,
            is_active=True
        ).filter(
            models.Q(employee_extra_permissions__expires_at__isnull=True) | 
            models.Q(employee_extra_permissions__expires_at__gt=timezone.now())
        ).distinct()
    
    def has_extra_permission(self, permission_code, city=None, branch=None, department=None):
        """
        Check if this employee has a specific extra permission (not via role).
        """
        return self.get_extra_permissions(
            city=city, branch=branch, department=department
        ).filter(code=permission_code).exists()
    
    def get_delegated_permissions(self, city=None, branch=None, department=None):
        """
        Return all active delegated permissions for this employee, optionally filtered by scope.
        Excludes expired delegations.
        """
        from permissions.models import PermissionDelegation, Permission
        from django.utils import timezone
        
        qs = PermissionDelegation.objects.filter(
            delegate=self,
            is_active=True,
            permission__is_active=True
        ).filter(
            # Not expired (null or future)
            models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=timezone.now())
        ).select_related('permission', 'city', 'branch', 'department')
        
        if city or branch or department:
            # Filter by scope - need to check each delegation's applicability
            perm_ids = [
                pd.permission_id for pd in qs 
                if pd.applies_to(city=city, branch=branch, department=department)
            ]
            return Permission.objects.filter(id__in=perm_ids, is_active=True)
        
        return Permission.objects.filter(
            delegations__delegate=self,
            delegations__is_active=True,
            is_active=True
        ).filter(
            models.Q(delegations__expires_at__isnull=True) | 
            models.Q(delegations__expires_at__gt=timezone.now())
        ).distinct()
    
    def has_delegated_permission(self, permission_code, city=None, branch=None, department=None):
        """
        Check if this employee has a specific delegated permission.
        """
        return self.get_delegated_permissions(
            city=city, branch=branch, department=department
        ).filter(code=permission_code).exists()
    
    def can_delegate_permission(self, permission, city=None, branch=None, department=None):
        """
        Check if this employee can delegate a specific permission.
        """
        from permissions.models import PermissionDelegation
        return PermissionDelegation.can_delegate(
            self, permission, city=city, branch=branch, department=department
        )
    
    def get_delegation_rights(self):
        """
        Return all active delegation rights for this employee.
        """
        from permissions.models import DelegationRight
        return DelegationRight.objects.filter(
            employee=self,
            is_active=True
        ).select_related('can_delegate_permission')
