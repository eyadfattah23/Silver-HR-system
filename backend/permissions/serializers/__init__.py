#!/usr/bin/env python3
"""Serializers for the permissions app."""

from .permission import (
    PermissionSerializer,
    PermissionListSerializer,
    PermissionMinimalSerializer,
)
from .role import (
    RoleSerializer,
    RoleListSerializer,
    RoleCreateUpdateSerializer,
    RoleMinimalSerializer,
    RolePermissionSerializer,
    AddPermissionToRoleSerializer,
)
from .employee_role import (
    EmployeeRoleSerializer,
    EmployeeRoleListSerializer,
    EmployeeRoleUpdateSerializer,
    EmployeeMinimalSerializer,
)
from .extra_permission import (
    EmployeeExtraPermissionSerializer,
    EmployeeExtraPermissionListSerializer,
    EmployeeExtraPermissionUpdateSerializer,
    GivePermissionSerializer,
)

__all__ = [
    # Permission
    'PermissionSerializer',
    'PermissionListSerializer',
    'PermissionMinimalSerializer',
    # Role
    'RoleSerializer',
    'RoleListSerializer',
    'RoleCreateUpdateSerializer',
    'RoleMinimalSerializer',
    'RolePermissionSerializer',
    'AddPermissionToRoleSerializer',
    # Employee Role
    'EmployeeRoleSerializer',
    'EmployeeRoleListSerializer',
    'EmployeeRoleUpdateSerializer',
    'EmployeeMinimalSerializer',
    # Extra Permission
    'EmployeeExtraPermissionSerializer',
    'EmployeeExtraPermissionListSerializer',
    'EmployeeExtraPermissionUpdateSerializer',
    'GivePermissionSerializer',
]
