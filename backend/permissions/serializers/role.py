#!/usr/bin/env python3
"""Serializers for Role and RolePermission models."""

from rest_framework import serializers
from permissions.models import Role, RolePermission, Permission
from .permission import PermissionMinimalSerializer


class RolePermissionSerializer(serializers.ModelSerializer):
    """Serializer for role-permission relationships."""
    permission = PermissionMinimalSerializer(read_only=True)
    permission_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = RolePermission
        fields = [
            'id',
            'permission',
            'permission_id',
            'is_active',
            'granted_at',
        ]
        read_only_fields = ['id', 'permission', 'granted_at']


class RoleSerializer(serializers.ModelSerializer):
    """Full role serializer with permissions."""
    permissions_list = serializers.SerializerMethodField()
    permissions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = [
            'id',
            'name',
            'description',
            'is_system_role',
            'is_active',
            'permissions_list',
            'permissions_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'is_system_role', 'created_at', 'updated_at']
    
    def get_permissions_list(self, obj):
        """Get list of active permissions for this role."""
        role_perms = RolePermission.objects.filter(
            role=obj,
            is_active=True,
            permission__is_active=True,
        ).select_related('permission')
        
        return [
            {
                'id': str(rp.permission.id),
                'code': rp.permission.code,
                'name': rp.permission.name,
                'can_be_given': rp.permission.can_be_given,
            }
            for rp in role_perms
        ]
    
    def get_permissions_count(self, obj):
        """Get count of active permissions."""
        return RolePermission.objects.filter(
            role=obj,
            is_active=True,
            permission__is_active=True,
        ).count()


class RoleListSerializer(serializers.ModelSerializer):
    """Compact role serializer for list views."""
    permissions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = [
            'id',
            'name',
            'description',
            'is_system_role',
            'is_active',
            'permissions_count',
        ]
    
    def get_permissions_count(self, obj):
        return RolePermission.objects.filter(
            role=obj,
            is_active=True,
            permission__is_active=True,
        ).count()


class RoleCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating roles."""
    permission_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        write_only=True,
        help_text="List of permission IDs to assign to this role",
    )
    
    class Meta:
        model = Role
        fields = [
            'id',
            'name',
            'description',
            'is_active',
            'permission_ids',
        ]
        read_only_fields = ['id']
    
    def validate_name(self, value):
        """Ensure role name is unique (case-insensitive)."""
        instance = self.instance
        queryset = Role.objects.filter(name__iexact=value)
        
        if instance:
            queryset = queryset.exclude(pk=instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError("A role with this name already exists.")
        
        return value
    
    def validate_permission_ids(self, value):
        """Validate that all permission IDs exist."""
        if value:
            existing_ids = set(
                Permission.objects.filter(id__in=value, is_active=True)
                .values_list('id', flat=True)
            )
            invalid_ids = set(value) - existing_ids
            if invalid_ids:
                raise serializers.ValidationError(
                    f"Invalid permission IDs: {[str(id) for id in invalid_ids]}"
                )
        return value
    
    def create(self, validated_data):
        permission_ids = validated_data.pop('permission_ids', [])
        role = Role.objects.create(**validated_data)
        
        # Add permissions
        for perm_id in permission_ids:
            RolePermission.objects.create(
                role=role,
                permission_id=perm_id,
            )
        
        return role
    
    def update(self, instance, validated_data):
        permission_ids = validated_data.pop('permission_ids', None)
        
        # Update role fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update permissions if provided
        if permission_ids is not None:
            # Remove existing permissions
            RolePermission.objects.filter(role=instance).delete()
            
            # Add new permissions
            for perm_id in permission_ids:
                RolePermission.objects.create(
                    role=instance,
                    permission_id=perm_id,
                )
        
        return instance


class RoleMinimalSerializer(serializers.ModelSerializer):
    """Minimal role serializer for nested representations."""
    
    class Meta:
        model = Role
        fields = ['id', 'name']
        read_only_fields = fields


class AddPermissionToRoleSerializer(serializers.Serializer):
    """Serializer for adding a permission to a role."""
    permission_id = serializers.UUIDField()
    
    def validate_permission_id(self, value):
        """Validate permission exists and is active."""
        try:
            Permission.objects.get(id=value, is_active=True)
        except Permission.DoesNotExist:
            raise serializers.ValidationError("Permission not found or is inactive.")
        return value
