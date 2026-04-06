#!/usr/bin/env python3
"""
Self-service views for employees to view their own permissions and roles,
and to give permissions to others (if they have the give_own permission).
"""

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from permissions.utils import (
    get_user_permissions,
    get_user_roles,
    get_giveable_permissions,
    has_permission,
)
from permissions.serializers import (
    EmployeeExtraPermissionSerializer,
    GivePermissionSerializer,
)


class MyPermissionsView(APIView):
    """
    GET: Get current user's effective permissions.
    
    Returns all permissions the user has from:
    - Their assigned roles
    - Extra permissions granted to them
    
    Includes scope information for each permission.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, format=None):
        user = request.user
        
        # Get all effective permissions
        permissions_list = get_user_permissions(user)
        
        # Group by resource for easier frontend consumption
        by_resource = {}
        for perm in permissions_list:
            resource = perm['resource']
            if resource not in by_resource:
                by_resource[resource] = []
            by_resource[resource].append(perm)
        
        return Response({
            'permissions': permissions_list,
            'by_resource': by_resource,
            'is_superuser': user.is_superuser,
            'total_count': len(permissions_list),
        })


class MyRolesView(APIView):
    """
    GET: Get current user's assigned roles.
    
    Returns all active role assignments with scope information.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, format=None):
        user = request.user
        
        roles_list = get_user_roles(user)
        
        return Response({
            'roles': roles_list,
            'total_count': len(roles_list),
        })


class GiveablePermissionsView(APIView):
    """
    GET: Get permissions that the current user can give to others.
    
    Only returns permissions that:
    - Come from the user's roles (not extra permissions)
    - Have can_be_given=True
    
    Requires the user to have permissions.give_own.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, format=None):
        user = request.user
        
        # Check if user has give_own permission
        if not has_permission(user, 'permissions.give_own'):
            return Response({
                'detail': 'You do not have permission to give permissions to others.',
                'permissions': [],
                'can_give': False,
            }, status=status.HTTP_403_FORBIDDEN)
        
        giveable = get_giveable_permissions(user)
        
        return Response({
            'permissions': giveable,
            'can_give': True,
            'total_count': len(giveable),
        })


class GivePermissionView(APIView):
    """
    POST: Give a permission to another employee.
    
    Requirements:
    - User must have permissions.give_own permission
    - Permission must be from user's role (not extra permission)
    - Permission must have can_be_given=True
    - Recipient must not already have the permission
    
    Scope rules:
    - If giver has global scope, recipient gets requested scope (or global)
    - If scopes overlap, recipient gets the narrower scope
    - If scopes don't overlap, recipient gets global scope
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, format=None):
        # Check if user has give_own permission
        if not has_permission(request.user, 'permissions.give_own'):
            return Response(
                {'detail': 'You do not have permission to give permissions to others.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = GivePermissionSerializer(data=request.data, context={'request': request})
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Create the extra permission
        extra_perm = serializer.save()
        
        # Return the created extra permission
        response_serializer = EmployeeExtraPermissionSerializer(
            extra_perm,
            context={'request': request}
        )
        
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
