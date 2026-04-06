#!/usr/bin/env python3
"""URL configuration for the permissions app."""

from django.urls import path

from .views import (
    # Permission (read-only)
    PermissionListView,
    PermissionDetailView,
    # Role
    RoleListCreateView,
    RoleDetailView,
    RolePermissionView,
    # Employee Role
    EmployeeRoleListCreateView,
    EmployeeRoleDetailView,
    # Extra Permission
    ExtraPermissionListCreateView,
    ExtraPermissionDetailView,
    # Self Service
    MyPermissionsView,
    MyRolesView,
    GiveablePermissionsView,
    GivePermissionView,
)

app_name = 'permissions'

urlpatterns = [
    # Permissions (read-only)
    path('', PermissionListView.as_view(), name='permission-list'),
    path('<uuid:pk>/', PermissionDetailView.as_view(), name='permission-detail'),
    
    # Roles
    path('roles/', RoleListCreateView.as_view(), name='role-list'),
    path('roles/<uuid:pk>/', RoleDetailView.as_view(), name='role-detail'),
    path('roles/<uuid:pk>/permissions/', RolePermissionView.as_view(), name='role-permission-add'),
    path('roles/<uuid:pk>/permissions/<uuid:permission_id>/', RolePermissionView.as_view(), name='role-permission-remove'),
    
    # Employee Roles
    path('employee-roles/', EmployeeRoleListCreateView.as_view(), name='employee-role-list'),
    path('employee-roles/<uuid:pk>/', EmployeeRoleDetailView.as_view(), name='employee-role-detail'),
    
    # Extra Permissions
    path('extra-permissions/', ExtraPermissionListCreateView.as_view(), name='extra-permission-list'),
    path('extra-permissions/<uuid:pk>/', ExtraPermissionDetailView.as_view(), name='extra-permission-detail'),
    
    # Self-service endpoints
    path('my-permissions/', MyPermissionsView.as_view(), name='my-permissions'),
    path('my-roles/', MyRolesView.as_view(), name='my-roles'),
    path('giveable/', GiveablePermissionsView.as_view(), name='giveable-permissions'),
    path('give/', GivePermissionView.as_view(), name='give-permission'),
]
