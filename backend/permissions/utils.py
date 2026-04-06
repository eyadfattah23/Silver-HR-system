#!/usr/bin/env python3
"""
Permission checking utilities for the Silver HR application.

This module provides:
- Custom DRF permission classes
- Helper functions for checking permissions with scope support
- Mixins for views that need permission checking
"""

from rest_framework import permissions
from django.db.models import Q


class HasPermission(permissions.BasePermission):
    """
    Custom permission class that checks if user has a specific permission.
    
    Usage in views:
        permission_classes = [HasPermission]
        required_permission = 'employees.view'
    
    Or with action mapping:
        permission_classes = [HasPermission]
        permission_map = {
            'list': 'employees.view',
            'create': 'employees.create',
            'retrieve': 'employees.view',
            'update': 'employees.update',
            'destroy': 'employees.delete',
        }
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers have all permissions
        if request.user.is_superuser:
            return True
        
        # Get required permission from view
        required_permission = self._get_required_permission(request, view)
        if not required_permission:
            return False
        
        # Check if user has the permission
        return has_permission(request.user, required_permission)
    
    def _get_required_permission(self, request, view):
        """Get the required permission code from the view."""
        # Check for action-based permission map
        permission_map = getattr(view, 'permission_map', None)
        if permission_map:
            action = getattr(view, 'action', None)
            if action and action in permission_map:
                return permission_map[action]
        
        # Fall back to single required_permission
        return getattr(view, 'required_permission', None)


class HasPermissionOrReadOnly(HasPermission):
    """
    Allow read access to authenticated users, write access requires permission.
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return super().has_permission(request, view)


class IsSuperUserOrHasPermission(permissions.BasePermission):
    """
    Allow superusers full access, others need specific permission.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        # Get required permission from view
        required_permission = getattr(view, 'required_permission', None)
        if not required_permission:
            return False
        
        return has_permission(request.user, required_permission)


class CanViewOwn(permissions.BasePermission):
    """
    Permission class for endpoints where users can view their own data.
    Used with get_queryset() filtering to show only own records.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers can access all
        if request.user.is_superuser:
            return True
        
        # Check for view_own permission
        view_own_permission = getattr(view, 'view_own_permission', None)
        if view_own_permission:
            return has_permission(request.user, view_own_permission)
        
        # Default: authenticated users can view their own
        return True


# =============================================================================
# Permission Helper Functions
# =============================================================================

def has_permission(user, permission_code, city=None, branch=None, department=None):
    """
    Check if a user has a specific permission, optionally within a scope.
    
    Args:
        user: The user to check
        permission_code: The permission code (e.g., 'employees.view')
        city: Optional city to check scope against
        branch: Optional branch to check scope against
        department: Optional department to check scope against
    
    Returns:
        bool: True if user has the permission (with appropriate scope)
    """
    if not user or not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    # Check role permissions
    if _has_role_permission(user, permission_code, city, branch, department):
        return True
    
    # Check extra permissions
    if _has_extra_permission(user, permission_code, city, branch, department):
        return True
    
    return False


def _has_role_permission(user, permission_code, city=None, branch=None, department=None):
    """Check if user has permission via their roles."""
    from permissions.models import EmployeeRole
    
    # Get active role assignments for this user
    role_assignments = EmployeeRole.objects.filter(
        employee=user,
        is_active=True,
        role__is_active=True,
    ).select_related('role', 'city', 'branch', 'department')
    
    for assignment in role_assignments:
        # Check if this role has the permission
        if not assignment.role.has_permission(permission_code):
            continue
        
        # Check if the scope applies
        if assignment.applies_to(city=city, branch=branch, department=department):
            return True
    
    return False


def _has_extra_permission(user, permission_code, city=None, branch=None, department=None):
    """Check if user has permission via extra permissions."""
    from permissions.models import EmployeeExtraPermission
    
    # Get active extra permissions for this user
    extra_permissions = EmployeeExtraPermission.objects.filter(
        employee=user,
        is_active=True,
        permission__code=permission_code,
        permission__is_active=True,
    ).select_related('permission', 'city', 'branch', 'department')
    
    for extra in extra_permissions:
        if extra.applies_to(city=city, branch=branch, department=department):
            return True
    
    return False


