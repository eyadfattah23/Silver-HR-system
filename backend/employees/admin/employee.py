#!/usr/bin/env python3
"""Admin configuration for the Employee model."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from ..models import Employee


# =============================================================================
# Employee Admin Forms
# =============================================================================

class EmployeeCreationForm(UserCreationForm):
    """Custom form for creating new employees in admin."""

    class Meta:
        model = Employee
        fields = (
            'phone_number1',
            'first_name',
            'second_name',
            'third_name',
            'fourth_name',
            'date_of_birth',
            'gender',
            'military_status',
            'hire_date',
            'national_id',
            'phone_number2',
        )


class EmployeeChangeForm(UserChangeForm):
    """Custom form for editing employees in admin."""

    class Meta:
        model = Employee
        fields = '__all__'


# =============================================================================
# Employee Admin
# =============================================================================

@admin.register(Employee)
class EmployeeAdmin(BaseUserAdmin):
    """Admin configuration for Employee model (custom User)."""
    
    form = EmployeeChangeForm
    add_form = EmployeeCreationForm
    
    list_display = (
        'id',
        'first_name',
        'fourth_name',
        'phone_number1',
        'employment_state',
        'job_title',
        'hire_date',
        'is_active',
    )
    list_filter = (
        'employment_state',
        'employment_type',
        'gender',
        'marital_status',
        'military_status',
        'is_active',
        'is_staff',
        'job_title',
        'department',
    )
    search_fields = (
        'first_name',
        'second_name',
        'third_name',
        'fourth_name',
        'phone_number1',
        'national_id',
        'fingerprint_id',
    )
    ordering = ('-created_at',)

    # Custom fieldsets for editing existing users
    fieldsets = (
        (None, {'fields': ('phone_number1', 'password')}),
        ('Personal Info', {'fields': (
            'first_name',
            'second_name',
            'third_name',
            'fourth_name',
            'date_of_birth',
            'gender',
            'national_id',
            'phone_number2',
            'address',
            'marital_status',
            'military_status',
        )}),
        ('Employment', {'fields': (
            'department',
            'job_title',
            'employment_type',
            'employment_state',
            'hire_date',
            'current_salary',
            'fingerprint_id',
            'is_attendance_exempt',
        )}),
        ('Permissions', {'fields': (
            'is_active',
            'is_staff',
            'is_superuser',
            'groups',
            'user_permissions',
        )}),
        ('Notes', {'fields': ('notes',)}),
        ('Audit', {'fields': (
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
            'last_login',
        )}),
    )
    readonly_fields = ('created_at', 'updated_at', 'last_login')

    # Custom fieldsets for adding new users
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'phone_number1',
                'password1',
                'password2',
            ),
        }),
        ('Personal Info', {
            'classes': ('wide',),
            'fields': (
                'first_name',
                'second_name',
                'third_name',
                'fourth_name',
                'date_of_birth',
                'gender',
                'national_id',
                'military_status',
            ),
        }),
        ('Employment', {
            'classes': ('wide',),
            'fields': (
                'hire_date',
                'job_title',
                'department',
            ),
        }),
    )
