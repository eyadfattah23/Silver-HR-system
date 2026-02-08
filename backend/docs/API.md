# Silver HR System - API Documentation

Complete API reference for the Silver HR System backend.

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
  - [Authentication Endpoints](#authentication-endpoints)
  - [Employee Self-Service](#employee-self-service)
  - [Admin Dashboard API](#admin-dashboard-api)
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
| **Admin** (`is_staff=True`) | Full CRUD on all employees |

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
    "first_name": "Ahmed",
    "rest_of_name": "Mohamed Hassan",
    "email": "ahmed@example.com",
    "is_active": true,
    "is_staff": false,
    "is_verified": true,
    "date_joined": "2024-06-01",
    "dob": "1995-03-15",
    "gender": "male",
    "identity_type": "nid",
    "identity_number": "29503151234567",
    "address": "123 Main St, Cairo",
    "location": "https://maps.google.com/...",
    "profile_picture": "https://res.cloudinary.com/...",
    "role": "Developer",
    "fingerprint_id": "FP001",
    "created_at": "2024-06-01T10:30:00Z",
    "updated_at": "2024-06-15T14:20:00Z"
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

### Admin Dashboard API

All admin endpoints require `is_staff=True`.

#### List All Employees

**Endpoint:** `GET /api/v1/employees/`

**Authentication:** Admin required

**Query Parameters:** (optional)
- Pagination is automatic

**Success Response (200 OK):**
```json
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "phone_number1": "+201000000002",
        "first_name": "Ahmed",
        "rest_of_name": "Mohamed Hassan",
        "email": "ahmed@example.com",
        "role": "Developer",
        "is_active": true,
        "is_staff": false,
        "date_joined": "2024-06-01"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "phone_number1": "+201000000003",
        "first_name": "Sara",
        "rest_of_name": "Ali Ibrahim",
        "email": null,
        "role": "Designer",
        "is_active": true,
        "is_staff": false,
        "date_joined": "2024-07-01"
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
    "first_name": "New",
    "rest_of_name": "Employee Name",
    "email": "new@example.com",
    "date_joined": "2025-01-15",
    "identity_type": "nid",
    "identity_number": "30001151234567",
    "address": "456 Street, Giza",
    "location": "https://maps.google.com/...",
    "role": "Accountant",
    "fingerprint_id": "FP002",
    "is_active": true,
    "is_staff": false,
    "is_verified": false
}
```

**Required Fields:**
- `phone_number1`
- `password`
- `re_password`
- `first_name`
- `rest_of_name`
- `date_joined`
- `identity_type`
- `identity_number`

**Success Response (201 Created):**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "phone_number1": "+201111111111",
    "phone_number2": "+201111111112",
    "first_name": "New",
    "rest_of_name": "Employee Name",
    "email": "new@example.com",
    "date_joined": "2025-01-15",
    "dob": "2000-01-15",
    "gender": "male",
    "identity_type": "nid",
    "identity_number": "30001151234567",
    "address": "456 Street, Giza",
    "location": "https://maps.google.com/...",
    "role": "Accountant",
    "is_active": true,
    "is_staff": false,
    "is_verified": false
}
```

**Validation Errors (400):**
```json
{
    "phone_number1": ["Phone number must be an Egyptian number starting with +20 country code."],
    "identity_number": ["Egyptian National ID must be exactly 14 digits."],
    "non_field_errors": ["The two password fields didn't match."]
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
    "first_name": "Updated Name",
    "role": "Senior Developer",
    "is_verified": true
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

## Data Models

### Employee Model

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID | Auto | Primary key |
| `phone_number1` | String | Yes | Primary phone (Egyptian +20), unique, used for login |
| `phone_number2` | String | No | Secondary phone number |
| `first_name` | String | Yes | First name (max 30 chars) |
| `rest_of_name` | String | Yes | Rest of name (max 150 chars) |
| `email` | Email | No | Unique if provided |
| `password` | String | Yes | Hashed password |
| `date_joined` | Date | Yes | Employment start date |
| `dob` | Date | No | Date of birth (auto-extracted from NID) |
| `gender` | String | No | "male" or "female" (auto-extracted from NID) |
| `identity_type` | String | Yes | "nid", "passport", "driving_license", "other" |
| `identity_number` | String | Yes | Government ID number, unique |
| `address` | Text | No | Full address |
| `location` | URL | No | Google Maps or similar URL |
| `profile_picture` | URL | No | Cloudinary image URL |
| `role` | String | No | Job role/title |
| `fingerprint_id` | String | No | Biometric ID |
| `is_active` | Boolean | - | Default: true |
| `is_staff` | Boolean | - | Admin access, default: false |
| `is_superuser` | Boolean | - | Full permissions, default: false |
| `is_verified` | Boolean | - | Account verified, default: false |
| `created_at` | DateTime | Auto | Record creation timestamp |
| `updated_at` | DateTime | Auto | Last update timestamp |
| `last_login` | DateTime | Auto | Last successful login |

### Identity Types

| Value | Description |
|-------|-------------|
| `nid` | Egyptian National ID (14 digits) - auto-extracts DOB and gender |
| `passport` | Passport number |
| `driving_license` | Driving license number |
| `other` | Other form of ID |

### Egyptian National ID Format

For `identity_type: "nid"`, the ID must be exactly 14 digits:
- **Digit 1:** Century (2 = 1900s, 3 = 2000s)
- **Digits 2-3:** Birth year
- **Digits 4-5:** Birth month
- **Digits 6-7:** Birth day
- **Digits 8-9:** Governorate code
- **Digits 10-13:** Serial number
- **Digit 13:** Gender (odd = male, even = female)
- **Digit 14:** Check digit

Example: `29503151234567`
- Born: March 15, 1995
- Gender: Male (7 is odd)

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
    "first_name": "Mohamed",
    "rest_of_name": "Ahmed Ali",
    "date_joined": "2025-02-01",
    "identity_type": "nid",
    "identity_number": "29503151234567",
    "role": "Developer"
  }'
```

### Admin: Update Employee (cURL)

```bash
curl -X PATCH http://localhost:8001/api/v1/employees/550e8400-e29b-41d4-a716-446655440000/ \
  -H "Content-Type: application/json" \
  -H "Authorization: JWT eyJ..." \
  -d '{
    "role": "Senior Developer",
    "is_verified": true
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

# Specific test class
python manage.py test employees.tests.AuthenticationTests

# Specific test method
python manage.py test employees.tests.AuthenticationTests.test_login_with_valid_credentials
```

### Test Coverage

The test suite covers:
- ✅ Authentication (login, token refresh, invalid credentials)
- ✅ Employee self-service (view profile, change password)
- ✅ Admin employee list & create
- ✅ Admin employee update & delete
- ✅ Admin employee activate/deactivate
- ✅ Admin password reset
- ✅ Permission enforcement
- ✅ Validation (phone numbers, NID, passwords)
- ✅ Model behavior (NID extraction, email null handling)
