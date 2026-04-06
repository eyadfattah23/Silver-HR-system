# Permissions System Documentation

This document explains how the Silver HR permissions system works and provides guidance for frontend implementation.

---

## Table of Contents

1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [Data Models](#data-models)
4. [Permission Scopes](#permission-scopes)
5. [Permission Grant Flow](#permission-grant-flow)
6. [Special Permissions](#special-permissions)
7. [API Endpoints](#api-endpoints)
8. [Frontend Implementation Guide](#frontend-implementation-guide)
9. [Security Considerations](#security-considerations)

---

## Overview

The Silver HR permission system is a Role-Based Access Control (RBAC) system with scope-based restrictions. Employees are assigned **roles**, and roles contain **permissions**. Additionally, employees can receive **extra permissions** beyond their role's default permissions.

### Key Features

- **Role-based permissions**: Employees get permissions from their assigned roles
- **Extra permissions**: Individual permissions can be granted beyond role defaults
- **Scoped access**: Permissions can be limited to specific cities, branches, or departments
- **Permission sharing**: Employees with special permission can share their role permissions with others

---

## Core Concepts

### Permissions

A permission represents an action that can be performed on a resource.

> **Note**: Permissions are **system-defined** by the backend team and cannot be created or modified by admins. Admins can only link existing permissions to roles and employees.

| Field | Description | Example |
|-------|-------------|---------|
| `code` | Unique identifier | `employees.view`, `documents.create` |
| `name` | Human-readable name | "View Employees", "Create Documents" |
| `resource` | The resource type | `employees`, `documents`, `attendance` |
| `action` | The action type | `view`, `create`, `update`, `delete`, `approve` |
| `can_be_given` | Can this permission be shared via "give_own"? | `true` / `false` |
| `is_active` | Is this permission currently active? | `true` / `false` |

### Roles

A role is a named collection of permissions. Examples:
- **Super Admin**: All permissions, global scope
- **HR Manager**: Employee management permissions
- **Department Manager**: Limited to their department
- **Employee**: Basic view-own permissions

| Field | Description |
|-------|-------------|
| `name` | Unique role name |
| `description` | Role description |
| `is_system_role` | Protected system role (cannot be deleted) |
| `is_active` | Is this role currently active? |

### Role Permissions

Links permissions to roles. Each role-permission link can be independently activated/deactivated.

### Employee Roles

Assigns a role to an employee with optional scope restrictions.

| Field | Description |
|-------|-------------|
| `employee` | The employee receiving the role |
| `role` | The role being assigned |
| `city` | (Optional) Restrict to this city |
| `branch` | (Optional) Restrict to this branch |
| `department` | (Optional) Restrict to this department |
| `is_active` | Is this assignment active? |
| `granted_by` | Who assigned this role |
| `granted_at` | When the role was assigned |
| `revoked_by` | (If revoked) Who revoked it |
| `revoked_at` | (If revoked) When it was revoked |

### Employee Extra Permissions

Grants individual permissions directly to an employee (outside of their roles).

| Field | Description |
|-------|-------------|
| `employee` | The employee receiving the permission |
| `permission` | The permission being granted |
| `city` | (Optional) Restrict to this city |
| `branch` | (Optional) Restrict to this branch |
| `department` | (Optional) Restrict to this department |
| `is_active` | Is this grant active? |
| `granted_by` | Who granted this permission |
| `granted_at` | When the permission was granted |

---

## Permission Scopes

Permissions can be scoped to limit where they apply:

| Scope Level | Description | Example |
|-------------|-------------|---------|
| **Global** | Applies everywhere | Can view all employees in the system |
| **City** | Applies to a specific city | Can view employees only in Cairo |
| **Branch** | Applies to a specific branch | Can view employees only in HQ branch |
| **Department** | Applies to a specific department | Can view employees only in IT department |

### Scope Hierarchy

Scopes follow the organizational hierarchy:
```
Global
  └── City
        └── Branch
              └── Department
```

- A **global** permission applies to all cities, branches, and departments
- A **city** permission applies to all branches and departments within that city
- A **branch** permission applies to all departments within that branch
- A **department** permission applies only to that specific department

### Scope Inheritance Example

If an employee has `employees.view` permission scoped to **Cairo** city:
- ✅ Can view employees in Cairo HQ Branch
- ✅ Can view employees in Cairo Downtown Branch
- ✅ Can view employees in any Cairo department
- ❌ Cannot view employees in Alexandria branches

---

## Permission Grant Flow

### Super Admin Granting Permissions

Super admins have the `permissions.edit_employee` permission and can:
1. Assign/revoke any role to any employee
2. Grant/revoke any extra permission to any employee
3. Set any scope for roles and extra permissions

### Employee Sharing Permissions ("Give Own")

Employees with the `permissions.give_own` permission can share their role permissions:

#### Rules for Giving Permissions

1. **Role permissions only**: Can only give permissions that come from their roles (NOT from their extra permissions)
2. **Must be `can_be_given`**: The permission must have `can_be_given = true`
3. **No duplicates**: Cannot give a permission the receiver already has
4. **Permanent**: Once given, the permission stays with the receiver (even if the giver loses it later)
5. **No revocation**: Givers cannot revoke permissions they gave; only super admin can remove extra permissions
6. **Automatic acceptance**: Receiver automatically gets the permission (no approval needed)

#### Scope Behavior When Giving

When Employee A gives a permission to Employee B:

| Scenario | Result |
|----------|--------|
| A has global scope | B gets global scope |
| A has city scope, B gets same city | B gets that city scope |
| A has city scope, chosen scope is narrower | B gets the narrower scope |
| A has branch scope, B's scope is different branch | B gets **global scope** (non-overlapping = upgrade) |

**Key Rule**: If the giver's scope and the target scope don't overlap, the receiver gets **global scope**.

#### Give Permission Flow

```
1. Employee A has role "HR Manager" with permission "employees.view" (city: Cairo)
2. Employee A has "permissions.give_own" permission
3. Employee A gives "employees.view" to Employee B

   Validation:
   ✓ "employees.view" is from A's role (not extra permission)
   ✓ "employees.view" has can_be_given = true
   ✓ Employee B doesn't already have this permission
   
4. Employee B receives extra permission "employees.view" (city: Cairo)
```

---

## Special Permissions

### `permissions.edit_employee`

- **Who can have it**: Super admins only
- **What it allows**:
  - Assign/revoke any role to any employee
  - Grant/revoke any extra permission
  - Modify permission scopes
  - Full CRUD on roles and permissions

### `permissions.give_own`

- **Who can have it**: Any employee can receive this
- **What it allows**:
  - Share permissions from their roles with other employees
  - Only permissions marked `can_be_given = true`
  - Cannot give this permission itself to others (super admin only)

---

## API Endpoints

### Permissions (Read-Only)

Permissions are **system-defined** and cannot be created, updated, or deleted via API.
They are managed by the backend team and synced to the database via migrations.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/permissions/` | List all available permissions |
| GET | `/api/permissions/{id}/` | Get permission details |

### Roles Management (Super Admin Only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/permissions/roles/` | List all roles |
| POST | `/api/permissions/roles/` | Create a new role |
| GET | `/api/permissions/roles/{id}/` | Get role details with permissions |
| PATCH | `/api/permissions/roles/{id}/` | Update a role |
| DELETE | `/api/permissions/roles/{id}/` | Delete a role (if not system role) |

### Role Permissions (Super Admin Only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/permissions/roles/{id}/permissions/` | Add permission to role |
| DELETE | `/api/permissions/roles/{id}/permissions/{permission_id}/` | Remove permission from role |

### Employee Roles (Super Admin Only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/permissions/employee-roles/` | List all employee role assignments |
| POST | `/api/permissions/employee-roles/` | Assign role to employee |
| GET | `/api/permissions/employee-roles/{id}/` | Get assignment details |
| PATCH | `/api/permissions/employee-roles/{id}/` | Update assignment (scope, status) |
| DELETE | `/api/permissions/employee-roles/{id}/` | Revoke role assignment |

### Employee Extra Permissions (Super Admin Only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/permissions/extra-permissions/` | List all extra permissions |
| POST | `/api/permissions/extra-permissions/` | Grant extra permission |
| GET | `/api/permissions/extra-permissions/{id}/` | Get grant details |
| PATCH | `/api/permissions/extra-permissions/{id}/` | Update scope/status |
| DELETE | `/api/permissions/extra-permissions/{id}/` | Revoke extra permission |

### Self-Service Endpoints (All Authenticated Users)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/permissions/my-permissions/` | Get current user's effective permissions |
| GET | `/api/permissions/my-roles/` | Get current user's roles |

### Give Permission Endpoint (Users with `give_own`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/permissions/give/` | Give a permission to another employee |

---

## Frontend Implementation Guide

### Checking User Permissions

After login, fetch the user's permissions:

```javascript
// GET /api/permissions/my-permissions/
const response = await api.get('/permissions/my-permissions/');

// Response structure
{
  "permissions": [
    {
      "code": "employees.view",
      "name": "View Employees",
      "resource": "employees",
      "action": "view",
      "source": "role",          // "role" or "extra"
      "role_name": "HR Manager", // Only if source is "role"
      "scope": {
        "level": "city",         // "global", "city", "branch", "department"
        "city": { "id": "...", "name": "Cairo" },
        "branch": null,
        "department": null
      }
    },
    // ... more permissions
  ]
}
```

### Permission Check Helper

```javascript
// Example permission checking utility
class PermissionChecker {
  constructor(permissions) {
    this.permissions = permissions;
  }

  // Check if user has a specific permission (any scope)
  hasPermission(code) {
    return this.permissions.some(p => p.code === code);
  }

  // Check if user has permission for a specific scope
  hasPermissionForScope(code, { city, branch, department }) {
    return this.permissions.some(p => {
      if (p.code !== code) return false;
      
      // Global scope applies everywhere
      if (p.scope.level === 'global') return true;
      
      // Check scope hierarchy
      if (p.scope.level === 'city' && city) {
        return p.scope.city.id === city.id;
      }
      if (p.scope.level === 'branch' && branch) {
        return p.scope.branch.id === branch.id;
      }
      if (p.scope.level === 'department' && department) {
        return p.scope.department.id === department.id;
      }
      
      return false;
    });
  }

  // Check if user can perform action on resource
  canPerform(resource, action) {
    const code = `${resource}.${action}`;
    return this.hasPermission(code);
  }
}
```

### UI Patterns

#### Showing/Hiding UI Elements

```jsx
// Only show button if user has permission
{permissions.hasPermission('employees.create') && (
  <Button onClick={handleCreateEmployee}>Add Employee</Button>
)}
```

#### Scoped Data Lists

When fetching data, the backend automatically filters results based on the user's scope. The frontend should:

1. Not send scope filters for super admins (they see everything)
2. Display scope indicators when relevant

```jsx
// Show scope badge next to data
const ScopeBadge = ({ scope }) => {
  if (scope.level === 'global') return null;
  
  return (
    <Badge variant="secondary">
      {scope.level}: {scope[scope.level]?.name}
    </Badge>
  );
};
```

#### Give Permission UI

For users with `permissions.give_own`:

```jsx
const GivePermissionForm = () => {
  // 1. Get list of permissions user can give
  //    (role permissions where can_be_given = true)
  
  // 2. Let user select recipient employee
  
  // 3. Let user select permission to give
  
  // 4. Optionally let user select scope
  //    (only scopes within user's own scope, or leave blank for same scope)
  
  // 5. Submit to POST /api/permissions/give/
};
```

### Error Handling

Common permission-related errors:

| Status | Error Code | Description |
|--------|------------|-------------|
| 401 | `not_authenticated` | User not logged in |
| 403 | `permission_denied` | User lacks required permission |
| 403 | `scope_denied` | User has permission but not for this scope |
| 400 | `already_has_permission` | Receiver already has this permission |
| 400 | `cannot_give_extra_permission` | Can only give role permissions |
| 400 | `permission_not_giveable` | Permission has `can_be_given = false` |

### Role-Based Navigation

```javascript
// Example navigation configuration
const navigationItems = [
  {
    path: '/employees',
    label: 'Employees',
    requiredPermission: 'employees.view',
  },
  {
    path: '/documents',
    label: 'Documents',
    requiredPermission: 'documents.view',
  },
  {
    path: '/admin/permissions',
    label: 'Permission Management',
    requiredPermission: 'permissions.edit_employee',
  },
];

// Filter navigation based on user permissions
const visibleNavItems = navigationItems.filter(item => 
  permissions.hasPermission(item.requiredPermission)
);
```

---

## Security Considerations

### Backend Enforcement

All permission checks are enforced on the backend. Frontend permission checks are for UX only—the API will reject unauthorized requests regardless of frontend logic.

### Token Security

- JWT tokens contain minimal claims (user ID, email, employee ID)
- Permissions are fetched via API, not stored in token
- Refresh tokens should be used for long sessions

### Sensitive Operations

The following require `permissions.edit_employee`:
- Creating/modifying roles
- Creating/modifying permissions
- Direct assignment of extra permissions
- Revoking any permission or role

### Audit Trail

All permission operations are logged:
- `granted_by` / `granted_at` on all grants
- `revoked_by` / `revoked_at` on revocations
- Consider implementing activity logging for compliance

---

## Example Scenarios

### Scenario 1: HR Manager Delegation

1. **Super Admin** creates "HR Manager" role with permissions:
   - `employees.view` (can_be_given: true)
   - `employees.create` (can_be_given: true)
   - `employees.update` (can_be_given: true)
   - `permissions.give_own` (can_be_given: false)

2. **Super Admin** assigns "HR Manager" role to Employee Ahmed with scope: Cairo

3. **Ahmed** can now share `employees.view`, `employees.create`, `employees.update` with other employees

4. **Ahmed** gives `employees.view` to Employee Sara
   - Sara receives extra permission `employees.view` scoped to Cairo
   - Sara can now view employees in Cairo branches

5. **Ahmed** cannot give `permissions.give_own` to Sara (it has can_be_given: false)

### Scenario 2: Department Manager

1. **Super Admin** assigns "Department Manager" role to Employee Ali, scoped to IT Department

2. Ali's permissions apply only to IT Department:
   - Can view/edit employees in IT Department
   - Cannot see employees in other departments

3. Ali gives `employees.view` to colleague Hassan, scoped to IT Department
   - Hassan can now view IT Department employees

### Scenario 3: Permission Scope Upgrade

1. **Ahmed** has `employees.view` scoped to Cairo
2. **Sara** has `employees.view` scoped to Alexandria
3. Ahmed gives his `employees.view` to Sara
4. Since Cairo and Alexandria don't overlap, Sara gets **global** scope
5. Sara can now view employees in all cities

---

## Summary

| User Type | Can Assign Roles | Can Give Extra Perms | Can Give Role Perms | Can Revoke |
|-----------|-----------------|---------------------|--------------------|-----------| 
| Super Admin | ✅ Any role | ✅ Any permission | ✅ (via extra perm) | ✅ Anything |
| User with `give_own` | ❌ | ❌ | ✅ From own roles | ❌ |
| Regular User | ❌ | ❌ | ❌ | ❌ |

The permission system is designed to be simple yet flexible:
- **Roles** define standard permission bundles
- **Extra permissions** allow individual grants
- **Scopes** limit where permissions apply
- **Give own** allows controlled delegation without complexity
