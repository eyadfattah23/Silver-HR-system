#!/usr/bin/env python3
"""Views for JobTitle management."""

from rest_framework import generics, permissions

from permissions.utils import has_permission

from ..models import JobTitle
from ..serializers import (
    JobTitleSerializer,
    JobTitleListSerializer,
    JobTitleCreateUpdateSerializer,
)


class HasEmployeeManagePermission(permissions.BasePermission):
    """
    Permission class for job title management.
    Requires employees.update permission for write operations.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        # Safe methods require view permission
        if request.method in permissions.SAFE_METHODS:
            return has_permission(request.user, 'employees.view')
        
        # Unsafe methods require update permission
        return has_permission(request.user, 'employees.update')


class JobTitleListCreateView(generics.ListCreateAPIView):
    """
    View for listing and creating job titles.

    GET: List all job titles (requires employees.view)
    POST: Create a new job title (requires employees.update)
    """
    queryset = JobTitle.objects.all().order_by('name')
    permission_classes = [HasEmployeeManagePermission]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return JobTitleCreateUpdateSerializer
        return JobTitleListSerializer


class JobTitleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for managing individual job titles.

    GET: Retrieve job title details (requires employees.view)
    PUT/PATCH: Update job title (requires employees.update)
    DELETE: Delete job title (requires employees.update)
    """
    queryset = JobTitle.objects.all()
    permission_classes = [HasEmployeeManagePermission]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return JobTitleCreateUpdateSerializer
        return JobTitleSerializer


class ActiveJobTitleListView(generics.ListAPIView):
    """
    View for listing only active job titles (for dropdown selections).
    Available to all authenticated users.
    """
    queryset = JobTitle.objects.filter(is_active=True).order_by('name')
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = JobTitleListSerializer
