#!/usr/bin/python3
"""
Data migration to create initial system permissions.

This migration creates all permissions defined in permissions/constants.py.
After this migration, use `python manage.py sync_permissions` to add new permissions.
"""
from django.db import migrations


# Permissions data (copied from constants.py to ensure migration is self-contained)
INITIAL_PERMISSIONS = [
    # EMPLOYEES
    {"code": "employees.view", "name": "View Employees", "description": "View employee profiles and basic information", "resource": "employees", "action": "view", "can_be_given": True},
    {"code": "employees.create", "name": "Create Employees", "description": "Create new employee records", "resource": "employees", "action": "create", "can_be_given": True},
    {"code": "employees.update", "name": "Update Employees", "description": "Update employee information", "resource": "employees", "action": "update", "can_be_given": True},
    {"code": "employees.delete", "name": "Delete Employees", "description": "Delete employee records", "resource": "employees", "action": "delete", "can_be_given": False},
    {"code": "employees.view_own", "name": "View Own Profile", "description": "View own employee profile", "resource": "employees", "action": "view_own", "can_be_given": False},
    {"code": "employees.update_own", "name": "Update Own Profile", "description": "Update own employee profile (limited fields)", "resource": "employees", "action": "update_own", "can_be_given": False},
    
    # DOCUMENTS
    {"code": "documents.view", "name": "View Documents", "description": "View all documents in the system", "resource": "documents", "action": "view", "can_be_given": True},
    {"code": "documents.create", "name": "Create Documents", "description": "Upload new documents", "resource": "documents", "action": "create", "can_be_given": True},
    {"code": "documents.update", "name": "Update Documents", "description": "Update document metadata", "resource": "documents", "action": "update", "can_be_given": True},
    {"code": "documents.delete", "name": "Delete Documents", "description": "Delete documents", "resource": "documents", "action": "delete", "can_be_given": False},
    {"code": "documents.view_own", "name": "View Own Documents", "description": "View documents belonging to own profile", "resource": "documents", "action": "view_own", "can_be_given": False},
    
    # DOCUMENT TYPES
    {"code": "document_types.view", "name": "View Document Types", "description": "View document type definitions", "resource": "document_types", "action": "view", "can_be_given": True},
    {"code": "document_types.manage", "name": "Manage Document Types", "description": "Create, update, delete document types", "resource": "document_types", "action": "manage", "can_be_given": False},
    
    # CORE
    {"code": "core.view", "name": "View Organization Structure", "description": "View cities, branches, and departments", "resource": "core", "action": "view", "can_be_given": True},
    {"code": "core.manage", "name": "Manage Organization Structure", "description": "Create, update, delete cities, branches, departments", "resource": "core", "action": "manage", "can_be_given": False},
    
    # PERMISSIONS
    {"code": "permissions.view", "name": "View Permissions", "description": "View available permissions in the system", "resource": "permissions", "action": "view", "can_be_given": True},
    {"code": "permissions.view_roles", "name": "View Roles", "description": "View role definitions and their permissions", "resource": "permissions", "action": "view_roles", "can_be_given": True},
    {"code": "permissions.manage_roles", "name": "Manage Roles", "description": "Create, update, delete roles and assign permissions to roles", "resource": "permissions", "action": "manage_roles", "can_be_given": False},
    {"code": "permissions.assign_roles", "name": "Assign Roles to Employees", "description": "Assign and revoke roles for employees", "resource": "permissions", "action": "assign_roles", "can_be_given": False},
    {"code": "permissions.edit_employee", "name": "Edit Employee Permissions", "description": "Grant and revoke extra permissions for employees (super admin only)", "resource": "permissions", "action": "edit_employee", "can_be_given": False},
    {"code": "permissions.give_own", "name": "Give Own Permissions", "description": "Share role permissions with other employees", "resource": "permissions", "action": "give_own", "can_be_given": False},
    
    # ATTENDANCE
    {"code": "attendance.view", "name": "View Attendance", "description": "View attendance records", "resource": "attendance", "action": "view", "can_be_given": True},
    {"code": "attendance.manage", "name": "Manage Attendance", "description": "Create and update attendance records", "resource": "attendance", "action": "manage", "can_be_given": True},
    {"code": "attendance.view_own", "name": "View Own Attendance", "description": "View own attendance records", "resource": "attendance", "action": "view_own", "can_be_given": False},
    
    # LEAVE
    {"code": "leave.view", "name": "View Leave Requests", "description": "View leave requests", "resource": "leave", "action": "view", "can_be_given": True},
    {"code": "leave.create", "name": "Create Leave Requests", "description": "Submit leave requests", "resource": "leave", "action": "create", "can_be_given": False},
    {"code": "leave.approve", "name": "Approve Leave Requests", "description": "Approve or reject leave requests", "resource": "leave", "action": "approve", "can_be_given": True},
    {"code": "leave.view_own", "name": "View Own Leave", "description": "View own leave requests and balance", "resource": "leave", "action": "view_own", "can_be_given": False},
    
    # SALARY
    {"code": "salary.view", "name": "View Salaries", "description": "View salary information", "resource": "salary", "action": "view", "can_be_given": False},
    {"code": "salary.manage", "name": "Manage Salaries", "description": "Update salary information", "resource": "salary", "action": "manage", "can_be_given": False},
    {"code": "salary.view_own", "name": "View Own Salary", "description": "View own salary information", "resource": "salary", "action": "view_own", "can_be_given": False},
    
    # REPORTS
    {"code": "reports.view", "name": "View Reports", "description": "View system reports", "resource": "reports", "action": "view", "can_be_given": True},
    {"code": "reports.export", "name": "Export Reports", "description": "Export reports to files", "resource": "reports", "action": "export", "can_be_given": True},
]


def create_permissions(apps, schema_editor):
    """Create all initial permissions."""
    Permission = apps.get_model('permissions', 'Permission')
    
    for perm_data in INITIAL_PERMISSIONS:
        Permission.objects.get_or_create(
            code=perm_data['code'],
            defaults={
                'name': perm_data['name'],
                'description': perm_data['description'],
                'resource': perm_data['resource'],
                'action': perm_data['action'],
                'can_be_given': perm_data['can_be_given'],
                'is_active': True,
            }
        )


def delete_permissions(apps, schema_editor):
    """Delete all initial permissions (reverse migration)."""
    Permission = apps.get_model('permissions', 'Permission')
    codes = [p['code'] for p in INITIAL_PERMISSIONS]
    Permission.objects.filter(code__in=codes).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('permissions', '0005_simplify_permissions'),
    ]

    operations = [
        migrations.RunPython(create_permissions, delete_permissions),
    ]