def get_user_permissions(user):
    """
    Get all effective permissions for a user.
    
    Returns:
        list: List of dicts with permission info and scope
    """
    if not user or not user.is_authenticated:
        return []
    
    permissions_list = []
    seen = set()  # Track (permission_code, scope_key) to avoid duplicates
    
    # Get role permissions
    from permissions.models import EmployeeRole, RolePermission
    
    role_assignments = EmployeeRole.objects.filter(
        employee=user,
        is_active=True,
        role__is_active=True,
    ).select_related('role', 'city', 'branch', 'department')
    
    for assignment in role_assignments:
        role_permissions = RolePermission.objects.filter(
            role=assignment.role,
            is_active=True,
            permission__is_active=True,
        ).select_related('permission')
        
        for rp in role_permissions:
            scope_key = _get_scope_key(assignment)
            perm_key = (rp.permission.code, scope_key)
            
            if perm_key not in seen:
                seen.add(perm_key)
                permissions_list.append({
                    'code': rp.permission.code,
                    'name': rp.permission.name,
                    'resource': rp.permission.resource,
                    'action': rp.permission.action,
                    'can_be_given': rp.permission.can_be_given,
                    'source': 'role',
                    'role_name': assignment.role.name,
                    'scope': _get_scope_dict(assignment),
                })
    
    # Get extra permissions
    from permissions.models import EmployeeExtraPermission
    
    extra_permissions = EmployeeExtraPermission.objects.filter(
        employee=user,
        is_active=True,
        permission__is_active=True,
    ).select_related('permission', 'city', 'branch', 'department')
    
    for extra in extra_permissions:
        scope_key = _get_scope_key(extra)
        perm_key = (extra.permission.code, scope_key)
        
        if perm_key not in seen:
            seen.add(perm_key)
            permissions_list.append({
                'code': extra.permission.code,
                'name': extra.permission.name,
                'resource': extra.permission.resource,
                'action': extra.permission.action,
                'can_be_given': extra.permission.can_be_given,
                'source': 'extra',
                'role_name': None,
                'scope': _get_scope_dict(extra),
            })
    
    return permissions_list


def get_user_roles(user):
    """
    Get all active roles for a user.
    
    Returns:
        list: List of dicts with role info and scope
    """
    if not user or not user.is_authenticated:
        return []
    
    from permissions.models import EmployeeRole
    
    roles_list = []
    role_assignments = EmployeeRole.objects.filter(
        employee=user,
        is_active=True,
        role__is_active=True,
    ).select_related('role', 'city', 'branch', 'department')
    
    for assignment in role_assignments:
        roles_list.append({
            'id': str(assignment.id),
            'role_id': str(assignment.role.id),
            'role_name': assignment.role.name,
            'role_description': assignment.role.description,
            'is_system_role': assignment.role.is_system_role,
            'scope': _get_scope_dict(assignment),
            'granted_at': assignment.granted_at,
        })
    
    return roles_list


def get_giveable_permissions(user):
    """
    Get permissions that a user can give to others.
    
    For superusers: Returns all permissions with can_be_given=True.
    For regular users: Only returns permissions that come from roles 
    (not extra permissions) and have can_be_given=True.
    """
    if not user or not user.is_authenticated:
        return []
    
    # User must have give_own permission
    if not has_permission(user, 'permissions.give_own'):
        return []
    
    from permissions.models import Permission, EmployeeRole, RolePermission
    
    # Superusers can give any giveable permission
    if user.is_superuser:
        giveable = []
        for perm in Permission.objects.filter(is_active=True, can_be_given=True):
            giveable.append({
                'id': str(perm.id),
                'code': perm.code,
                'name': perm.name,
                'resource': perm.resource,
                'action': perm.action,
                'scope': {'level': 'global', 'city': None, 'branch': None, 'department': None},
            })
        return giveable
    
    giveable = []
    seen = set()
    
    role_assignments = EmployeeRole.objects.filter(
        employee=user,
        is_active=True,
        role__is_active=True,
    ).select_related('role', 'city', 'branch', 'department')
    
    for assignment in role_assignments:
        role_permissions = RolePermission.objects.filter(
            role=assignment.role,
            is_active=True,
            permission__is_active=True,
            permission__can_be_given=True,  # Only giveable permissions
        ).select_related('permission')
        
        for rp in role_permissions:
            perm_key = rp.permission.code
            
            if perm_key not in seen:
                seen.add(perm_key)
                giveable.append({
                    'code': rp.permission.code,
                    'name': rp.permission.name,
                    'resource': rp.permission.resource,
                    'action': rp.permission.action,
                    'source_role': assignment.role.name,
                    'source_scope': _get_scope_dict(assignment),
                })
    
    return giveable


