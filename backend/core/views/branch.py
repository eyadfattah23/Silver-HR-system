#!/usr/bin/env python3
"""
Views for Branch management.

Permission Structure:
- Users with core.view: Can view branches
- Users with core.manage: Can create, update, delete branches
- Superusers: Full access
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from permissions.utils import has_permission

from ..models import Branch
from ..serializers import (
    BranchSerializer,
    BranchListSerializer,
    BranchCreateUpdateSerializer,
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


class BranchListCreateView(generics.ListCreateAPIView):
    """
    View for listing and creating branches.

    GET: List all branches (requires core.view)
    POST: Create a new branch (requires core.manage)
    """
    queryset = Branch.objects.all().select_related('city').order_by('city__name', 'name')
    permission_classes = [HasCorePermission]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BranchCreateUpdateSerializer
        return BranchListSerializer


class BranchDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for managing individual branches.

    GET: Retrieve branch details (requires core.view)
    PUT/PATCH: Update branch data (requires core.manage)
    DELETE: Deactivate branch (requires core.manage)
    """
    queryset = Branch.objects.all().select_related('city')
    permission_classes = [HasCorePermission]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return BranchCreateUpdateSerializer
        return BranchSerializer

    def destroy(self, request, *args, **kwargs):
        """Soft delete: set is_active to False instead of deleting."""
        branch = self.get_object()
        branch.is_active = False
        branch.save()
        return Response(
            {'detail': 'Branch deactivated successfully.'},
            status=status.HTTP_200_OK
        )


class ActiveBranchListView(generics.ListAPIView):
    """
    View for listing active branches.

    GET: List only active branches (requires core.view)
    """
    queryset = Branch.objects.filter(is_active=True).select_related('city').order_by('city__name', 'name')
    permission_classes = [HasCorePermission]
    serializer_class = BranchListSerializer
