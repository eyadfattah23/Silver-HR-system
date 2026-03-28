#!/usr/bin/env python3
"""Serializers for the City model."""

from rest_framework import serializers

from ..models import City


class CityListSerializer(serializers.ModelSerializer):
    """Compact serializer for city list view."""
    
    branch_count = serializers.SerializerMethodField()

    class Meta:
        model = City
        fields = (
            'id',
            'name',
            'code',
            'is_active',
            'branch_count',
        )
        read_only_fields = fields

    def get_branch_count(self, obj):
        """Return the number of branches in this city."""
        return obj.branches.count()


class CitySerializer(serializers.ModelSerializer):
    """Full serializer for city detail view."""
    
    branch_count = serializers.SerializerMethodField()

    class Meta:
        model = City
        fields = (
            'id',
            'name',
            'code',
            'is_active',
            'branch_count',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'branch_count', 'created_at', 'updated_at')

    def get_branch_count(self, obj):
        """Return the number of branches in this city."""
        return obj.branches.count()


class CityCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating cities."""

    class Meta:
        model = City
        fields = (
            'id',
            'name',
            'code',
            'is_active',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_code(self, value):
        """Ensure code is uppercase."""
        return value.upper() if value else value
