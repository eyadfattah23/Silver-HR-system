#!/usr/bin/env python3
"""
Views for Employee Role management.

Accessible by:
- Superusers (full CRUD)
- Users with permissions.assign_roles (assign/revoke roles)
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from permissions.models import EmployeeRole
from permissions.serializers import (
    EmployeeRoleSerializer,
    EmployeeRoleListSerializer,
    EmployeeRoleUpdateSerializer,
)


class IsSuperUserOrCanAssignRoles(permissions.BasePermission):
    """Allow superusers or users with permissions.assign_roles permission."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        from permissions.utils import has_permission
        return has_permission(request.user, 'permissions.assign_roles')


class EmployeeRoleListCreateView(generics.ListCreateAPIView):
    """
    GET: List all employee role assignments
    POST: Assign a role to an employee
    """
    permission_classes = [IsSuperUserOrCanAssignRoles]
    
    def get_queryset(self):
        queryset = EmployeeRole.objects.select_related(
            'employee', 'role', 'granted_by', 'city', 'branch', 'department'
        ).order_by('-granted_at')
        
        # Filter by employee if provided
        employee_id = self.request.query_params.get('employee')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        # Filter by role if provided
        role_id = self.request.query_params.get('role')
        if role_id:
            queryset = queryset.filter(role_id=role_id)
        
        # Filter by is_active if provided
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EmployeeRoleSerializer
        return EmployeeRoleListSerializer


class EmployeeRoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve employee role assignment details
    PATCH: Update assignment (scope, status)
    DELETE: Revoke the role assignment
    """
    queryset = EmployeeRole.objects.select_related(
        'employee', 'role', 'granted_by', 'revoked_by',
        'city', 'branch', 'department'
    )
    permission_classes = [IsSuperUserOrCanAssignRoles]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return EmployeeRoleUpdateSerializer
        return EmployeeRoleSerializer
    
    def destroy(self, request, *args, **kwargs):
        """Revoke the role assignment (soft delete)."""
        instance = self.get_object()
        
        if not instance.is_active:
            return Response(
                {'detail': 'Role assignment is already revoked.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        instance.revoke(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
