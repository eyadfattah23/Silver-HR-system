#!/usr/bin/env python3
"""
Views for Department management.

Permission Structure:
- Only superusers can manage departments (CRUD)
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from ..models import Department
from ..serializers import (
    DepartmentSerializer,
    DepartmentListSerializer,
    DepartmentCreateUpdateSerializer,
)


class IsSuperUser(permissions.BasePermission):
    """Permission class that only allows superusers."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser


class DepartmentListCreateView(generics.ListCreateAPIView):
    """
    Super admin-only view.

    GET: List all departments
    POST: Create a new department
    """
    queryset = Department.objects.all().select_related('branch', 'branch__city').order_by('branch__city__name', 'branch__name', 'name')
    permission_classes = [IsSuperUser]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DepartmentCreateUpdateSerializer
        return DepartmentListSerializer


class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Super admin-only view for managing individual departments.

    GET: Retrieve department details
    PUT/PATCH: Update department data
    DELETE: Deactivate department (soft delete by setting is_active=False)
    """
    queryset = Department.objects.all().select_related('branch', 'branch__city')
    permission_classes = [IsSuperUser]

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
    Super admin-only view.

    GET: List only active departments
    """
    queryset = Department.objects.filter(is_active=True).select_related('branch', 'branch__city').order_by('branch__city__name', 'branch__name', 'name')
    permission_classes = [IsSuperUser]
    serializer_class = DepartmentListSerializer
