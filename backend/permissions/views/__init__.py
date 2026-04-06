#!/usr/bin/env python3
"""Views for the permissions app."""

from .permission import PermissionListView, PermissionDetailView
from .role import (
    RoleListCreateView,
    RoleDetailView,
    RolePermissionView,
)
from .employee_role import (
    EmployeeRoleListCreateView,
    EmployeeRoleDetailView,
)
from .extra_permission import (
    ExtraPermissionListCreateView,
    ExtraPermissionDetailView,
)
from .self_service import (
    MyPermissionsView,
    MyRolesView,
    GiveablePermissionsView,
    GivePermissionView,
)

__all__ = [
    # Permission
    'PermissionListView',
    'PermissionDetailView',
    # Role
    'RoleListCreateView',
    'RoleDetailView',
    'RolePermissionView',
    # Employee Role
    'EmployeeRoleListCreateView',
    'EmployeeRoleDetailView',
    # Extra Permission
    'ExtraPermissionListCreateView',
    'ExtraPermissionDetailView',
    # Self Service
    'MyPermissionsView',
    'MyRolesView',
    'GiveablePermissionsView',
    'GivePermissionView',
]
