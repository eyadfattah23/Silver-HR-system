#!/usr/bin/env python3
"""Serializers for EmployeeRole model."""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from permissions.models import EmployeeRole, Role
from core.models import City, Branch, Department
from .role import RoleMinimalSerializer

Employee = get_user_model()


class EmployeeMinimalSerializer(serializers.ModelSerializer):
    """Minimal employee serializer for nested representations."""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = ['id', 'email', 'full_name']
        read_only_fields = fields
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email


class ScopeSerializer(serializers.Serializer):
    """Serializer for scope information."""
    level = serializers.CharField()
    city = serializers.DictField(allow_null=True)
    branch = serializers.DictField(allow_null=True)
    department = serializers.DictField(allow_null=True)


class EmployeeRoleSerializer(serializers.ModelSerializer):
    """Full employee role serializer."""
    employee = EmployeeMinimalSerializer(read_only=True)
    role = RoleMinimalSerializer(read_only=True)
    granted_by = EmployeeMinimalSerializer(read_only=True)
    revoked_by = EmployeeMinimalSerializer(read_only=True)
    scope = serializers.SerializerMethodField()
    
    # Write-only fields
    employee_id = serializers.UUIDField(write_only=True)
    role_id = serializers.UUIDField(write_only=True)
    city_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    branch_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    department_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = EmployeeRole
        fields = [
            'id',
            'employee',
            'employee_id',
            'role',
            'role_id',
            'city_id',
            'branch_id',
            'department_id',
            'scope',
            'is_active',
            'granted_by',
            'granted_at',
            'revoked_by',
            'revoked_at',
        ]
        read_only_fields = [
            'id', 'employee', 'role', 'scope',
            'granted_by', 'granted_at', 'revoked_by', 'revoked_at',
        ]
    
    def get_scope(self, obj):
        """Get scope information."""
        scope = {
            'level': 'global',
            'city': None,
            'branch': None,
            'department': None,
        }
        
        if obj.department:
            scope['level'] = 'department'
            scope['department'] = {'id': str(obj.department.id), 'name': obj.department.name}
            if obj.department.branch:
                scope['branch'] = {'id': str(obj.department.branch.id), 'name': obj.department.branch.name}
                if obj.department.branch.city:
                    scope['city'] = {'id': str(obj.department.branch.city.id), 'name': obj.department.branch.city.name}
        elif obj.branch:
            scope['level'] = 'branch'
            scope['branch'] = {'id': str(obj.branch.id), 'name': obj.branch.name}
            if obj.branch.city:
                scope['city'] = {'id': str(obj.branch.city.id), 'name': obj.branch.city.name}
        elif obj.city:
            scope['level'] = 'city'
            scope['city'] = {'id': str(obj.city.id), 'name': obj.city.name}
        
        return scope
    
    def validate(self, attrs):
        """Validate scope consistency."""
        city_id = attrs.get('city_id')
        branch_id = attrs.get('branch_id')
        department_id = attrs.get('department_id')
        
        # Validate relationships
        if department_id:
            try:
                dept = Department.objects.select_related('branch__city').get(id=department_id)
                # If branch or city provided, they must match
                if branch_id and dept.branch_id != branch_id:
                    raise serializers.ValidationError({
                        'branch_id': 'Branch does not match the department\'s branch.'
                    })
                if city_id and dept.branch.city_id != city_id:
                    raise serializers.ValidationError({
                        'city_id': 'City does not match the department\'s city.'
                    })
            except Department.DoesNotExist:
                raise serializers.ValidationError({'department_id': 'Department not found.'})
        elif branch_id:
            try:
                branch = Branch.objects.select_related('city').get(id=branch_id)
                if city_id and branch.city_id != city_id:
                    raise serializers.ValidationError({
                        'city_id': 'City does not match the branch\'s city.'
                    })
            except Branch.DoesNotExist:
                raise serializers.ValidationError({'branch_id': 'Branch not found.'})
        elif city_id:
            if not City.objects.filter(id=city_id).exists():
                raise serializers.ValidationError({'city_id': 'City not found.'})
        
        return attrs
    
    def validate_employee_id(self, value):
        """Validate employee exists."""
        if not Employee.objects.filter(id=value).exists():
            raise serializers.ValidationError("Employee not found.")
        return value
    
    def validate_role_id(self, value):
        """Validate role exists and is active."""
        if not Role.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("Role not found or is inactive.")
        return value
    
    def create(self, validated_data):
        # Remove scope fields to handle them separately
        city_id = validated_data.pop('city_id', None)
        branch_id = validated_data.pop('branch_id', None)
        department_id = validated_data.pop('department_id', None)
        
        # Set granted_by from context
        request = self.context.get('request')
        if request and request.user:
            validated_data['granted_by'] = request.user
        
        return EmployeeRole.objects.create(
            city_id=city_id,
            branch_id=branch_id,
            department_id=department_id,
            **validated_data
        )


