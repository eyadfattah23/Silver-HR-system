#!/usr/bin/env python3
"""
Views for Employee Extra Permission management.

Accessible by:
- Superusers (full CRUD)
- Users with permissions.edit_employee (grant/revoke extra permissions)
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from permissions.models import EmployeeExtraPermission
from permissions.serializers import (
    EmployeeExtraPermissionSerializer,
    EmployeeExtraPermissionListSerializer,
    EmployeeExtraPermissionUpdateSerializer,
)


class IsSuperUserOrCanEditEmployeePermissions(permissions.BasePermission):
    """Allow superusers or users with permissions.edit_employee permission."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        from permissions.utils import has_permission
        return has_permission(request.user, 'permissions.edit_employee')


class ExtraPermissionListCreateView(generics.ListCreateAPIView):
    """
    GET: List all extra permission grants
    POST: Grant an extra permission to an employee
    """
    permission_classes = [IsSuperUserOrCanEditEmployeePermissions]
    
    def get_queryset(self):
        queryset = EmployeeExtraPermission.objects.select_related(
            'employee', 'permission', 'granted_by',
            'city', 'branch', 'department'
        ).order_by('-granted_at')
        
        # Filter by employee if provided
        employee_id = self.request.query_params.get('employee')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        # Filter by permission if provided
        permission_id = self.request.query_params.get('permission')
        if permission_id:
            queryset = queryset.filter(permission_id=permission_id)
        
        # Filter by permission code if provided
        permission_code = self.request.query_params.get('permission_code')
        if permission_code:
            queryset = queryset.filter(permission__code=permission_code)
        
        # Filter by is_active if provided
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EmployeeExtraPermissionSerializer
        return EmployeeExtraPermissionListSerializer


class ExtraPermissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve extra permission details
    PATCH: Update (scope, status)
    DELETE: Revoke the extra permission
    """
    queryset = EmployeeExtraPermission.objects.select_related(
        'employee', 'permission', 'granted_by',
        'city', 'branch', 'department'
    )
    permission_classes = [IsSuperUserOrCanEditEmployeePermissions]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return EmployeeExtraPermissionUpdateSerializer
        return EmployeeExtraPermissionSerializer
    
    def destroy(self, request, *args, **kwargs):
        """Delete the extra permission grant."""
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
