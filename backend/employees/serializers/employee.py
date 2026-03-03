#!/usr/bin/env python3
"""Serializers for Employee model.
Defines custom serializers for admin dashboard API and employee self-service.
"""

from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from ..models import (
    Employee,
    JobTitle,
    validate_egyptian_phone_number,
    validate_egyptian_national_id,
    extract_dob_from_nid,
    extract_gender_from_nid,
    Gender,
    MilitaryStatus,
    MaritalStatus,
    EmploymentType,
    EmploymentState,
)
from .job_title import JobTitleListSerializer


class EmployeeCreateSerializer(UserCreateSerializer):
    """Serializer for admins to create new employees via API."""

    re_password = serializers.CharField(
        write_only=True, style={'input_type': 'password'})
    # Make military_status optional so it can be auto-set for females
    military_status = serializers.ChoiceField(
        choices=MilitaryStatus.choices,
        required=False,
        allow_blank=True
    )
    
    # Nested display for read
    job_title_detail = JobTitleListSerializer(source='job_title', read_only=True)

    class Meta(UserCreateSerializer.Meta):
        model = Employee
        fields = (
            'id',
            # Identifiers
            'phone_number1',
            'phone_number2',
            'password',
            're_password',
            'fingerprint_id',
            'national_id',
            # Personal info
            'first_name',
            'second_name',
            'third_name',
            'fourth_name',
            'date_of_birth',
            'gender',
            'address',
            'marital_status',
            'military_status',
            # Employment info
            'department',
            'job_title',
            'job_title_detail',
            'employment_type',
            'employment_state',
            'hire_date',
            'current_salary',
            'is_attendance_exempt',
            'notes',
        )
        read_only_fields = ('id', 'job_title_detail')

    def validate_phone_number1(self, value):
        """Validate Egyptian phone number format."""
        validate_egyptian_phone_number(value)
        return value

    def validate_national_id(self, value):
        """Validate Egyptian National ID format."""
        if value:
            validate_egyptian_national_id(value)
        return value

    def validate(self, attrs):
        """Cross-field validation + auto-extraction from NID."""
        # Password validation: ensure passwords match
        password = attrs.get('password')
        re_password = attrs.pop('re_password', None)

        if password != re_password:
            raise serializers.ValidationError({
                're_password': 'Passwords do not match.'
            })

        # Auto-extract DOB and gender from National ID if provided
        national_id = attrs.get('national_id')
        if national_id:
            if not attrs.get('date_of_birth'):
                extracted_dob = extract_dob_from_nid(national_id)
                if extracted_dob:
                    attrs['date_of_birth'] = extracted_dob
            if not attrs.get('gender'):
                extracted_gender = extract_gender_from_nid(national_id)
                if extracted_gender:
                    attrs['gender'] = extracted_gender

        # Auto-set military_status to not_applicable for females
        if attrs.get('gender') == Gender.FEMALE and not attrs.get('military_status'):
            attrs['military_status'] = MilitaryStatus.NOT_APPLICABLE

        return attrs


class EmployeeSerializer(UserSerializer):
    """Full read-only serializer for employee data."""
    
    job_title_detail = JobTitleListSerializer(source='job_title', read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta(UserSerializer.Meta):
        model = Employee
        fields = (
            'id',
            # Identifiers
            'phone_number1',
            'phone_number2',
            'fingerprint_id',
            'national_id',
            # Personal info
            'first_name',
            'second_name',
            'third_name',
            'fourth_name',
            'full_name',
            'date_of_birth',
            'gender',
            'address',
            'marital_status',
            'military_status',
            # Employment info
            'department',
            'job_title',
            'job_title_detail',
            'employment_type',
            'employment_state',
            'hire_date',
            'current_salary',
            'is_attendance_exempt',
            'notes',
            # Status
            'is_active',
            'is_staff',
            # Timestamps
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
        )
        read_only_fields = fields


class EmployeeListSerializer(serializers.ModelSerializer):
    """Compact serializer for employee list view."""
    
    full_name = serializers.CharField(read_only=True)
    job_title_name = serializers.CharField(source='job_title.name', read_only=True)

    class Meta:
        model = Employee
        fields = (
            'id',
            'phone_number1',
            'first_name',
            'fourth_name',
            'full_name',
            'job_title_name',
            'employment_state',
            'is_active',
            'is_staff',
            'hire_date',
        )
        read_only_fields = fields


class EmployeeAdminUpdateSerializer(serializers.ModelSerializer):
    """Serializer for admins to update any employee data (except password)."""
    
    job_title_detail = JobTitleListSerializer(source='job_title', read_only=True)

    class Meta:
        model = Employee
        fields = (
            'id',
            # Identifiers
            'phone_number1',
            'phone_number2',
            'fingerprint_id',
            'national_id',
            # Personal info
            'first_name',
            'second_name',
            'third_name',
            'fourth_name',
            'date_of_birth',
            'gender',
            'address',
            'marital_status',
            'military_status',
            # Employment info
            'department',
            'job_title',
            'job_title_detail',
            'employment_type',
            'employment_state',
            'hire_date',
            'current_salary',
            'is_attendance_exempt',
            'notes',
            # Status
            'is_active',
            'is_staff',
        )
        read_only_fields = ('id', 'job_title_detail')

    def validate_phone_number1(self, value):
        """Validate Egyptian phone number format."""
        validate_egyptian_phone_number(value)
        return value

    def validate_national_id(self, value):
        """Validate Egyptian National ID format."""
        if value:
            validate_egyptian_national_id(value)
        return value

    def update(self, instance, validated_data):
        """Update and set updated_by from request context."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['updated_by'] = request.user
        return super().update(instance, validated_data)
