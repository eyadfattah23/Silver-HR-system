# Silver HR System - API Documentation

Complete API reference for the Silver HR System backend.

> **For Frontend Developers:** Jump to [Quick Reference](#quick-reference) for a complete endpoint table.

---

## Quick Reference

### All Endpoints at a Glance

> **Note:** Users with `is_superuser=True` bypass all permission checks and have full access to all endpoints.

#### 🔐 Authentication (No auth required)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/jwt/create/` | Login (get tokens) |
| POST | `/api/v1/auth/jwt/refresh/` | Refresh access token |

#### 👤 Employee Self-Service (Any authenticated user)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/employees/me/` | Get own profile |
| POST | `/api/v1/auth/users/set_password/` | Change own password |

#### 👔 Employee Management (`employees.view`, `employees.create`, `employees.update`, `employees.delete`)
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/api/v1/employees/` | List all employees | `employees.view` |
| POST | `/api/v1/employees/` | Create employee | `employees.create` |
| GET | `/api/v1/employees/{id}/` | Get employee | `employees.view` |
| PATCH | `/api/v1/employees/{id}/` | Update employee | `employees.update` |
| DELETE | `/api/v1/employees/{id}/` | Deactivate employee | `employees.delete` |
| POST | `/api/v1/employees/{id}/activate/` | Reactivate employee | `employees.update` |
| POST | `/api/v1/employees/{id}/set-password/` | Reset employee password | `employees.update` |

#### 👔 Job Titles (`employees.view`, `employees.update`)
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/api/v1/employees/job-titles/` | List all job titles | `employees.view` |
| GET | `/api/v1/employees/job-titles/active/` | List active job titles | Authenticated |
| POST | `/api/v1/employees/job-titles/` | Create job title | `employees.update` |
| GET | `/api/v1/employees/job-titles/{id}/` | Get job title | `employees.view` |
| PATCH | `/api/v1/employees/job-titles/{id}/` | Update job title | `employees.update` |
| DELETE | `/api/v1/employees/job-titles/{id}/` | Deactivate job title | `employees.update` |

#### 🏢 Core - Cities (`core.view`, `core.manage`)
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/api/v1/core/cities/` | List all cities | `core.view` |
| GET | `/api/v1/core/cities/active/` | List active cities | `core.view` |
| POST | `/api/v1/core/cities/` | Create city | `core.manage` |
| GET | `/api/v1/core/cities/{id}/` | Get city | `core.view` |
| PATCH | `/api/v1/core/cities/{id}/` | Update city | `core.manage` |
| DELETE | `/api/v1/core/cities/{id}/` | Deactivate city | `core.manage` |

#### 🏢 Core - Branches (`core.view`, `core.manage`)
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/api/v1/core/branches/` | List all branches | `core.view` |
| GET | `/api/v1/core/branches/active/` | List active branches | `core.view` |
| POST | `/api/v1/core/branches/` | Create branch | `core.manage` |
| GET | `/api/v1/core/branches/{id}/` | Get branch | `core.view` |
| PATCH | `/api/v1/core/branches/{id}/` | Update branch | `core.manage` |
| DELETE | `/api/v1/core/branches/{id}/` | Deactivate branch | `core.manage` |

#### 🏢 Core - Departments (`core.view`, `core.manage`)
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/api/v1/core/departments/` | List all departments | `core.view` |
| GET | `/api/v1/core/departments/active/` | List active departments | `core.view` |
| POST | `/api/v1/core/departments/` | Create department | `core.manage` |
| GET | `/api/v1/core/departments/{id}/` | Get department | `core.view` |
| PATCH | `/api/v1/core/departments/{id}/` | Update department | `core.manage` |
| DELETE | `/api/v1/core/departments/{id}/` | Deactivate department | `core.manage` |

#### 📄 Document Types (`document_types.view`, `document_types.manage`)
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/api/v1/documents/types/` | List all document types | `document_types.view` |
| GET | `/api/v1/documents/types/active/` | List active document types | `document_types.view` |
| POST | `/api/v1/documents/types/` | Create document type | `document_types.manage` |
| GET | `/api/v1/documents/types/{id}/` | Get document type | `document_types.view` |
| PATCH | `/api/v1/documents/types/{id}/` | Update document type | `document_types.manage` |
| DELETE | `/api/v1/documents/types/{id}/` | Deactivate document type | `document_types.manage` |

#### 📄 Documents (`documents.view`, `documents.create`, `documents.update`, `documents.delete`)
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/api/v1/documents/` | List all documents | `documents.view` |
| GET | `/api/v1/documents/active/` | List active documents | `documents.view` |
| POST | `/api/v1/documents/` | Create document | `documents.create` |
| GET | `/api/v1/documents/{uuid}/` | Get document | `documents.view` |
| PATCH | `/api/v1/documents/{uuid}/` | Update document | `documents.update` |
| DELETE | `/api/v1/documents/{uuid}/` | Deactivate document | `documents.delete` |
| GET | `/api/v1/documents/employee/{uuid}/` | List employee's documents | `documents.view` |

#### 📄 Employee - My Documents (Any authenticated user)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/documents/my/` | List own documents |
| GET | `/api/v1/documents/my/{uuid}/` | Get own document detail |

#### 🔑 Permissions Self-Service (Any authenticated user)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/permissions/my-permissions/` | Get own permissions |
| GET | `/api/v1/permissions/my-roles/` | Get own roles |
| GET | `/api/v1/permissions/giveable/` | Get permissions you can give |
| POST | `/api/v1/permissions/give/` | Give permission to another user |

#### 🔑 Permissions - Permissions List (`permissions.view`)
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/api/v1/permissions/` | List all permissions | `permissions.view` |
| GET | `/api/v1/permissions/{id}/` | Get permission details | `permissions.view` |

#### 🔑 Permissions - Roles (`permissions.view_roles`, `permissions.manage_roles`)
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/api/v1/permissions/roles/` | List all roles | `permissions.view_roles` |
| POST | `/api/v1/permissions/roles/` | Create role | `permissions.manage_roles` |
| GET | `/api/v1/permissions/roles/{id}/` | Get role details | `permissions.view_roles` |
| PATCH | `/api/v1/permissions/roles/{id}/` | Update role | `permissions.manage_roles` |
| DELETE | `/api/v1/permissions/roles/{id}/` | Delete/deactivate role | `permissions.manage_roles` |
| POST | `/api/v1/permissions/roles/{id}/permissions/` | Add permission to role | `permissions.manage_roles` |
| DELETE | `/api/v1/permissions/roles/{id}/permissions/{perm_id}/` | Remove permission from role | `permissions.manage_roles` |

#### 🔑 Permissions - Employee Roles (`permissions.assign_roles`)
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/api/v1/permissions/employee-roles/` | List role assignments | `permissions.assign_roles` |
| POST | `/api/v1/permissions/employee-roles/` | Assign role to employee | `permissions.assign_roles` |
| GET | `/api/v1/permissions/employee-roles/{id}/` | Get assignment details | `permissions.assign_roles` |
| PATCH | `/api/v1/permissions/employee-roles/{id}/` | Update assignment | `permissions.assign_roles` |
| DELETE | `/api/v1/permissions/employee-roles/{id}/` | Revoke role | `permissions.assign_roles` |

#### 🔑 Permissions - Extra Permissions (`permissions.edit_employee`)
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/api/v1/permissions/extra-permissions/` | List extra permissions | `permissions.edit_employee` |
| POST | `/api/v1/permissions/extra-permissions/` | Grant extra permission | `permissions.edit_employee` |
| GET | `/api/v1/permissions/extra-permissions/{id}/` | Get extra permission details | `permissions.edit_employee` |
| PATCH | `/api/v1/permissions/extra-permissions/{id}/` | Update extra permission | `permissions.edit_employee` |
| DELETE | `/api/v1/permissions/extra-permissions/{id}/` | Revoke extra permission | `permissions.edit_employee` |

---

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
  - [Authentication Endpoints](#authentication-endpoints)
  - [Employee Self-Service](#employee-self-service)
  - [Admin Employee Management](#admin-employee-management)
  - [JobTitle Management](#jobtitle-management)
  - [Core Management](#core-management)
    - [City Management](#city-management)
    - [Branch Management](#branch-management)
    - [Department Management](#department-management)
  - [Documents Management](#documents-management)
    - [Document Type Management](#document-type-management)
    - [Document Management](#document-management)
    - [My Documents (Employee Self-Service)](#my-documents-employee-self-service)
  - [Permissions Management](#permissions-management)
    - [Permissions Self-Service](#permissions-self-service)
    - [Permissions List](#permissions-list)
    - [Role Management](#role-management)
    - [Employee Role Assignment](#employee-role-assignment)
    - [Extra Permission Management](#extra-permission-management)
- [Data Models](#data-models)
- [Error Handling](#error-handling)
- [Examples](#examples)

---

## Overview

### Base URL
```
http://localhost:8001/api/v1/
```

### Content Type
All requests should use `Content-Type: application/json`

### Authentication
The API uses **JWT (JSON Web Token)** authentication. Include the token in the `Authorization` header:
```
Authorization: JWT <access_token>
```

### Permission Levels

The system uses **Role-Based Access Control (RBAC)** with scoped permissions. Users with `is_superuser=True` bypass all permission checks.

| Level | Description |
|-------|-------------|
| **Unauthenticated** | Login only |
| **Authenticated** | View own profile, change own password, view own documents |
| **Permission-based** | Access based on assigned permissions (via roles or extra permissions) |
| **Superuser** (`is_superuser=True`) | Full access to all endpoints, bypasses all permission checks |

#### Common Permissions

| Permission Code | Description |
|-----------------|-------------|
| `employees.view` | View employees |
| `employees.create` | Create employees |
| `employees.update` | Update employees |
| `employees.delete` | Delete/deactivate employees |
| `core.view` | View cities, branches, departments |
| `core.manage` | Create/update/delete cities, branches, departments |
| `documents.view` | View documents |
| `documents.create` | Create documents |
| `documents.update` | Update documents |
| `documents.delete` | Delete documents |
| `document_types.view` | View document types |
| `document_types.manage` | Manage document types |
| `permissions.view_roles` | View roles |
| `permissions.manage_roles` | Create/update/delete roles |
| `permissions.assign_roles` | Assign/revoke roles to employees |
| `permissions.edit_employee` | Grant/revoke extra permissions |
| `permissions.give_own` | Give own role permissions to others |
### Organizational Hierarchy

```
City (Cairo, Alexandria, ...)
  └── Branch (Main Branch, Downtown Branch, ...)
        └── Department (HR, IT, Sales, ...)
              └── Employee
```

- **City**: Geographic location (e.g., Cairo, Alexandria)
- **Branch**: Physical office within a city
- **Department**: Organizational unit within a branch (HR, IT, etc.)
- **Employee**: Staff member assigned to a department

---

## Authentication

### Login (Obtain JWT Tokens)

**Endpoint:** `POST /api/v1/auth/jwt/create/`

**Request Body:**
```json
{
    "phone_number1": "+201000000001",
    "password": "YourPassword123!"
}
```

**Success Response (200 OK):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Error Response (401 Unauthorized):**
```json
{
    "detail": "No active account found with the given credentials"
}
```

### Refresh Token

**Endpoint:** `POST /api/v1/auth/jwt/refresh/`

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Success Response (200 OK):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Token Lifetime

| Token Type | Lifetime |
|------------|----------|
| Access Token | 99 days |
| Refresh Token | 7 days |

### Frontend Integration Notes

1. **Store tokens securely** - Use `httpOnly` cookies or secure storage
2. **Include token in all requests** - Add `Authorization: JWT <access_token>` header
3. **Handle 401 errors** - Redirect to login or attempt token refresh
4. **Check permissions** - Use `/api/v1/permissions/my-permissions/` to get the user's effective permissions

```javascript
// Example: Axios interceptor for auth
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `JWT ${token}`;
  }
  return config;
});
```

---

## API Endpoints

### Employee Self-Service

#### Get Own Profile

Retrieve the current authenticated employee's profile.

**Endpoint:** `GET /api/v1/employees/me/`

**Authentication:** Required (any authenticated user)

**Success Response (200 OK):**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "phone_number1": "+201000000002",
    "phone_number2": null,
    "fingerprint_id": null,
    "national_id": "29506151234528",
    "first_name": "فاطمة",
    "second_name": "أحمد",
    "third_name": "محمود",
    "fourth_name": "سعيد",
    "full_name": "فاطمة أحمد محمود سعيد",
    "date_of_birth": "1995-06-15",
    "gender": "female",
    "address": null,
    "marital_status": "single",
    "military_status": "not_applicable",
    "department": null,
    "job_title": "550e8400-e29b-41d4-a716-446655440001",
    "job_title_detail": {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "Software Engineer"
    },
    "employment_type": "full_time",
    "employment_state": "active",
    "hire_date": "2024-06-01",
    "current_salary": "10000.00",
    "is_attendance_exempt": false,
    "notes": null,
    "is_active": true,
    "is_staff": false,
    "created_at": "2024-06-01T10:30:00Z",
    "updated_at": "2024-06-15T14:20:00Z",
    "created_by": null,
    "updated_by": null
}
```

#### Change Own Password

Change the current authenticated employee's password.

**Endpoint:** `POST /api/v1/auth/users/set_password/`

**Authentication:** Required (any authenticated user)

**Request Body:**
```json
{
    "current_password": "OldPassword123!",
    "new_password": "NewSecurePass456!",
    "re_new_password": "NewSecurePass456!"
}
```

**Success Response (204 No Content):** Empty response

**Error Responses:**

- Wrong current password (400):
```json
{
    "current_password": ["Invalid password."]
}
```

- Passwords don't match (400):
```json
{
    "non_field_errors": ["The two password fields didn't match."]
}
```

---

### Admin Employee Management

Employee management endpoints require `employees.*` permissions. Superusers have full access.

#### List All Employees

**Endpoint:** `GET /api/v1/employees/`

**Authentication:** Required (`employees.view` permission or superuser)

**Success Response (200 OK):**
```json
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "phone_number1": "+201000000002",
        "first_name": "فاطمة",
        "fourth_name": "سعيد",
        "full_name": "فاطمة أحمد محمود سعيد",
        "job_title_name": "Software Engineer",
        "employment_state": "active",
        "is_active": true,
        "is_staff": false,
        "hire_date": "2024-06-01"
    }
]
```

#### Create New Employee

**Endpoint:** `POST /api/v1/employees/`

**Authentication:** Required (`employees.create` permission or superuser)

**Request Body:**
```json
{
    "phone_number1": "+201111111111",
    "phone_number2": "+201111111112",
    "password": "SecurePass123!",
    "re_password": "SecurePass123!",
    "first_name": "أحمد",
    "second_name": "محمد",
    "third_name": "علي",
    "fourth_name": "حسن",
    "date_of_birth": "1995-01-15",
    "gender": "male",
    "military_status": "completed",
    "hire_date": "2025-01-15",
    "national_id": "29501151234517",
    "fingerprint_id": "FPCaITM001",
    "address": "123 Main St, Cairo",
    "marital_status": "single",
    "employment_type": "full_time",
    "employment_state": "active",
    "current_salary": "15000.00",
    "is_attendance_exempt": false,
    "notes": "New employee notes",
    "job_title": "550e8400-e29b-41d4-a716-446655440001",
    "department": "550e8400-e29b-41d4-a716-446655440002"
}
```

**Required Fields:**
- `phone_number1` (Egyptian +20 format)
- `password`
- `re_password`
- `first_name`
- `second_name`
- `third_name`
- `fourth_name`
- `date_of_birth`
- `gender`
- `military_status` (required for males, auto-set to `not_applicable` for females)
- `hire_date`

**Success Response (201 Created):** Full employee object

**Validation Errors (400):**
```json
{
    "phone_number1": ["Phone number must be an Egyptian number starting with +20 country code."],
    "national_id": ["Egyptian National ID must be exactly 14 digits."],
    "re_password": ["Passwords do not match."]
}
```

#### Get Employee Details

**Endpoint:** `GET /api/v1/employees/{id}/`

**Authentication:** Required (`employees.view` permission or superuser)

**Success Response (200 OK):** Full employee object (see [Data Models](#employee-model))

**Error Response (404):**
```json
{
    "detail": "No Employee matches the given query."
}
```

#### Update Employee

**Endpoint:** `PUT /api/v1/employees/{id}/` or `PATCH /api/v1/employees/{id}/`

**Authentication:** Required (`employees.update` permission or superuser)

**Request Body (PATCH - partial update):**
```json
{
    "first_name": "تحديث",
    "current_salary": "20000.00",
    "employment_state": "on_leave"
}
```

**Success Response (200 OK):** Updated employee object

#### Deactivate Employee (Soft Delete)

Deactivates an employee instead of deleting. Deactivated employees cannot log in.

**Endpoint:** `DELETE /api/v1/employees/{id}/`

**Authentication:** Required (`employees.delete` permission or superuser)

**Success Response (200 OK):**
```json
{
    "detail": "Employee deactivated successfully."
}
```

#### Activate Employee

Reactivates a previously deactivated employee.

**Endpoint:** `POST /api/v1/employees/{id}/activate/`

**Authentication:** Required (`employees.update` permission or superuser)

**Success Response (200 OK):**
```json
{
    "detail": "Employee activated successfully."
}
```

**Error Response (404):**
```json
{
    "detail": "Employee not found."
}
```

#### Reset Employee Password (Admin)

Admins can reset any employee's password without knowing the current password.

**Endpoint:** `POST /api/v1/employees/{id}/set-password/`

**Authentication:** Required (`employees.update` permission or superuser)

**Request Body:**
```json
{
    "new_password": "NewPassword123!",
    "re_new_password": "NewPassword123!"
}
```

**Success Response (200 OK):**
```json
{
    "detail": "Password updated successfully."
}
```

**Error Responses:**

- Missing password (400):
```json
{
    "new_password": ["This field is required."]
}
```

- Passwords don't match (400):
```json
{
    "re_new_password": ["Passwords do not match."]
}
```

---

### JobTitle Management

JobTitle management requires `employees.view` for read and `employees.update` for write operations. Superusers have full access.

#### List All Job Titles

**Endpoint:** `GET /api/v1/employees/job-titles/`

**Authentication:** Required (`employees.view` permission or superuser)

**Success Response (200 OK):**
```json
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "Software Engineer",
        "description": "Develops software applications",
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
]
```

#### List Active Job Titles Only

**Endpoint:** `GET /api/v1/employees/job-titles/active/`

**Authentication:** Required (any authenticated user)

**Success Response (200 OK):** Array of active job titles (same format as above)

#### Create Job Title

**Endpoint:** `POST /api/v1/employees/job-titles/`

**Authentication:** Required (`employees.update` permission or superuser)

**Request Body:**
```json
{
    "name": "Senior Developer",
    "description": "Senior software developer with 5+ years experience",
    "is_active": true
}
```

**Success Response (201 Created):** Created job title object

#### Get Job Title Details

**Endpoint:** `GET /api/v1/employees/job-titles/{id}/`

**Authentication:** Required (`employees.view` permission or superuser)

**Success Response (200 OK):** Job title object

#### Update Job Title

**Endpoint:** `PUT /api/v1/employees/job-titles/{id}/` or `PATCH /api/v1/employees/job-titles/{id}/`

**Authentication:** Required (`employees.update` permission or superuser)

**Request Body:**
```json
{
    "description": "Updated description",
    "is_active": false
}
```

**Success Response (200 OK):** Updated job title object

---

### Core Management

Core management endpoints (City, Branch, Department) require `core.view` for read and `core.manage` for write operations. Superusers have full access.
These endpoints manage the organizational hierarchy: **City → Branch → Department → Employee**

#### City Management

##### List All Cities

**Endpoint:** `GET /api/v1/core/cities/`

**Authentication:** Required (`core.view` permission or superuser)

**Success Response (200 OK):**
```json
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "Cairo",
        "code": "CAI",
        "description": "Capital city of Egypt",
        "branch_count": 3,
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
]
```

##### List Active Cities Only

**Endpoint:** `GET /api/v1/core/cities/active/`

**Authentication:** Required (`core.view` permission or superuser)

**Success Response (200 OK):** Array of active cities (same format as above)

##### Create City

**Endpoint:** `POST /api/v1/core/cities/`

**Authentication:** Required (`core.manage` permission or superuser)

**Request Body:**
```json
{
    "name": "Alexandria",
    "code": "ALX",
    "description": "Second largest city in Egypt"
}
```

**Success Response (201 Created):** Created city object

**Validation:**
- `name` and `code` must be unique
- `code` is auto-uppercased

##### Get City Details

**Endpoint:** `GET /api/v1/core/cities/{id}/`

**Authentication:** Required (`core.view` permission or superuser)

**Success Response (200 OK):** City object with branch count

##### Update City

**Endpoint:** `PUT /api/v1/core/cities/{id}/` or `PATCH /api/v1/core/cities/{id}/`

**Authentication:** Required (`core.manage` permission or superuser)

**Request Body:**
```json
{
    "description": "Updated description",
    "is_active": false
}
```

**Success Response (200 OK):** Updated city object

##### Delete (Soft Delete) City

**Endpoint:** `DELETE /api/v1/core/cities/{id}/`

**Authentication:** Required (`core.manage` permission or superuser)

**Success Response (200 OK):**
```json
{
    "message": "City deactivated successfully"
}
```

**Note:** Cities are soft-deleted (is_active=false), not permanently removed.

---

#### Branch Management

##### List All Branches

**Endpoint:** `GET /api/v1/core/branches/`

**Authentication:** Required (`core.view` permission or superuser)

**Success Response (200 OK):**
```json
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440002",
        "name": "Main Branch",
        "description": "Headquarters",
        "city": "550e8400-e29b-41d4-a716-446655440001",
        "city_name": "Cairo",
        "location": "https://maps.google.com/...",
        "department_count": 5,
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
]
```

##### List Active Branches Only

**Endpoint:** `GET /api/v1/core/branches/active/`

**Authentication:** Required (`core.view` permission or superuser)

**Success Response (200 OK):** Array of active branches

##### Create Branch

**Endpoint:** `POST /api/v1/core/branches/`

**Authentication:** Required (`core.manage` permission or superuser)

**Request Body:**
```json
{
    "name": "Downtown Branch",
    "description": "Branch in downtown area",
    "city": "550e8400-e29b-41d4-a716-446655440001",
    "location": "https://maps.google.com/..."
}
```

**Success Response (201 Created):** Created branch object

**Validation:**
- Branch name must be unique within the same city
- Cannot create branch in an inactive city

##### Get Branch Details

**Endpoint:** `GET /api/v1/core/branches/{id}/`

**Authentication:** Required (`core.view` permission or superuser)

**Success Response (200 OK):** Branch object with city details and department count

##### Update Branch

**Endpoint:** `PUT /api/v1/core/branches/{id}/` or `PATCH /api/v1/core/branches/{id}/`

**Authentication:** Required (`core.manage` permission or superuser)

**Success Response (200 OK):** Updated branch object

##### Delete (Soft Delete) Branch

**Endpoint:** `DELETE /api/v1/core/branches/{id}/`

**Authentication:** Required (`core.manage` permission or superuser)

**Success Response (200 OK):**
```json
{
    "message": "Branch deactivated successfully"
}
```

---

#### Department Management

##### List All Departments

**Endpoint:** `GET /api/v1/core/departments/`

**Authentication:** Required (`core.view` permission or superuser)

**Success Response (200 OK):**
```json
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440003",
        "name": "Human Resources",
        "code": "HR",
        "description": "HR Department",
        "branch": "550e8400-e29b-41d4-a716-446655440002",
        "branch_name": "Main Branch",
        "city_name": "Cairo",
        "employee_count": 12,
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
]
```

##### List Active Departments Only

**Endpoint:** `GET /api/v1/core/departments/active/`

**Authentication:** Required (`core.view` permission or superuser)

**Success Response (200 OK):** Array of active departments

##### Create Department

**Endpoint:** `POST /api/v1/core/departments/`

**Authentication:** Required (`core.manage` permission or superuser)

**Request Body:**
```json
{
    "name": "Information Technology",
    "code": "IT",
    "description": "IT Department",
    "branch": "550e8400-e29b-41d4-a716-446655440002"
}
```

**Success Response (201 Created):** Created department object

**Validation:**
- Department `code` must be unique
- `code` is auto-uppercased
- Cannot create department in an inactive branch

##### Get Department Details

**Endpoint:** `GET /api/v1/core/departments/{id}/`

**Authentication:** Required (`core.view` permission or superuser)

**Success Response (200 OK):** Department object with branch/city details and employee count

##### Update Department

**Endpoint:** `PUT /api/v1/core/departments/{id}/` or `PATCH /api/v1/core/departments/{id}/`

**Authentication:** Required (`core.manage` permission or superuser)

**Success Response (200 OK):** Updated department object

##### Delete (Soft Delete) Department

**Endpoint:** `DELETE /api/v1/core/departments/{id}/`

**Authentication:** Required (`core.manage` permission or superuser)

**Success Response (200 OK):**
```json
{
    "message": "Department deactivated successfully"
}
```

---

### Documents Management

Manage employee documents such as ID cards, passports, contracts, etc.

#### Document Type Management

Document Type management requires `document_types.view` for read and `document_types.manage` for write operations. Superusers have full access.

##### List All Document Types

**Endpoint:** `GET /api/v1/documents/types/`

**Authentication:** Required (`document_types.view` permission or superuser)

**Success Response (200 OK):**
```json
[
    {
        "id": 1,
        "name": "ID Card",
        "description": "National ID Card",
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
]
```

##### List Active Document Types Only

**Endpoint:** `GET /api/v1/documents/types/active/`

**Authentication:** Required (`document_types.view` permission or superuser)

**Success Response (200 OK):** Array of active document types

##### Create Document Type

**Endpoint:** `POST /api/v1/documents/types/`

**Authentication:** Required (`document_types.manage` permission or superuser)

**Request Body:**
```json
{
    "name": "Passport",
    "description": "International Passport",
    "is_active": true
}
```

**Success Response (201 Created):** Created document type object

**Validation:**
- Document type `name` must be unique (case-insensitive)

##### Get Document Type Details

**Endpoint:** `GET /api/v1/documents/types/{id}/`

**Authentication:** Required (`document_types.view` permission or superuser)

**Success Response (200 OK):**
```json
{
    "id": 1,
    "name": "ID Card",
    "description": "National ID Card",
    "document_count": 15,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

##### Update Document Type

**Endpoint:** `PUT /api/v1/documents/types/{id}/` or `PATCH /api/v1/documents/types/{id}/`

**Authentication:** Required (`document_types.manage` permission or superuser)

**Success Response (200 OK):** Updated document type object

##### Delete (Soft Delete) Document Type

**Endpoint:** `DELETE /api/v1/documents/types/{id}/`

**Authentication:** Required (`document_types.manage` permission or superuser)

**Success Response (200 OK):**
```json
{
    "detail": "Document type deactivated successfully."
}
```

---

#### Document Management

Document management requires `documents.*` permissions. Superusers have full access.

##### List All Documents

**Endpoint:** `GET /api/v1/documents/`

**Authentication:** Required (`documents.view` permission or superuser)

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `employee` | UUID | Filter by employee ID |
| `document_type` | Integer | Filter by document type ID |
| `is_active` | Boolean | Filter by active status |

**Success Response (200 OK):**
```json
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "employee": "550e8400-e29b-41d4-a716-446655440000",
        "employee_name": "أحمد محمد علي حسن",
        "document_type": 1,
        "document_type_name": "ID Card",
        "file_name": "employee_id.pdf",
        "file_format": "pdf",
        "expiration_date": "2027-01-01",
        "is_expired": false,
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z"
    }
]
```

##### List Active Documents Only

**Endpoint:** `GET /api/v1/documents/active/`

**Authentication:** Required (`documents.view` permission or superuser)

**Query Parameters:** Same as List All Documents

**Success Response (200 OK):** Array of active documents

##### List Employee's Documents

**Endpoint:** `GET /api/v1/documents/employee/{employee_id}/`

**Authentication:** Required (`documents.view` permission or superuser)

**Success Response (200 OK):** Array of documents for the specified employee

##### Create Document

**Endpoint:** `POST /api/v1/documents/`

**Authentication:** Required (`documents.create` permission or superuser)

**Request Body:**
```json
{
    "employee": "550e8400-e29b-41d4-a716-446655440000",
    "document_type": 1,
    "file_name": "employee_passport.pdf",
    "file_format": "pdf",
    "file_size": 2048,
    "description": "Employee passport copy",
    "expiration_date": "2028-06-15",
    "notes": "Renewal reminder set"
}
```

**Success Response (201 Created):** Created document object

**Validation:**
- Cannot use an inactive document type
- `file_format` is auto-lowercased
- `uploaded_by` is automatically set to the current user

##### Get Document Details

**Endpoint:** `GET /api/v1/documents/{uuid}/`

**Authentication:** Required (`documents.view` permission or superuser)

**Success Response (200 OK):**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "employee": "550e8400-e29b-41d4-a716-446655440000",
    "employee_name": "أحمد محمد علي حسن",
    "document_type": 1,
    "document_type_detail": {
        "id": 1,
        "name": "ID Card"
    },
    "file_name": "employee_id.pdf",
    "file_format": "pdf",
    "file_size": 1024,
    "file_path": "/media/documents/employee_id.pdf",
    "description": "National ID Card",
    "expiration_date": "2027-01-01",
    "is_expired": false,
    "notes": null,
    "is_active": true,
    "uploaded_by": "550e8400-e29b-41d4-a716-446655440099",
    "uploaded_by_name": "سوبر أدمن المدير العام",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

##### Update Document

**Endpoint:** `PUT /api/v1/documents/{uuid}/` or `PATCH /api/v1/documents/{uuid}/`

**Authentication:** Required (`documents.update` permission or superuser)

**Request Body:**
```json
{
    "description": "Updated description",
    "expiration_date": "2028-01-01",
    "is_active": true
}
```

**Success Response (200 OK):** Updated document object

##### Delete (Soft Delete) Document

**Endpoint:** `DELETE /api/v1/documents/{uuid}/`

**Authentication:** Required (`documents.delete` permission or superuser)

**Success Response (200 OK):**
```json
{
    "detail": "Document deactivated successfully."
}
```

---

#### My Documents (Employee Self-Service)

Endpoints for employees to view their own documents. Requires authentication.

##### List My Documents

**Endpoint:** `GET /api/v1/documents/my/`

**Authentication:** Required (any authenticated user)

**Success Response (200 OK):**
```json
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "document_type": 1,
        "document_type_name": "ID Card",
        "file_name": "my_id.pdf",
        "file_format": "pdf",
        "file_size": 1024,
        "file_path": "/media/documents/my_id.pdf",
        "description": "My National ID Card",
        "expiration_date": "2027-01-01",
        "is_expired": false,
        "created_at": "2024-01-01T00:00:00Z"
    }
]
```

**Notes:**
- Only returns the authenticated employee's own documents
- Only returns active documents
- Ordered by creation date (newest first)

##### Get My Document Detail

**Endpoint:** `GET /api/v1/documents/my/{uuid}/`

**Authentication:** Required (any authenticated user)

**Success Response (200 OK):** Document object (same format as list)

**Error Response (404 Not Found):**
- If document doesn't exist
- If document belongs to another employee
- If document is inactive

---

### Permissions Management

The permissions system provides Role-Based Access Control (RBAC) with scope support. For detailed documentation on the permissions system, see [PERMISSIONS.md](./PERMISSIONS.md).

#### Permissions Self-Service

Endpoints for employees to view their own permissions and share permissions with others.

##### Get My Permissions

**Endpoint:** `GET /api/v1/permissions/my-permissions/`

**Authentication:** Required (any authenticated user)

**Success Response (200 OK):**
```json
{
    "permissions": [
        {
            "code": "employees.view",
            "name": "View Employees",
            "resource": "employees",
            "action": "view",
            "source": "role",
            "role_name": "HR Manager",
            "scope": {
                "level": "city",
                "city": {"id": "...", "name": "Cairo"}
            }
        }
    ],
    "by_resource": {
        "employees": [...]
    },
    "is_superuser": false,
    "total_count": 5
}
```

##### Get My Roles

**Endpoint:** `GET /api/v1/permissions/my-roles/`

**Authentication:** Required (any authenticated user)

**Success Response (200 OK):**
```json
{
    "roles": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "role_name": "HR Manager",
            "scope": {
                "level": "city",
                "city": {"id": "...", "name": "Cairo"}
            },
            "granted_at": "2024-01-01T00:00:00Z"
        }
    ],
    "total_count": 1
}
```

##### Get Giveable Permissions

Get permissions that the current user can share with others. Requires `permissions.give_own` permission.

**Endpoint:** `GET /api/v1/permissions/giveable/`

**Authentication:** Required (`permissions.give_own` permission)

**Success Response (200 OK):**
```json
{
    "permissions": [
        {
            "id": "...",
            "code": "employees.view",
            "name": "View Employees",
            "can_be_given": true
        }
    ],
    "can_give": true,
    "total_count": 3
}
```

**Error Response (403 Forbidden):** If user doesn't have `permissions.give_own` permission.

##### Give Permission

Share a permission from your role with another employee.

**Endpoint:** `POST /api/v1/permissions/give/`

**Authentication:** Required (`permissions.give_own` permission)

**Request Body:**
```json
{
    "employee_id": "550e8400-e29b-41d4-a716-446655440000",
    "permission_id": "550e8400-e29b-41d4-a716-446655440001",
    "city_id": "550e8400-e29b-41d4-a716-446655440002"
}
```

**Success Response (201 Created):** Extra permission object

**Error Responses:**
- `400`: Permission not in user's roles, permission not giveable, or recipient already has permission
- `403`: User doesn't have `permissions.give_own` permission

---

#### Permissions List

List and view available permissions. Permissions are system-defined and cannot be created via API.

##### List All Permissions

**Endpoint:** `GET /api/v1/permissions/`

**Authentication:** Required (`permissions.view` permission or superuser)

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `resource` | String | Filter by resource (e.g., `employees`) |
| `action` | String | Filter by action (e.g., `view`) |
| `can_be_given` | Boolean | Filter by giveable status |

**Success Response (200 OK):**
```json
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "code": "employees.view",
        "name": "View Employees",
        "resource": "employees",
        "action": "view",
        "can_be_given": true
    }
]
```

##### Get Permission Details

**Endpoint:** `GET /api/v1/permissions/{id}/`

**Authentication:** Required (`permissions.view` permission or superuser)

**Success Response (200 OK):**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "code": "employees.view",
    "name": "View Employees",
    "description": "Allows viewing employee records",
    "resource": "employees",
    "action": "view",
    "can_be_given": true
}
```

---

#### Role Management

Manage roles which group permissions together.

##### List All Roles

**Endpoint:** `GET /api/v1/permissions/roles/`

**Authentication:** Required (`permissions.view_roles` permission or superuser)

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `is_active` | Boolean | Filter by active status |
| `is_system_role` | Boolean | Filter system roles |

**Success Response (200 OK):**
```json
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "HR Manager",
        "description": "Human Resources Manager",
        "is_system_role": false,
        "is_active": true,
        "permission_count": 5
    }
]
```

##### Create Role

**Endpoint:** `POST /api/v1/permissions/roles/`

**Authentication:** Required (`permissions.manage_roles` permission or superuser)

**Request Body:**
```json
{
    "name": "Sales Manager",
    "description": "Sales department manager role",
    "permissions": [
        {"permission_id": "550e8400-e29b-41d4-a716-446655440001"},
        {"permission_id": "550e8400-e29b-41d4-a716-446655440002"}
    ]
}
```

**Success Response (201 Created):** Role object with permissions

##### Get Role Details

**Endpoint:** `GET /api/v1/permissions/roles/{id}/`

**Authentication:** Required (`permissions.view_roles` permission or superuser)

**Success Response (200 OK):**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "name": "HR Manager",
    "description": "Human Resources Manager",
    "is_system_role": false,
    "is_active": true,
    "permissions": [
        {
            "id": "...",
            "code": "employees.view",
            "name": "View Employees"
        }
    ]
}
```

##### Update Role

**Endpoint:** `PUT /api/v1/permissions/roles/{id}/` or `PATCH /api/v1/permissions/roles/{id}/`

**Authentication:** Required (`permissions.manage_roles` permission or superuser)

**Success Response (200 OK):** Updated role object

##### Delete Role

**Endpoint:** `DELETE /api/v1/permissions/roles/{id}/`

**Authentication:** Required (`permissions.manage_roles` permission or superuser)

**Success Response (200 OK):**
```json
{
    "message": "Role deactivated successfully"
}
```

**Error Response (400):** Cannot delete role with active employee assignments

##### Add Permission to Role

**Endpoint:** `POST /api/v1/permissions/roles/{id}/permissions/`

**Authentication:** Required (`permissions.manage_roles` permission or superuser)

**Request Body:**
```json
{
    "permission_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

**Success Response (201 Created):** Role object with updated permissions

##### Remove Permission from Role

**Endpoint:** `DELETE /api/v1/permissions/roles/{id}/permissions/{permission_id}/`

**Authentication:** Required (`permissions.manage_roles` permission or superuser)

**Success Response (200 OK):** Role object with updated permissions

---

#### Employee Role Assignment

Assign and manage roles for employees.

##### List Employee Roles

**Endpoint:** `GET /api/v1/permissions/employee-roles/`

**Authentication:** Required (`permissions.assign_roles` permission or superuser)

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `employee` | UUID | Filter by employee |
| `role` | UUID | Filter by role |
| `is_active` | Boolean | Filter by active status |

**Success Response (200 OK):**
```json
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "employee_id": "...",
        "employee_name": "أحمد محمد علي حسن",
        "employee_email": "ahmed@example.com",
        "role_id": "...",
        "role_name": "HR Manager",
        "city_name": "Cairo",
        "branch_name": null,
        "department_name": null,
        "scope_level": "city",
        "is_active": true,
        "granted_at": "2024-01-01T00:00:00Z"
    }
]
```

##### Assign Role to Employee

**Endpoint:** `POST /api/v1/permissions/employee-roles/`

**Authentication:** Required (`permissions.assign_roles` permission or superuser)

**Request Body:**
```json
{
    "employee_id": "550e8400-e29b-41d4-a716-446655440000",
    "role_id": "550e8400-e29b-41d4-a716-446655440001",
    "city_id": "550e8400-e29b-41d4-a716-446655440002",
    "branch_id": null,
    "department_id": null
}
```

**Success Response (201 Created):** Employee role assignment object

##### Get Employee Role Details

**Endpoint:** `GET /api/v1/permissions/employee-roles/{id}/`

**Authentication:** Required (`permissions.assign_roles` permission or superuser)

**Success Response (200 OK):** Full employee role object

##### Update Employee Role

**Endpoint:** `PATCH /api/v1/permissions/employee-roles/{id}/`

**Authentication:** Required (`permissions.assign_roles` permission or superuser)

**Request Body:**
```json
{
    "city_id": "550e8400-e29b-41d4-a716-446655440003",
    "is_active": true
}
```

**Success Response (200 OK):** Updated employee role object

##### Revoke Employee Role

**Endpoint:** `DELETE /api/v1/permissions/employee-roles/{id}/`

**Authentication:** Required (`permissions.assign_roles` permission or superuser)

**Success Response (200 OK):**
```json
{
    "message": "Role assignment revoked successfully"
}
```

---

#### Extra Permission Management

Grant individual permissions to employees outside of their roles.

##### List Extra Permissions

**Endpoint:** `GET /api/v1/permissions/extra-permissions/`

**Authentication:** Required (`permissions.edit_employee` permission or superuser)

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `employee` | UUID | Filter by employee |
| `permission_code` | String | Filter by permission code |

**Success Response (200 OK):**
```json
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "employee_id": "...",
        "employee_email": "ahmed@example.com",
        "permission_id": "...",
        "permission_code": "employees.view",
        "city_name": "Cairo",
        "scope_level": "city",
        "is_active": true,
        "granted_at": "2024-01-01T00:00:00Z"
    }
]
```

##### Grant Extra Permission

**Endpoint:** `POST /api/v1/permissions/extra-permissions/`

**Authentication:** Required (`permissions.edit_employee` permission or superuser)

**Request Body:**
```json
{
    "employee_id": "550e8400-e29b-41d4-a716-446655440000",
    "permission_id": "550e8400-e29b-41d4-a716-446655440001",
    "city_id": "550e8400-e29b-41d4-a716-446655440002"
}
```

**Success Response (201 Created):** Extra permission object

##### Get Extra Permission Details

**Endpoint:** `GET /api/v1/permissions/extra-permissions/{id}/`

**Authentication:** Required (`permissions.edit_employee` permission or superuser)

**Success Response (200 OK):** Full extra permission object

##### Update Extra Permission

**Endpoint:** `PATCH /api/v1/permissions/extra-permissions/{id}/`

**Authentication:** Required (`permissions.edit_employee` permission or superuser)

**Request Body:**
```json
{
    "city_id": "550e8400-e29b-41d4-a716-446655440003",
    "is_active": true
}
```

**Success Response (200 OK):** Updated extra permission object

##### Revoke Extra Permission

**Endpoint:** `DELETE /api/v1/permissions/extra-permissions/{id}/`

**Authentication:** Required (`permissions.edit_employee` permission or superuser)

**Success Response (200 OK):**
```json
{
    "message": "Extra permission revoked successfully"
}
```

---

## Data Models

### City Model

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID | Auto | Primary key |
| `name` | String | Yes | City name (max 100 chars), unique |
| `code` | String | Yes | City code (max 10 chars), unique, auto-uppercased |
| `description` | Text | No | City description |
| `is_active` | Boolean | No | Active status (default: true) |
| `created_at` | DateTime | Auto | Record creation timestamp |
| `updated_at` | DateTime | Auto | Last update timestamp |

### Branch Model

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID | Auto | Primary key |
| `name` | String | Yes | Branch name (max 100 chars) |
| `description` | Text | No | Branch description |
| `city` | UUID | Yes | Foreign key to City |
| `location` | URL | No | Google Maps or location URL |
| `is_active` | Boolean | No | Active status (default: true) |
| `created_at` | DateTime | Auto | Record creation timestamp |
| `updated_at` | DateTime | Auto | Last update timestamp |

**Note:** Branch name must be unique within the same city.

### Department Model

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID | Auto | Primary key |
| `name` | String | Yes | Department name (max 100 chars) |
| `code` | String | Yes | Department code (max 10 chars), unique, auto-uppercased |
| `description` | Text | No | Department description |
| `branch` | UUID | Yes | Foreign key to Branch |
| `is_active` | Boolean | No | Active status (default: true) |
| `created_at` | DateTime | Auto | Record creation timestamp |
| `updated_at` | DateTime | Auto | Last update timestamp |

### Employee Model

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID | Auto | Primary key |
| `phone_number1` | String | Yes | Primary phone (Egyptian +20), unique, used for login |
| `phone_number2` | String | No | Secondary phone number |
| `fingerprint_id` | String | No | Biometric ID, unique. Format: FP{CityCode}{DeptCode}{Gender}{DeviceID} |
| `national_id` | String | No | Egyptian National ID (14 digits), unique |
| `first_name` | String | Yes | First name in Arabic (max 50 chars) |
| `second_name` | String | Yes | Father name in Arabic (max 50 chars) |
| `third_name` | String | Yes | Grandfather name in Arabic (max 50 chars) |
| `fourth_name` | String | Yes | Family name in Arabic (max 50 chars) |
| `full_name` | String | Read-only | Computed: all four name parts combined |
| `date_of_birth` | Date | Yes | Date of birth (auto-extracted from NID if provided) |
| `gender` | String | Yes | "male" or "female" (auto-extracted from NID if provided) |
| `address` | Text | No | Residential address |
| `marital_status` | String | No | "single" (default) or "married" |
| `military_status` | String | Yes* | See Military Status values below. *Auto-set for females |
| `department` | UUID | No | Reference to Department (core app) |
| `job_title` | UUID | No | Reference to JobTitle |
| `employment_type` | String | No | "full_time" (default), "part_time", "contractor", "intern" |
| `employment_state` | String | No | "active" (default), "suspended", "terminated", "on_leave" |
| `hire_date` | Date | Yes | Employment start date |
| `current_salary` | Decimal | No | Current salary (default: 0) |
| `is_attendance_exempt` | Boolean | No | If true, attendance policies do not apply |
| `notes` | Text | No | Additional notes |
| `is_active` | Boolean | Auto | Default: true |
| `is_staff` | Boolean | Auto | Admin access, default: false |
| `is_superuser` | Boolean | Auto | Full permissions, default: false |
| `created_at` | DateTime | Auto | Record creation timestamp |
| `updated_at` | DateTime | Auto | Last update timestamp |
| `created_by` | UUID | Auto | Employee who created this record |
| `updated_by` | UUID | Auto | Employee who last updated this record |
| `last_login` | DateTime | Auto | Last successful login |

### Gender Values

| Value | Description |
|-------|-------------|
| `male` | Male |
| `female` | Female |

### Military Status Values

| Value | Description |
|-------|-------------|
| `temporary_exemption` | Temporary Exemption |
| `permanent_exemption` | Permanent Exemption |
| `evasion` | Evasion |
| `postponed` | Postponed |
| `completed` | Completed |
| `not_applicable` | Not Applicable (auto-set for females) |
| `other` | Other |

### Marital Status Values

| Value | Description |
|-------|-------------|
| `single` | Single (default) |
| `married` | Married |

### Employment Type Values

| Value | Description |
|-------|-------------|
| `full_time` | Full Time (default) |
| `part_time` | Part Time |
| `contractor` | Contractor |
| `intern` | Intern |

### Employment State Values

| Value | Description |
|-------|-------------|
| `active` | Active (default) |
| `suspended` | Suspended |
| `terminated` | Terminated |
| `on_leave` | On Leave |

### JobTitle Model

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID | Auto | Primary key |
| `name` | String | Yes | Job title name (max 100 chars), unique |
| `description` | Text | No | Job description |
| `is_active` | Boolean | No | Active status (default: true) |
| `created_at` | DateTime | Auto | Record creation timestamp |
| `updated_at` | DateTime | Auto | Last update timestamp |

### DocumentType Model

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | Integer | Auto | Primary key |
| `name` | String | Yes | Document type name (max 100 chars), unique |
| `description` | Text | No | Document type description |
| `is_active` | Boolean | No | Active status (default: true) |
| `created_at` | DateTime | Auto | Record creation timestamp |
| `updated_at` | DateTime | Auto | Last update timestamp |

### Document Model

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID | Auto | Primary key |
| `employee` | UUID | Yes | Foreign key to Employee |
| `document_type` | Integer | Yes | Foreign key to DocumentType |
| `file_name` | String | Yes | Original file name (max 255 chars) |
| `file_format` | String | Yes | File extension (max 20 chars), auto-lowercased |
| `file_size` | Integer | Yes | File size in bytes |
| `file_path` | File | No | Uploaded file (stored in 'documents/') |
| `description` | Text | No | Document description |
| `expiration_date` | Date | No | Document expiration date |
| `notes` | Text | No | Additional notes |
| `is_active` | Boolean | No | Active status (default: true) |
| `uploaded_by` | UUID | Auto | Employee who uploaded the document |
| `created_at` | DateTime | Auto | Record creation timestamp |
| `updated_at` | DateTime | Auto | Last update timestamp |

### Permission Model

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID | Auto | Primary key |
| `code` | String | Yes | Unique permission code (e.g., `employees.view`) |
| `name` | String | Yes | Human-readable name |
| `description` | Text | No | Permission description |
| `resource` | String | Yes | The resource being protected |
| `action` | String | Yes | The action (view, create, update, delete) |
| `can_be_given` | Boolean | No | Can be delegated via give_own (default: true) |

### Role Model

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID | Auto | Primary key |
| `name` | String | Yes | Role name, unique |
| `description` | Text | No | Role description |
| `is_system_role` | Boolean | No | Protected system role (default: false) |
| `is_active` | Boolean | No | Active status (default: true) |

### EmployeeRole Model

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID | Auto | Primary key |
| `employee` | UUID | Yes | Foreign key to Employee |
| `role` | UUID | Yes | Foreign key to Role |
| `city` | UUID | No | Scope to specific city |
| `branch` | UUID | No | Scope to specific branch |
| `department` | UUID | No | Scope to specific department |
| `is_active` | Boolean | No | Active status (default: true) |
| `granted_by` | UUID | Auto | Who assigned this role |
| `granted_at` | DateTime | Auto | When assigned |
| `revoked_by` | UUID | Auto | Who revoked (if revoked) |
| `revoked_at` | DateTime | Auto | When revoked (if revoked) |

### EmployeeExtraPermission Model

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID | Auto | Primary key |
| `employee` | UUID | Yes | Foreign key to Employee |
| `permission` | UUID | Yes | Foreign key to Permission |
| `city` | UUID | No | Scope to specific city |
| `branch` | UUID | No | Scope to specific branch |
| `department` | UUID | No | Scope to specific department |
| `is_active` | Boolean | No | Active status (default: true) |
| `granted_by` | UUID | Auto | Who granted this permission |
| `granted_at` | DateTime | Auto | When granted |

### Scope Levels

Permissions can be scoped to limit where they apply:

| Level | Description |
|-------|-------------|
| **Global** | No scope restrictions (city, branch, department all null) |
| **City** | Applies to all branches/departments in the city |
| **Branch** | Applies to all departments in the branch |
| **Department** | Applies only to the specific department |

### Egyptian National ID Format

Egyptian National ID must be exactly 14 digits:
- **Digit 1:** Century (2 = 1900s, 3 = 2000s)
- **Digits 2-3:** Birth year
- **Digits 4-5:** Birth month
- **Digits 6-7:** Birth day
- **Digits 8-9:** Governorate code
- **Digits 10-13:** Serial number
- **Digit 13:** Gender (odd = male, even = female)
- **Digit 14:** Check digit

**Example:** `29503151234567`
- Born: March 15, 1995
- Gender: Male (7 is odd)

When a valid National ID is provided, the system automatically extracts:
- Date of birth
- Gender

### Egyptian Phone Number Format

Egyptian phone numbers must:
- Start with `+20` country code
- Use valid mobile prefixes: 10, 11, 12, or 15
- Be exactly 13 characters total (e.g., `+201012345678`)

---

## Error Handling

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 204 | No Content (success with no body) |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (missing/invalid token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 405 | Method Not Allowed |
| 500 | Internal Server Error |

### Common Error Responses

**401 Unauthorized:**
```json
{
    "detail": "Authentication credentials were not provided."
}
```

**403 Forbidden:**
```json
{
    "detail": "You do not have permission to perform this action."
}
```

**404 Not Found:**
```json
{
    "detail": "Not found."
}
```

**400 Validation Error:**
```json
{
    "field_name": ["Error message for this field."],
    "non_field_errors": ["Error not related to a specific field."]
}
```

---

## Examples

### Complete Login Flow (cURL)

```bash
# 1. Login and get tokens
curl -X POST http://localhost:8001/api/v1/auth/jwt/create/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number1": "+201000000001", "password": "AdminPass123!"}'

# Response: {"access": "eyJ...", "refresh": "eyJ..."}

# 2. Use access token for authenticated requests
curl -X GET http://localhost:8001/api/v1/employees/me/ \
  -H "Authorization: JWT eyJ..."

# 3. Refresh token when access token expires
curl -X POST http://localhost:8001/api/v1/auth/jwt/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "eyJ..."}'
```

### Admin: Create Employee (cURL)

```bash
curl -X POST http://localhost:8001/api/v1/employees/ \
  -H "Content-Type: application/json" \
  -H "Authorization: JWT eyJ..." \
  -d '{
    "phone_number1": "+201111111111",
    "password": "SecurePass123!",
    "re_password": "SecurePass123!",
    "first_name": "أحمد",
    "second_name": "محمد",
    "third_name": "علي",
    "fourth_name": "حسن",
    "date_of_birth": "1995-01-15",
    "gender": "male",
    "military_status": "completed",
    "hire_date": "2025-02-01"
  }'
```

### Admin: Create Female Employee (cURL)

Military status is auto-set to `not_applicable` for females:

```bash
curl -X POST http://localhost:8001/api/v1/employees/ \
  -H "Content-Type: application/json" \
  -H "Authorization: JWT eyJ..." \
  -d '{
    "phone_number1": "+201122222222",
    "password": "SecurePass123!",
    "re_password": "SecurePass123!",
    "first_name": "فاطمة",
    "second_name": "أحمد",
    "third_name": "محمود",
    "fourth_name": "سعيد",
    "date_of_birth": "1998-03-15",
    "gender": "female",
    "hire_date": "2025-03-01"
  }'
```

### Admin: Update Employee (cURL)

```bash
curl -X PATCH http://localhost:8001/api/v1/employees/550e8400-e29b-41d4-a716-446655440000/ \
  -H "Content-Type: application/json" \
  -H "Authorization: JWT eyJ..." \
  -d '{
    "current_salary": "20000.00",
    "employment_state": "on_leave"
  }'
```

### Admin: Create Job Title (cURL)

```bash
curl -X POST http://localhost:8001/api/v1/employees/job-titles/ \
  -H "Content-Type: application/json" \
  -H "Authorization: JWT eyJ..." \
  -d '{
    "name": "مهندس برمجيات أول",
    "description": "مطور برمجيات بخبرة 5 سنوات أو أكثر",
    "is_active": true
  }'
```

### Employee: Change Password (cURL)

```bash
curl -X POST http://localhost:8001/api/v1/auth/users/set_password/ \
  -H "Content-Type: application/json" \
  -H "Authorization: JWT eyJ..." \
  -d '{
    "current_password": "OldPassword123!",
    "new_password": "NewSecurePass456!",
    "re_new_password": "NewSecurePass456!"
  }'
```

### Superuser: Create City (cURL)

```bash
curl -X POST http://localhost:8001/api/v1/core/cities/ \
  -H "Content-Type: application/json" \
  -H "Authorization: JWT eyJ..." \
  -d '{
    "name": "الإسكندرية",
    "code": "ALX",
    "description": "محافظة الإسكندرية"
  }'
```

### Superuser: Create Branch (cURL)

```bash
curl -X POST http://localhost:8001/api/v1/core/branches/ \
  -H "Content-Type: application/json" \
  -H "Authorization: JWT eyJ..." \
  -d '{
    "name": "الفرع الرئيسي",
    "city": "550e8400-e29b-41d4-a716-446655440001",
    "description": "المقر الرئيسي",
    "location": "https://maps.google.com/..."
  }'
```

### Superuser: Create Department (cURL)

```bash
curl -X POST http://localhost:8001/api/v1/core/departments/ \
  -H "Content-Type: application/json" \
  -H "Authorization: JWT eyJ..." \
  -d '{
    "name": "الموارد البشرية",
    "code": "HR",
    "branch": "550e8400-e29b-41d4-a716-446655440002",
    "description": "قسم الموارد البشرية"
  }'
```

---

## Testing

Run the test suite:

```bash
# All tests (local)
python manage.py test

# All tests (Docker)
docker compose exec silver-backend-web-app python manage.py test

# Specific app
python manage.py test employees
python manage.py test core

# With verbosity
python manage.py test -v 2

# Specific test module
python manage.py test employees.tests.test_authentication
python manage.py test core.tests.test_city

# Specific test class
python manage.py test employees.tests.test_authentication.AuthenticationTests

# Specific test method
python manage.py test employees.tests.test_authentication.AuthenticationTests.test_login_with_valid_credentials
```

### Test Coverage

**Employee Tests (57 tests):**
- ✅ Authentication (login, token refresh, invalid credentials)
- ✅ Employee self-service (view profile, change password)
- ✅ Admin employee list & create
- ✅ Admin employee update & delete
- ✅ Admin employee activate/deactivate
- ✅ Admin password reset
- ✅ JobTitle CRUD operations
- ✅ Permission enforcement
- ✅ Validation (phone numbers, NID, passwords)
- ✅ Model behavior (NID extraction, military status auto-set)

**Core Tests (56 tests):**
- ✅ City CRUD operations (superuser only)
- ✅ Branch CRUD operations (superuser only)
- ✅ Department CRUD operations (superuser only)
- ✅ Permission enforcement (admin/employee denied)
- ✅ Validation (inactive parent entities, duplicates)
- ✅ Model behavior (soft delete, auto-uppercase codes)