def _get_scope_key(obj):
    """Get a hashable scope key from an object with city/branch/department."""
    if obj.department_id:
        return ('department', obj.department_id)
    if obj.branch_id:
        return ('branch', obj.branch_id)
    if obj.city_id:
        return ('city', obj.city_id)
    return ('global', None)


def _get_scope_dict(obj):
    """Get scope dictionary from an object with city/branch/department."""
    scope = {
        'level': 'global',
        'city': None,
        'branch': None,
        'department': None,
    }
    
    if obj.department_id:
        scope['level'] = 'department'
        scope['department'] = {
            'id': str(obj.department_id),
            'name': obj.department.name if obj.department else None,
        }
        # Also include branch and city for context
        if obj.department and obj.department.branch:
            scope['branch'] = {
                'id': str(obj.department.branch_id),
                'name': obj.department.branch.name,
            }
            if obj.department.branch.city:
                scope['city'] = {
                    'id': str(obj.department.branch.city_id),
                    'name': obj.department.branch.city.name,
                }
    elif obj.branch_id:
        scope['level'] = 'branch'
        scope['branch'] = {
            'id': str(obj.branch_id),
            'name': obj.branch.name if obj.branch else None,
        }
        if obj.branch and obj.branch.city:
            scope['city'] = {
                'id': str(obj.branch.city_id),
                'name': obj.branch.city.name,
            }
    elif obj.city_id:
        scope['level'] = 'city'
        scope['city'] = {
            'id': str(obj.city_id),
            'name': obj.city.name if obj.city else None,
        }
    
    return scope


# =============================================================================
# Permission-Filtered QuerySet Mixin
# =============================================================================

class PermissionScopedQuerySetMixin:
    """
    Mixin for views that need to filter querysets based on user's permission scope.
    
    Subclasses should define:
        - scope_filter_field: The field path to filter by scope (e.g., 'employee__department')
        - required_permission: The permission code to check for scope
    """
    
    scope_filter_field = None
    
    def get_scoped_queryset(self, queryset, permission_code):
        """Filter queryset based on user's permission scope."""
        user = self.request.user
        
        if not user or not user.is_authenticated:
            return queryset.none()
        
        if user.is_superuser:
            return queryset
        
        # Get all scopes where user has this permission
        scopes = self._get_permission_scopes(user, permission_code)
        
        if not scopes:
            return queryset.none()
        
        # Check for global scope
        if any(s['level'] == 'global' for s in scopes):
            return queryset
        
        # Build OR filter for all applicable scopes
        q_filter = Q()
        field_prefix = self.scope_filter_field + '__' if self.scope_filter_field else ''
        
        for scope in scopes:
            if scope['level'] == 'city' and scope['city']:
                q_filter |= Q(**{f'{field_prefix}branch__city_id': scope['city']['id']})
            elif scope['level'] == 'branch' and scope['branch']:
                q_filter |= Q(**{f'{field_prefix}branch_id': scope['branch']['id']})
            elif scope['level'] == 'department' and scope['department']:
                q_filter |= Q(**{f'{field_prefix}department_id': scope['department']['id']})
        
        return queryset.filter(q_filter) if q_filter else queryset.none()
    
    def _get_permission_scopes(self, user, permission_code):
        """Get all scopes where user has a specific permission."""
        scopes = []
        
        # From roles
        from permissions.models import EmployeeRole
        role_assignments = EmployeeRole.objects.filter(
            employee=user,
            is_active=True,
            role__is_active=True,
        ).select_related('role', 'city', 'branch', 'department')
        
        for assignment in role_assignments:
            if assignment.role.has_permission(permission_code):
                scopes.append(_get_scope_dict(assignment))
        
        # From extra permissions
        from permissions.models import EmployeeExtraPermission
        extra_permissions = EmployeeExtraPermission.objects.filter(
            employee=user,
            is_active=True,
            permission__code=permission_code,
            permission__is_active=True,
        ).select_related('city', 'branch', 'department')
        
        for extra in extra_permissions:
            scopes.append(_get_scope_dict(extra))
        
        return scopes