class EmployeeRoleListSerializer(serializers.ModelSerializer):
    """Compact employee role serializer for list views."""
    employee_email = serializers.CharField(source='employee.email', read_only=True)
    employee_name = serializers.SerializerMethodField()
    role_name = serializers.CharField(source='role.name', read_only=True)
    scope_level = serializers.CharField(read_only=True)
    
    class Meta:
        model = EmployeeRole
        fields = [
            'id',
            'employee_email',
            'employee_name',
            'role_name',
            'scope_level',
            'is_active',
            'granted_at',
        ]
    
    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}".strip() or obj.employee.email


class EmployeeRoleUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating employee roles (limited fields)."""
    city_id = serializers.UUIDField(required=False, allow_null=True)
    branch_id = serializers.UUIDField(required=False, allow_null=True)
    department_id = serializers.UUIDField(required=False, allow_null=True)
    
    class Meta:
        model = EmployeeRole
        fields = [
            'is_active',
            'city_id',
            'branch_id',
            'department_id',
        ]
    
    def validate(self, attrs):
        """Validate scope consistency (same logic as create)."""
        city_id = attrs.get('city_id', self.instance.city_id if self.instance else None)
        branch_id = attrs.get('branch_id', self.instance.branch_id if self.instance else None)
        department_id = attrs.get('department_id', self.instance.department_id if self.instance else None)
        
        if department_id:
            try:
                dept = Department.objects.select_related('branch__city').get(id=department_id)
                if branch_id and dept.branch_id != branch_id:
                    raise serializers.ValidationError({
                        'branch_id': 'Branch does not match the department\'s branch.'
                    })
                if city_id and dept.branch.city_id != city_id:
                    raise serializers.ValidationError({
                        'city_id': 'City does not match the department\'s city.'
                    })
            except Department.DoesNotExist:
                raise serializers.ValidationError({'department_id': 'Department not found.'})
        elif branch_id:
            try:
                branch = Branch.objects.select_related('city').get(id=branch_id)
                if city_id and branch.city_id != city_id:
                    raise serializers.ValidationError({
                        'city_id': 'City does not match the branch\'s city.'
                    })
            except Branch.DoesNotExist:
                raise serializers.ValidationError({'branch_id': 'Branch not found.'})
        elif city_id:
            if not City.objects.filter(id=city_id).exists():
                raise serializers.ValidationError({'city_id': 'City not found.'})
        
        return attrs
    
    def update(self, instance, validated_data):
        # Handle is_active changes (revocation)
        if 'is_active' in validated_data and not validated_data['is_active'] and instance.is_active:
            # Mark as revoked
            request = self.context.get('request')
            if request and request.user:
                instance.revoke(request.user)
                return instance
        
        # Handle scope updates
        if 'city_id' in validated_data:
            instance.city_id = validated_data['city_id']
        if 'branch_id' in validated_data:
            instance.branch_id = validated_data['branch_id']
        if 'department_id' in validated_data:
            instance.department_id = validated_data['department_id']
        if 'is_active' in validated_data:
            instance.is_active = validated_data['is_active']
        
        instance.save()
        return instance
