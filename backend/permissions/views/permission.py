#!/usr/bin/env python3
"""
Views for Permission management (read-only).

Permissions are system-defined and cannot be created/modified via API.
"""

from rest_framework import generics, permissions

from permissions.models import Permission
from permissions.serializers import PermissionSerializer, PermissionListSerializer


class IsSuperUserOrHasViewPermission(permissions.BasePermission):
    """Allow superusers or users with permissions.view permission."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        from permissions.utils import has_permission
        return has_permission(request.user, 'permissions.view')


class PermissionListView(generics.ListAPIView):
    """
    GET: List all available permissions.
    
    Accessible by:
    - Superusers
    - Users with permissions.view permission
    """
    queryset = Permission.objects.filter(is_active=True).order_by('resource', 'action')
    permission_classes = [IsSuperUserOrHasViewPermission]
    serializer_class = PermissionListSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by resource if provided
        resource = self.request.query_params.get('resource')
        if resource:
            queryset = queryset.filter(resource=resource)
        
        # Filter by can_be_given if provided
        can_be_given = self.request.query_params.get('can_be_given')
        if can_be_given is not None:
            queryset = queryset.filter(can_be_given=can_be_given.lower() == 'true')
        
        return queryset


class PermissionDetailView(generics.RetrieveAPIView):
    """
    GET: Retrieve a specific permission's details.
    
    Accessible by:
    - Superusers
    - Users with permissions.view permission
    """
    queryset = Permission.objects.filter(is_active=True)
    permission_classes = [IsSuperUserOrHasViewPermission]
    serializer_class = PermissionSerializer
