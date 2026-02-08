from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

from .models import Employee


class NullableEmailField(forms.EmailField):
    """Email field that treats empty values as None for unique constraint compatibility."""

    def to_python(self, value):
        """Convert empty string to None before any validation."""
        if value in self.empty_values:
            return None
        return super().to_python(value)

    def validate(self, value):
        """Skip validation for None values."""
        if value is None:
            return
        super().validate(value)


class EmployeeCreationForm(UserCreationForm):
    """Custom form for creating new employees in admin."""

    email = NullableEmailField(required=False)

    class Meta:
        model = Employee
        fields = ('phone_number1', 'first_name', 'rest_of_name', 'date_joined',
                  'identity_type', 'identity_number', 'email', 'phone_number2', 'dob')

    def clean_email(self):
        """Convert empty email to None to avoid unique constraint issues."""
        email = self.cleaned_data.get('email')
        if not email:
            return None
        return email


class EmployeeChangeForm(UserChangeForm):
    """Custom form for editing employees in admin."""

    email = NullableEmailField(required=False)

    class Meta:
        model = Employee
        fields = '__all__'

    def clean_email(self):
        """Convert empty email to None to avoid unique constraint issues."""
        email = self.cleaned_data.get('email')
        if not email:
            return None
        return email


@admin.register(Employee)
class EmployeeAdmin(BaseUserAdmin):
    form = EmployeeChangeForm
    add_form = EmployeeCreationForm
    list_display = ('id', 'first_name', 'rest_of_name',
                    'email', 'phone_number1', 'date_joined')
    search_fields = ('first_name', 'phone_number1')
    list_filter = ('date_joined',)
    ordering = ('first_name', 'created_at')

    # Custom fieldsets for editing existing users (no username field)
    fieldsets = (
        (None, {'fields': ('phone_number1', 'password')}),
        ('Personal info', {'fields': ('first_name', 'rest_of_name', 'email',
         'phone_number2', 'dob', 'gender', 'address', 'location', 'profile_picture')}),
        ('Identity', {'fields': ('identity_type', 'identity_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff',
         'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('date_joined', 'last_login')}),
        ('Other', {'fields': ('role', 'fingerprint_id')}),
    )

    # Custom fieldsets for adding new users
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number1', 'first_name', 'rest_of_name', 'date_joined', 'identity_type', 'identity_number', 'password1', 'password2', 'email', 'phone_number2', 'dob'),
        }),
    )
