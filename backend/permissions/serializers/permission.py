#!/usr/bin/env python3
"""Serializers for Permission model."""

from rest_framework import serializers
from permissions.models import Permission


class PermissionSerializer(serializers.ModelSerializer):
    """Full permission serializer (read-only)."""
    
    class Meta:
        model = Permission
        fields = [
            'id',
            'code',
            'name',
            'description',
            'resource',
            'action',
            'can_be_given',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields  # All fields are read-only


class PermissionListSerializer(serializers.ModelSerializer):
    """Compact permission serializer for list views."""
    
    class Meta:
        model = Permission
        fields = [
            'id',
            'code',
            'name',
            'resource',
            'action',
            'can_be_given',
            'is_active',
        ]
        read_only_fields = fields


class PermissionMinimalSerializer(serializers.ModelSerializer):
    """Minimal permission serializer for nested representations."""
    
    class Meta:
        model = Permission
        fields = ['id', 'code', 'name']
        read_only_fields = fields
