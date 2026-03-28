#!/usr/bin/env python3
"""Serializers for the Branch model."""

from rest_framework import serializers

from ..models import Branch, City
from .city import CityListSerializer


class BranchListSerializer(serializers.ModelSerializer):
    """Compact serializer for branch list view."""
    
    city_name = serializers.CharField(source='city.name', read_only=True)
    department_count = serializers.SerializerMethodField()

    class Meta:
        model = Branch
        fields = (
            'id',
            'name',
            'city',
            'city_name',
            'is_active',
            'department_count',
        )
        read_only_fields = fields

    def get_department_count(self, obj):
        """Return the number of departments in this branch."""
        return obj.departments.count()


class BranchSerializer(serializers.ModelSerializer):
    """Full serializer for branch detail view."""
    
    city_detail = CityListSerializer(source='city', read_only=True)
    department_count = serializers.SerializerMethodField()

    class Meta:
        model = Branch
        fields = (
            'id',
            'name',
            'description',
            'city',
            'city_detail',
            'location',
            'is_active',
            'department_count',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'city_detail', 'department_count', 'created_at', 'updated_at')

    def get_department_count(self, obj):
        """Return the number of departments in this branch."""
        return obj.departments.count()


class BranchCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating branches."""
    
    city_detail = CityListSerializer(source='city', read_only=True)

    class Meta:
        model = Branch
        fields = (
            'id',
            'name',
            'description',
            'city',
            'city_detail',
            'location',
            'is_active',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'city_detail', 'created_at', 'updated_at')

    def validate_city(self, value):
        """Ensure the city is active."""
        if value and not value.is_active:
            raise serializers.ValidationError("Cannot assign branch to an inactive city.")
        return value
