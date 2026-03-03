# Silver HR System - API Documentation

Complete API reference for the Silver HR System backend.

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
  - [Authentication Endpoints](#authentication-endpoints)
  - [Employee Self-Service](#employee-self-service)
  - [Admin Employee Management](#admin-employee-management)
  - [JobTitle Management](#jobtitle-management)
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

| Role | Permissions |
|------|-------------|
| **Unauthenticated** | Login only |
| **Employee** | View own profile, change own password |
| **Admin** (`is_staff=True`) | Full CRUD on all employees, job titles |

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

All admin endpoints require `is_staff=True`.

#### List All Employees

**Endpoint:** `GET /api/v1/employees/`

**Authentication:** Admin required

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

**Authentication:** Admin required

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

**Authentication:** Admin required

**Success Response (200 OK):** Full employee object (see [Data Models](#employee-model))

**Error Response (404):**
```json
{
    "detail": "No Employee matches the given query."
}
```

#### Update Employee

**Endpoint:** `PUT /api/v1/employees/{id}/` or `PATCH /api/v1/employees/{id}/`

**Authentication:** Admin required

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

**Authentication:** Admin required

**Success Response (200 OK):**
```json
{
    "detail": "Employee deactivated successfully."
}
```

#### Activate Employee

Reactivates a previously deactivated employee.

**Endpoint:** `POST /api/v1/employees/{id}/activate/`

**Authentication:** Admin required

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

Admin can reset any employee's password without knowing the current password.

**Endpoint:** `POST /api/v1/employees/{id}/set-password/`

**Authentication:** Admin required

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

All JobTitle management endpoints require `is_staff=True`.

#### List All Job Titles

**Endpoint:** `GET /api/v1/employees/job-titles/`

**Authentication:** Admin required

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

**Authentication:** Admin required

**Success Response (200 OK):** Array of active job titles (same format as above)

#### Create Job Title

**Endpoint:** `POST /api/v1/employees/job-titles/`

**Authentication:** Admin required

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

**Authentication:** Admin required

**Success Response (200 OK):** Job title object

#### Update Job Title

**Endpoint:** `PUT /api/v1/employees/job-titles/{id}/` or `PATCH /api/v1/employees/job-titles/{id}/`

**Authentication:** Admin required

**Request Body:**
```json
{
    "description": "Updated description",
    "is_active": false
}
```

**Success Response (200 OK):** Updated job title object

---

## Data Models

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

---

## Testing

Run the test suite:

```bash
# Local
python manage.py test employees

# Docker
docker compose exec silver-backend-web-app python manage.py test employees

# With verbosity
python manage.py test employees -v 2

# Specific test module
python manage.py test employees.tests.test_authentication

# Specific test class
python manage.py test employees.tests.test_authentication.AuthenticationTests

# Specific test method
python manage.py test employees.tests.test_authentication.AuthenticationTests.test_login_with_valid_credentials
```

### Test Coverage

The test suite covers:
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
