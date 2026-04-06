#!/usr/bin/env python3
"""
Views for Department management.

Permission Structure:
- Users with core.view: Can view departments
- Users with core.manage: Can create, update, delete departments
- Superusers: Full access
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from permissions.utils import has_permission

from ..models import Department
from ..serializers import (
    DepartmentSerializer,
    DepartmentListSerializer,
    DepartmentCreateUpdateSerializer,
)


class HasCorePermission(permissions.BasePermission):
    """
    Permission class for core endpoints (cities, branches, departments).
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        # Safe methods require view permission
        if request.method in permissions.SAFE_METHODS:
            return has_permission(request.user, 'core.view')
        
        # Unsafe methods require manage permission
        return has_permission(request.user, 'core.manage')


class DepartmentListCreateView(generics.ListCreateAPIView):
    """
    View for listing and creating departments.

    GET: List all departments (requires core.view)
    POST: Create a new department (requires core.manage)
    """
    queryset = Department.objects.all().select_related('branch', 'branch__city').order_by('branch__city__name', 'branch__name', 'name')
    permission_classes = [HasCorePermission]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DepartmentCreateUpdateSerializer
        return DepartmentListSerializer


class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for managing individual departments.

    GET: Retrieve department details (requires core.view)
    PUT/PATCH: Update department data (requires core.manage)
    DELETE: Deactivate department (requires core.manage)
    """
    queryset = Department.objects.all().select_related('branch', 'branch__city')
    permission_classes = [HasCorePermission]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return DepartmentCreateUpdateSerializer
        return DepartmentSerializer

    def destroy(self, request, *args, **kwargs):
        """Soft delete: set is_active to False instead of deleting."""
        department = self.get_object()
        department.is_active = False
        department.save()
        return Response(
            {'detail': 'Department deactivated successfully.'},
            status=status.HTTP_200_OK
        )


class ActiveDepartmentListView(generics.ListAPIView):
    """
    View for listing active departments.

    GET: List only active departments (requires core.view)
    """
    queryset = Department.objects.filter(is_active=True).select_related('branch', 'branch__city').order_by('branch__city__name', 'branch__name', 'name')
    permission_classes = [HasCorePermission]
    serializer_class = DepartmentListSerializer
