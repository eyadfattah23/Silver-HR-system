#!/usr/bin/env python3
"""
Views for Branch management.

Permission Structure:
- Only superusers can manage branches (CRUD)
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from ..models import Branch
from ..serializers import (
    BranchSerializer,
    BranchListSerializer,
    BranchCreateUpdateSerializer,
)


class IsSuperUser(permissions.BasePermission):
    """Permission class that only allows superusers."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser


class BranchListCreateView(generics.ListCreateAPIView):
    """
    Super admin-only view.

    GET: List all branches
    POST: Create a new branch
    """
    queryset = Branch.objects.all().select_related('city').order_by('city__name', 'name')
    permission_classes = [IsSuperUser]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BranchCreateUpdateSerializer
        return BranchListSerializer


class BranchDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Super admin-only view for managing individual branches.

    GET: Retrieve branch details
    PUT/PATCH: Update branch data
    DELETE: Deactivate branch (soft delete by setting is_active=False)
    """
    queryset = Branch.objects.all().select_related('city')
    permission_classes = [IsSuperUser]

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
    Super admin-only view.

    GET: List only active branches
    """
    queryset = Branch.objects.filter(is_active=True).select_related('city').order_by('city__name', 'name')
    permission_classes = [IsSuperUser]
    serializer_class = BranchListSerializer
