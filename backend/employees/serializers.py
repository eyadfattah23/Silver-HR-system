#!/usr/bin/env python3
"""Serializers for Employee model.
Defines custom serializers for admin dashboard API and employee self-service.
"""

from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from .models import (
    Employee,
    validate_egyptian_phone_number,
    validate_egyptian_national_id,
    extract_dob_from_nid,
    extract_gender_from_nid,
)


class EmployeeCreateSerializer(UserCreateSerializer):
    """Serializer for admins to create new employees via API."""

    re_password = serializers.CharField(
        write_only=True, style={'input_type': 'password'})

    class Meta(UserCreateSerializer.Meta):
        model = Employee
        fields = (
            'id',
            'phone_number1',
            'phone_number2',
            'password',
            're_password',
            'first_name',
            'rest_of_name',
            'email',
            'date_joined',
            'dob',
            'gender',
            'identity_type',
            'identity_number',
            'address',
            'location',
            'role',
            'fingerprint_id',
            'is_active',
            'is_staff',
            'is_verified',
        )
        read_only_fields = ('id',)

    def validate_phone_number1(self, value):
        """Validate Egyptian phone number format."""
        validate_egyptian_phone_number(value)
        return value

    def validate_identity_number(self, value):
        """Validate identity number based on identity type."""
        identity_type = self.initial_data.get('identity_type')
        if identity_type == 'nid':
            validate_egyptian_national_id(value)
        return value

    def validate_email(self, value):
        """Convert empty email to None to avoid unique constraint issues."""
        if not value:
            return None
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

        identity_type = attrs.get('identity_type')
        identity_number = attrs.get('identity_number')

        if identity_type == 'nid' and identity_number:
            if not attrs.get('dob'):
                attrs['dob'] = extract_dob_from_nid(identity_number)
            if not attrs.get('gender'):
                attrs['gender'] = extract_gender_from_nid(identity_number)

        return attrs

    def create(self, validated_data):
        """Create employee with password."""
        password = validated_data.pop('password', None)
        employee = Employee(**validated_data)
        if password:
            employee.set_password(password)
        employee.save()
        return employee


class EmployeeSerializer(UserSerializer):
    """Read-only serializer for employee data."""

    class Meta(UserSerializer.Meta):
        model = Employee
        fields = (
            'id',
            'phone_number1',
            'phone_number2',
            'first_name',
            'rest_of_name',
            'email',
            'is_active',
            'is_staff',
            'is_verified',
            'date_joined',
            'dob',
            'gender',
            'identity_type',
            'identity_number',
            'address',
            'location',
            'profile_picture',
            'role',
            'fingerprint_id',
            'created_at',
            'updated_at',
        )
        read_only_fields = fields


class EmployeeListSerializer(serializers.ModelSerializer):
    """Compact serializer for employee list view."""

    class Meta:
        model = Employee
        fields = (
            'id',
            'phone_number1',
            'first_name',
            'rest_of_name',
            'email',
            'role',
            'is_active',
            'is_staff',
            'date_joined',
        )
        read_only_fields = fields


class EmployeeAdminUpdateSerializer(serializers.ModelSerializer):
    """Serializer for admins to update any employee data (except password)."""

    class Meta:
        model = Employee
        fields = (
            'id',
            'phone_number1',
            'phone_number2',
            'first_name',
            'rest_of_name',
            'email',
            'date_joined',
            'dob',
            'gender',
            'identity_type',
            'identity_number',
            'address',
            'location',
            'profile_picture',
            'role',
            'fingerprint_id',
            'is_active',
            'is_staff',
            'is_verified',
        )
        read_only_fields = ('id',)

    def validate_phone_number1(self, value):
        validate_egyptian_phone_number(value)
        return value

    def validate_email(self, value):
        if not value:
            return None
        return value

    def validate_identity_number(self, value):
        identity_type = self.initial_data.get(
            'identity_type',
            self.instance.identity_type if self.instance else None
        )
        if identity_type == 'nid':
            validate_egyptian_national_id(value)
        return value
