#!/usr/bin/python3
"""
System-defined permissions for the Silver HR application.

Permissions are defined here and synced to the database via:
- Data migration (initial setup)
- Management command: python manage.py sync_permissions (ongoing development)

DO NOT create permissions via admin or API - they are system constants.
"""

# All system permissions
# Format: {code, name, description, resource, action, can_be_given}
PERMISSIONS = [
    # ===================
    # EMPLOYEES
    # ===================
    {
        "code": "employees.view",
        "name": "View Employees",
        "description": "View employee profiles and basic information",
        "resource": "employees",
        "action": "view",
        "can_be_given": True,
    },
    {
        "code": "employees.create",
        "name": "Create Employees",
        "description": "Create new employee records",
        "resource": "employees",
        "action": "create",
        "can_be_given": True,
    },
    {
        "code": "employees.update",
        "name": "Update Employees",
        "description": "Update employee information",
        "resource": "employees",
        "action": "update",
        "can_be_given": True,
    },
    {
        "code": "employees.delete",
        "name": "Delete Employees",
        "description": "Delete employee records",
        "resource": "employees",
        "action": "delete",
        "can_be_given": False,  # Sensitive - super admin only
    },
    {
        "code": "employees.view_own",
        "name": "View Own Profile",
        "description": "View own employee profile",
        "resource": "employees",
        "action": "view_own",
        "can_be_given": False,  # Everyone has this by default
    },
    
    # ===================
    # DOCUMENTS
    # ===================
    {
        "code": "documents.view",
        "name": "View Documents",
        "description": "View all documents in the system",
        "resource": "documents",
        "action": "view",
        "can_be_given": True,
    },
    {
        "code": "documents.create",
        "name": "Create Documents",
        "description": "Upload new documents",
        "resource": "documents",
        "action": "create",
        "can_be_given": True,
    },
    {
        "code": "documents.update",
        "name": "Update Documents",
        "description": "Update document metadata",
        "resource": "documents",
        "action": "update",
        "can_be_given": True,
    },
    {
        "code": "documents.delete",
        "name": "Delete Documents",
        "description": "Delete documents",
        "resource": "documents",
        "action": "delete",
        "can_be_given": False,  # Sensitive
    },
    {
        "code": "documents.view_own",
        "name": "View Own Documents",
        "description": "View documents belonging to own profile",
        "resource": "documents",
        "action": "view_own",
        "can_be_given": False,
    },
    
    # ===================
    # DOCUMENT TYPES
    # ===================
    {
        "code": "document_types.view",
        "name": "View Document Types",
        "description": "View document type definitions",
        "resource": "document_types",
        "action": "view",
        "can_be_given": True,
    },
    {
        "code": "document_types.manage",
        "name": "Manage Document Types",
        "description": "Create, update, delete document types",
        "resource": "document_types",
        "action": "manage",
        "can_be_given": True,
    },
    
    # ===================
    # CORE (Cities, Branches, Departments)
    # ===================
    {
        "code": "core.view",
        "name": "View Organization Structure",
        "description": "View cities, branches, and departments",
        "resource": "core",
        "action": "view",
        "can_be_given": True,
    },
    {
        "code": "core.manage",
        "name": "Manage Organization Structure",
        "description": "Create, update, delete cities, branches, departments",
        "resource": "core",
        "action": "manage",
        "can_be_given": True,
    },
    
    # ===================
    # PERMISSIONS
    # ===================
    {
        "code": "permissions.view",
        "name": "View Permissions",
        "description": "View available permissions in the system",
        "resource": "permissions",
        "action": "view",
        "can_be_given": True,
    },
    {
        "code": "permissions.view_roles",
        "name": "View Roles",
        "description": "View role definitions and their permissions",
        "resource": "permissions",
        "action": "view_roles",
        "can_be_given": True,
    },
    {
        "code": "permissions.manage_roles",
        "name": "Manage Roles",
        "description": "Create, update, delete roles and assign permissions to roles",
        "resource": "permissions",
        "action": "manage_roles",
        "can_be_given": True,
    },
    {
        "code": "permissions.assign_roles",
        "name": "Assign Roles to Employees",
        "description": "Assign and revoke roles for employees",
        "resource": "permissions",
        "action": "assign_roles",
        "can_be_given": True,
    },
    {
        "code": "permissions.edit_employee",
        "name": "Edit Employee Permissions",
        "description": "Grant and revoke extra permissions for employees (super admin only)",
        "resource": "permissions",
        "action": "edit_employee",
        "can_be_given": False,  # Super admin only - cannot be given
    },
    {
        "code": "permissions.give_own",
        "name": "Give Own Permissions",
        "description": "Share role permissions with other employees",
        "resource": "permissions",
        "action": "give_own",
        "can_be_given": False,  # Cannot give this permission via give_own
    },
    
    # ===================
    # ATTENDANCE (Future)
    # ===================
    {
        "code": "attendance.view",
        "name": "View Attendance",
        "description": "View attendance records",
        "resource": "attendance",
        "action": "view",
        "can_be_given": True,
    },
    {
        "code": "attendance.manage",
        "name": "Manage Attendance",
        "description": "Create and update attendance records",
        "resource": "attendance",
        "action": "manage",
        "can_be_given": True,
    },
    {
        "code": "attendance.view_own",
        "name": "View Own Attendance",
        "description": "View own attendance records",
        "resource": "attendance",
        "action": "view_own",
        "can_be_given": False,
    },
    
    # ===================
    # LEAVE (Future)
    # ===================
    {
        "code": "leave.view",
        "name": "View Leave Requests",
        "description": "View leave requests",
        "resource": "leave",
        "action": "view",
        "can_be_given": True,
    },
    {
        "code": "leave.create",
        "name": "Create Leave Requests",
        "description": "Submit leave requests",
        "resource": "leave",
        "action": "create",
        "can_be_given": False,  # Everyone can create their own
    },
    {
        "code": "leave.approve",
        "name": "Approve Leave Requests",
        "description": "Approve or reject leave requests",
        "resource": "leave",
        "action": "approve",
        "can_be_given": True,
    },
    {
        "code": "leave.view_own",
        "name": "View Own Leave",
        "description": "View own leave requests and balance",
        "resource": "leave",
        "action": "view_own",
        "can_be_given": False,
    },
    
    # ===================
    # SALARY (Future)
    # ===================
    {
        "code": "salary.view",
        "name": "View Salaries",
        "description": "View salary information",
        "resource": "salary",
        "action": "view",
        "can_be_given": False,  # Sensitive - no delegation
    },
    {
        "code": "salary.manage",
        "name": "Manage Salaries",
        "description": "Update salary information",
        "resource": "salary",
        "action": "manage",
        "can_be_given": False,  # Sensitive
    },
    {
        "code": "salary.view_own",
        "name": "View Own Salary",
        "description": "View own salary information",
        "resource": "salary",
        "action": "view_own",
        "can_be_given": False,
    },
    
    # ===================
    # REPORTS (Future)
    # ===================
    {
        "code": "reports.view",
        "name": "View Reports",
        "description": "View system reports",
        "resource": "reports",
        "action": "view",
        "can_be_given": True,
    },
    {
        "code": "reports.export",
        "name": "Export Reports",
        "description": "Export reports to files",
        "resource": "reports",
        "action": "export",
        "can_be_given": True,
    },
]


def get_permission_codes():
    """Return list of all permission codes."""
    return [p["code"] for p in PERMISSIONS]


def get_permissions_by_resource(resource):
    """Return all permissions for a specific resource."""
    return [p for p in PERMISSIONS if p["resource"] == resource]


def get_giveable_permissions():
    """Return all permissions that can be shared via give_own."""
    return [p for p in PERMISSIONS if p["can_be_given"]]
