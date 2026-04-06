#!/usr/bin/env python3
"""Serializers for EmployeeExtraPermission model and Give Permission flow."""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from permissions.models import EmployeeExtraPermission, Permission, EmployeeRole, RolePermission
from core.models import City, Branch, Department
from .permission import PermissionMinimalSerializer
from .employee_role import EmployeeMinimalSerializer

Employee = get_user_model()


class EmployeeExtraPermissionSerializer(serializers.ModelSerializer):
    """Full extra permission serializer."""
    employee = EmployeeMinimalSerializer(read_only=True)
    permission = PermissionMinimalSerializer(read_only=True)
    granted_by = EmployeeMinimalSerializer(read_only=True)
    scope = serializers.SerializerMethodField()
    
    # Write-only fields
    employee_id = serializers.UUIDField(write_only=True)
    permission_id = serializers.UUIDField(write_only=True)
    city_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    branch_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    department_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = EmployeeExtraPermission
        fields = [
            'id',
            'employee',
            'employee_id',
            'permission',
            'permission_id',
            'city_id',
            'branch_id',
            'department_id',
            'scope',
            'is_active',
            'granted_by',
            'granted_at',
        ]
        read_only_fields = [
            'id', 'employee', 'permission', 'scope',
            'granted_by', 'granted_at',
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
        """Validate scope consistency and uniqueness."""
        employee_id = attrs.get('employee_id')
        permission_id = attrs.get('permission_id')
        city_id = attrs.get('city_id')
        branch_id = attrs.get('branch_id')
        department_id = attrs.get('department_id')
        
        # Check if employee already has this permission
        existing = EmployeeExtraPermission.objects.filter(
            employee_id=employee_id,
            permission_id=permission_id,
        )
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise serializers.ValidationError({
                'permission_id': 'Employee already has this permission.'
            })
        
        # Validate scope relationships
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
    
    def validate_employee_id(self, value):
        """Validate employee exists."""
        if not Employee.objects.filter(id=value).exists():
            raise serializers.ValidationError("Employee not found.")
        return value
    
    def validate_permission_id(self, value):
        """Validate permission exists and is active."""
        if not Permission.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("Permission not found or is inactive.")
        return value
    
    def create(self, validated_data):
        city_id = validated_data.pop('city_id', None)
        branch_id = validated_data.pop('branch_id', None)
        department_id = validated_data.pop('department_id', None)
        
        request = self.context.get('request')
        if request and request.user:
            validated_data['granted_by'] = request.user
        
        return EmployeeExtraPermission.objects.create(
            city_id=city_id,
            branch_id=branch_id,
            department_id=department_id,
            **validated_data
        )


class EmployeeExtraPermissionListSerializer(serializers.ModelSerializer):
    """Compact extra permission serializer for list views."""
    employee_email = serializers.CharField(source='employee.email', read_only=True)
    employee_name = serializers.SerializerMethodField()
    permission_code = serializers.CharField(source='permission.code', read_only=True)
    permission_name = serializers.CharField(source='permission.name', read_only=True)
    granted_by_email = serializers.CharField(source='granted_by.email', read_only=True)
    scope_level = serializers.CharField(read_only=True)
    
    class Meta:
        model = EmployeeExtraPermission
        fields = [
            'id',
            'employee_email',
            'employee_name',
            'permission_code',
            'permission_name',
            'scope_level',
            'is_active',
            'granted_by_email',
            'granted_at',
        ]
    
    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}".strip() or obj.employee.email


class EmployeeExtraPermissionUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating extra permissions (limited fields)."""
    city_id = serializers.UUIDField(required=False, allow_null=True)
    branch_id = serializers.UUIDField(required=False, allow_null=True)
    department_id = serializers.UUIDField(required=False, allow_null=True)
    
    class Meta:
        model = EmployeeExtraPermission
        fields = [
            'is_active',
            'city_id',
            'branch_id',
            'department_id',
        ]


# =============================================================================
# Give Permission Serializer (for employees with give_own permission)
# =============================================================================

class GivePermissionSerializer(serializers.Serializer):
    """Serializer for the Give Permission endpoint."""
    recipient_id = serializers.UUIDField(help_text="ID of the employee to give the permission to")
    permission_code = serializers.CharField(help_text="Code of the permission to give")
    city_id = serializers.UUIDField(required=False, allow_null=True, help_text="Optional city scope")
    branch_id = serializers.UUIDField(required=False, allow_null=True, help_text="Optional branch scope")
    department_id = serializers.UUIDField(required=False, allow_null=True, help_text="Optional department scope")
    
    def validate_recipient_id(self, value):
        """Validate recipient exists."""
        if not Employee.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("Recipient not found or is inactive.")
        return value
    
    def validate_permission_code(self, value):
        """Validate permission exists and can be given."""
        try:
            permission = Permission.objects.get(code=value, is_active=True)
            if not permission.can_be_given:
                raise serializers.ValidationError("This permission cannot be shared.")
        except Permission.DoesNotExist:
            raise serializers.ValidationError("Permission not found.")
        return value
    
    def validate(self, attrs):
        """Validate the complete give permission request."""
        request = self.context.get('request')
        giver = request.user
        recipient_id = attrs['recipient_id']
        permission_code = attrs['permission_code']
        
        # Cannot give to yourself
        if str(giver.id) == str(recipient_id):
            raise serializers.ValidationError({
                'recipient_id': 'Cannot give permission to yourself.'
            })
        
        # Check if recipient already has this permission (via extra permissions)
        if EmployeeExtraPermission.objects.filter(
            employee_id=recipient_id,
            permission__code=permission_code,
            is_active=True,
        ).exists():
            raise serializers.ValidationError({
                'permission_code': 'Recipient already has this permission.'
            })
        
        # Superusers can give any permission without needing it via a role
        if giver.is_superuser:
            attrs['_giver_scope'] = None  # Superuser has global scope by default
            return attrs
        
        # Check if giver has this permission FROM A ROLE (not extra permission)
        giver_has_from_role = False
        giver_scope = None
        
        role_assignments = EmployeeRole.objects.filter(
            employee=giver,
            is_active=True,
            role__is_active=True,
        ).select_related('role', 'city', 'branch', 'department')
        
        for assignment in role_assignments:
            if assignment.role.has_permission(permission_code):
                giver_has_from_role = True
                giver_scope = assignment
                break
        
        if not giver_has_from_role:
            raise serializers.ValidationError({
                'permission_code': 'You can only give permissions from your roles (not extra permissions).'
            })
        
        # Store giver_scope for use in create
        attrs['_giver_scope'] = giver_scope
        
        # Validate scope
        city_id = attrs.get('city_id')
        branch_id = attrs.get('branch_id')
        department_id = attrs.get('department_id')
        
        if department_id:
            try:
                dept = Department.objects.select_related('branch__city').get(id=department_id)
                if branch_id and dept.branch_id != branch_id:
                    raise serializers.ValidationError({
                        'branch_id': 'Branch does not match the department.'
                    })
                if city_id and dept.branch.city_id != city_id:
                    raise serializers.ValidationError({
                        'city_id': 'City does not match the department.'
                    })
            except Department.DoesNotExist:
                raise serializers.ValidationError({'department_id': 'Department not found.'})
        elif branch_id:
            try:
                branch = Branch.objects.select_related('city').get(id=branch_id)
                if city_id and branch.city_id != city_id:
                    raise serializers.ValidationError({
                        'city_id': 'City does not match the branch.'
                    })
            except Branch.DoesNotExist:
                raise serializers.ValidationError({'branch_id': 'Branch not found.'})
        elif city_id:
            if not City.objects.filter(id=city_id).exists():
                raise serializers.ValidationError({'city_id': 'City not found.'})
        
        return attrs
    
    @transaction.atomic
    def create(self, validated_data):
        """Create the extra permission for the recipient."""
        request = self.context.get('request')
        giver = request.user
        recipient_id = validated_data['recipient_id']
        permission_code = validated_data['permission_code']
        giver_scope = validated_data.pop('_giver_scope')
        
        # Determine the scope for the new permission
        requested_city_id = validated_data.get('city_id')
        requested_branch_id = validated_data.get('branch_id')
        requested_department_id = validated_data.get('department_id')
        
        # Calculate final scope based on giver's scope and requested scope
        final_city_id, final_branch_id, final_department_id = self._calculate_scope(
            giver_scope,
            requested_city_id,
            requested_branch_id,
            requested_department_id,
        )
        
        # Get the permission object
        permission = Permission.objects.get(code=permission_code)
        
        # Create the extra permission
        extra_perm = EmployeeExtraPermission.objects.create(
            employee_id=recipient_id,
            permission=permission,
            city_id=final_city_id,
            branch_id=final_branch_id,
            department_id=final_department_id,
            granted_by=giver,
        )
        
        return extra_perm
    
    def _calculate_scope(self, giver_scope, req_city_id, req_branch_id, req_department_id):
        """
        Calculate the final scope for the permission being given.
        
        Rules:
        - If giver_scope is None (superuser), use requested scope (or global if none)
        - If giver has global scope, use requested scope (or global if none)
        - If scopes overlap, use the narrower one
        - If scopes don't overlap, give global scope
        """
        # Superuser or giver has global scope - use requested scope (or global if none)
        if giver_scope is None or (not giver_scope.city_id and not giver_scope.branch_id and not giver_scope.department_id):
            return req_city_id, req_branch_id, req_department_id
        
        # No scope requested - use giver's scope
        if not req_city_id and not req_branch_id and not req_department_id:
            return giver_scope.city_id, giver_scope.branch_id, giver_scope.department_id
        
        # Check if scopes overlap
        if self._scopes_overlap(giver_scope, req_city_id, req_branch_id, req_department_id):
            # Use the narrower scope (requested or giver's, whichever is more specific)
            return self._get_narrower_scope(
                giver_scope, req_city_id, req_branch_id, req_department_id
            )
        else:
            # Non-overlapping scopes - give global
            return None, None, None
    
    def _scopes_overlap(self, giver_scope, req_city_id, req_branch_id, req_department_id):
        """Check if giver's scope overlaps with requested scope."""
        # Load related objects for comparison
        if req_department_id:
            try:
                dept = Department.objects.select_related('branch__city').get(id=req_department_id)
                req_branch = dept.branch
                req_city = dept.branch.city
            except Department.DoesNotExist:
                return False
        elif req_branch_id:
            try:
                req_branch = Branch.objects.select_related('city').get(id=req_branch_id)
                req_city = req_branch.city
            except Branch.DoesNotExist:
                return False
        elif req_city_id:
            req_branch = None
            req_city = City.objects.filter(id=req_city_id).first()
        else:
            return True  # No scope requested, always overlaps
        
        # Giver has department scope
        if giver_scope.department_id:
            if req_department_id:
                return giver_scope.department_id == req_department_id
            if req_branch_id:
                return giver_scope.department.branch_id == req_branch_id
            if req_city_id:
                return giver_scope.department.branch.city_id == req_city_id
        
        # Giver has branch scope
        if giver_scope.branch_id:
            if req_department_id:
                return req_branch and giver_scope.branch_id == req_branch.id
            if req_branch_id:
                return giver_scope.branch_id == req_branch_id
            if req_city_id:
                return giver_scope.branch.city_id == req_city_id
        
        # Giver has city scope
        if giver_scope.city_id:
            if req_department_id:
                return req_city and giver_scope.city_id == req_city.id
            if req_branch_id:
                return req_city and giver_scope.city_id == req_city.id
            if req_city_id:
                return giver_scope.city_id == req_city_id
        
        return False
    
    def _get_narrower_scope(self, giver_scope, req_city_id, req_branch_id, req_department_id):
        """Get the narrower (more specific) scope between giver's and requested."""
        # Department is the most specific
        if req_department_id:
            return None, None, req_department_id
        if giver_scope.department_id:
            return None, None, giver_scope.department_id
        
        # Branch is next
        if req_branch_id:
            return None, req_branch_id, None
        if giver_scope.branch_id:
            return None, giver_scope.branch_id, None
        
        # City is least specific
        if req_city_id:
            return req_city_id, None, None
        if giver_scope.city_id:
            return giver_scope.city_id, None, None
        
        return None, None, None
