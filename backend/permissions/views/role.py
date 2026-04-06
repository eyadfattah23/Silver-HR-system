#!/usr/bin/env python3
"""
Views for Role management.

Accessible by:
- Superusers (full CRUD)
- Users with permissions.manage_roles (create/update/delete)
- Users with permissions.view_roles (read only)
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from permissions.models import Role, RolePermission, Permission
from permissions.serializers import (
    RoleSerializer,
    RoleListSerializer,
    RoleCreateUpdateSerializer,
    AddPermissionToRoleSerializer,
)


class IsSuperUserOrHasRolePermission(permissions.BasePermission):
    """
    Permission class for role management.
    
    - Superusers: full access
    - permissions.manage_roles: create, update, delete
    - permissions.view_roles: read only
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        from permissions.utils import has_permission
        
        # Safe methods require view_roles permission
        if request.method in permissions.SAFE_METHODS:
            return has_permission(request.user, 'permissions.view_roles')
        
        # Unsafe methods require manage_roles permission
        return has_permission(request.user, 'permissions.manage_roles')


class RoleListCreateView(generics.ListCreateAPIView):
    """
    GET: List all roles
    POST: Create a new role (requires manage_roles permission)
    """
    queryset = Role.objects.all().order_by('name')
    permission_classes = [IsSuperUserOrHasRolePermission]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RoleCreateUpdateSerializer
        return RoleListSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by is_active if provided
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by is_system_role if provided
        is_system_role = self.request.query_params.get('is_system_role')
        if is_system_role is not None:
            queryset = queryset.filter(is_system_role=is_system_role.lower() == 'true')
        
        return queryset


class RoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve role details with permissions
    PUT/PATCH: Update role (requires manage_roles permission)
    DELETE: Delete role (requires manage_roles permission, cannot delete system roles)
    """
    queryset = Role.objects.all()
    permission_classes = [IsSuperUserOrHasRolePermission]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return RoleCreateUpdateSerializer
        return RoleSerializer
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Cannot delete system roles
        if instance.is_system_role:
            return Response(
                {'detail': 'Cannot delete a system role.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if role is assigned to any employees
        if instance.employee_roles.filter(is_active=True).exists():
            return Response(
                {'detail': 'Cannot delete a role that is assigned to employees. '
                           'Revoke all assignments first or deactivate the role.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().destroy(request, *args, **kwargs)


class RolePermissionView(APIView):
    """
    Manage permissions for a specific role.
    
    POST: Add a permission to the role
    DELETE: Remove a permission from the role
    """
    permission_classes = [IsSuperUserOrHasRolePermission]
    
    def get_role(self, pk):
        """Get the role object."""
        try:
            return Role.objects.get(pk=pk)
        except Role.DoesNotExist:
            return None
    
    def post(self, request, pk, format=None):
        """Add a permission to the role."""
        role = self.get_role(pk)
        if not role:
            return Response(
                {'detail': 'Role not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = AddPermissionToRoleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        permission_id = serializer.validated_data['permission_id']
        
        # Check if already assigned
        if RolePermission.objects.filter(role=role, permission_id=permission_id).exists():
            # Reactivate if inactive
            rp = RolePermission.objects.get(role=role, permission_id=permission_id)
            if not rp.is_active:
                rp.is_active = True
                rp.save()
                return Response(
                    {'detail': 'Permission reactivated for this role.'},
                    status=status.HTTP_200_OK
                )
            return Response(
                {'detail': 'Permission is already assigned to this role.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the role-permission link
        RolePermission.objects.create(
            role=role,
            permission_id=permission_id,
        )
        
        return Response(
            {'detail': 'Permission added to role.'},
            status=status.HTTP_201_CREATED
        )
    
    def delete(self, request, pk, permission_id, format=None):
        """Remove a permission from the role."""
        role = self.get_role(pk)
        if not role:
            return Response(
                {'detail': 'Role not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            rp = RolePermission.objects.get(role=role, permission_id=permission_id)
            rp.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except RolePermission.DoesNotExist:
            return Response(
                {'detail': 'Permission is not assigned to this role.'},
                status=status.HTTP_404_NOT_FOUND
            )
