#!/usr/bin/env python3
"""Serializers for the Department model."""

from rest_framework import serializers

from ..models import Department, Branch
from .branch import BranchListSerializer


class DepartmentListSerializer(serializers.ModelSerializer):
    """Compact serializer for department list view."""
    
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    city_name = serializers.CharField(source='branch.city.name', read_only=True)
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = (
            'id',
            'name',
            'code',
            'branch',
            'branch_name',
            'city_name',
            'is_active',
            'employee_count',
        )
        read_only_fields = fields

    def get_employee_count(self, obj):
        """Return the number of employees in this department."""
        return obj.employees.count()


class DepartmentSerializer(serializers.ModelSerializer):
    """Full serializer for department detail view."""
    
    branch_detail = BranchListSerializer(source='branch', read_only=True)
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = (
            'id',
            'name',
            'code',
            'description',
            'branch',
            'branch_detail',
            'is_active',
            'employee_count',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'branch_detail', 'employee_count', 'created_at', 'updated_at')

    def get_employee_count(self, obj):
        """Return the number of employees in this department."""
        return obj.employees.count()


class DepartmentCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating departments."""
    
    branch_detail = BranchListSerializer(source='branch', read_only=True)

    class Meta:
        model = Department
        fields = (
            'id',
            'name',
            'code',
            'description',
            'branch',
            'branch_detail',
            'is_active',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'branch_detail', 'created_at', 'updated_at')

    def validate_code(self, value):
        """Ensure code is uppercase."""
        return value.upper() if value else value

    def validate_branch(self, value):
        """Ensure the branch is active."""
        if value and not value.is_active:
            raise serializers.ValidationError("Cannot assign department to an inactive branch.")
        return value
