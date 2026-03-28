# Silver HR System – Backend

Backend system for **Silver HR System**, built with **Django 5**, **Django REST Framework**, **JWT authentication (Djoser)**, **PostgreSQL**, **Docker**, and **Channels**.

This project supports both **local development** and **Docker deployment**. Migrations must be created locally and committed to git.


## Table of Contents

- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure-high-level)
- [Quick Start (Local Development)](#-quick-start-local-development)
- [Running with Docker](#-running-with-docker)
- [API Documentation](#-api-documentation)
- [Testing](#-testing)
- [Migration Workflow](#-migration-workflow)


## Tech Stack
- Python 3.14
- Django 5.2
- Django REST Framework
- Djoser (JWT Authentication)
- PostgreSQL 17
- Docker & Docker Compose
- Channels + Redis
- Timezone: `Africa/Cairo`
- Primary Language: Arabic (`ar`)

---

## 🚀 Quick Start (Local Development)

### 1. Setup Virtual Environment

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or: .venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Environment Setup

```bash
# For local development (connecting to local PostgreSQL):
cp .env.local .env
# DATABASE_HOST should be 'localhost' for local dev

# For Docker development:
# Keep DATABASE_HOST=db in .env
```

### 3. Run Commands Locally

```bash
# Always use the venv python:
.venv/bin/python manage.py <command>

# Or activate first:
source .venv/bin/activate
python manage.py <command>
```

### 4. Start Development Server

```bash
# Make sure PostgreSQL is running (locally or via Docker)
python manage.py migrate
python manage.py runserver
```

---

## 🐳 Running with Docker

### Start All Services

```bash
docker compose up --build
```

This will:
* Start PostgreSQL
* Apply migrations automatically
* Collect static files
* Run Django development server on `http://localhost:8000`

### Docker Commands

```bash
# Start in background:
docker compose up -d

# View logs:
docker compose logs -f silver-backend-web-app

# Run Django commands in container:
docker compose exec silver-backend-web-app python manage.py <command>

# Reset everything (WARNING: deletes data):
docker compose down -v
docker compose up --build
```

### Docker vs Local Development

| Task | Local | Docker |
|------|-------|--------|
| `makemigrations` | ✅ **Yes (required)** | ❌ Never |
| `migrate` | ✅ Yes | ✅ Auto (entrypoint) |
| `runserver` | ✅ Yes | ✅ Auto (entrypoint) |
| `createsuperuser` | ✅ Yes | ✅ `docker compose exec silver-backend-web-app python manage.py createsuperuser` |
| `test` | ✅ Yes | ✅ Yes |

---

## 📚 API Documentation

For complete API reference, see **[docs/API.md](docs/API.md)**.

### Quick Reference

#### Authentication
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/jwt/create/` | POST | Login (get JWT tokens) |
| `/api/v1/auth/jwt/refresh/` | POST | Refresh access token |
| `/api/v1/auth/users/set_password/` | POST | Change own password |

#### Employee Self-Service
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/employees/me/` | GET | View own profile (read-only) |

#### Admin Employee Management (is_staff=True)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/employees/` | GET | List all employees |
| `/api/v1/employees/` | POST | Create new employee |
| `/api/v1/employees/{id}/` | GET | Get employee details |
| `/api/v1/employees/{id}/` | PATCH | Update employee |
| `/api/v1/employees/{id}/` | DELETE | Deactivate employee |
| `/api/v1/employees/{id}/activate/` | POST | Reactivate employee |
| `/api/v1/employees/{id}/set-password/` | POST | Reset employee password |
| `/api/v1/employees/job-titles/` | GET/POST | List/Create job titles |
| `/api/v1/employees/job-titles/{id}/` | GET/PATCH/DELETE | Job title details |

#### Core Management (is_superuser=True)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/core/cities/` | GET/POST | List/Create cities |
| `/api/v1/core/cities/active/` | GET | List active cities only |
| `/api/v1/core/cities/{id}/` | GET/PATCH/DELETE | City details |
| `/api/v1/core/branches/` | GET/POST | List/Create branches |
| `/api/v1/core/branches/active/` | GET | List active branches only |
| `/api/v1/core/branches/{id}/` | GET/PATCH/DELETE | Branch details |
| `/api/v1/core/departments/` | GET/POST | List/Create departments |
| `/api/v1/core/departments/active/` | GET | List active departments only |
| `/api/v1/core/departments/{id}/` | GET/PATCH/DELETE | Department details |

### Permission Summary

| User Type | Flag | Can Do |
|-----------|------|--------|
| **Employee** | - | View own profile, change own password |
| **Admin** | `is_staff=True` | Full CRUD on employees, job titles |
| **Superuser** | `is_superuser=True` | All admin permissions + City/Branch/Department management |

---

## 🧪 Testing

### Run All Tests

```bash
# Local - All tests
python manage.py test

# Docker - All tests
docker compose exec silver-backend-web-app python manage.py test

# Specific app
python manage.py test employees
python manage.py test core

# With verbosity
python manage.py test -v 2
```

### Run Specific Tests

```bash
# Run a specific test class
python manage.py test employees.tests.AuthenticationTests

# Run a specific test method
python manage.py test employees.tests.AuthenticationTests.test_login_with_valid_credentials
```

### Test Categories

#### Employee Tests (57 tests)
| Category | Description |
|----------|-------------|
| `AuthenticationTests` | JWT login, token refresh, invalid credentials |
| `EmployeeMeViewTests` | Self-service profile viewing |
| `EmployeePasswordChangeTests` | Password change functionality |
| `AdminEmployeeListTests` | Admin listing employees |
| `AdminEmployeeCreateTests` | Admin creating employees + validation |
| `AdminEmployeeDetailTests` | Admin viewing employee details |
| `AdminEmployeeUpdateTests` | Admin updating employees |
| `AdminEmployeeDeleteTests` | Soft delete (deactivation) |
| `AdminEmployeeActivateTests` | Reactivating employees |
| `AdminSetPasswordTests` | Admin password reset |
| `EmployeeModelTests` | Model validations, NID extraction |
| `JobTitleTests` | Job title CRUD operations |

#### Core Tests (56 tests)
| Category | Description |
|----------|-------------|
| `CityListTests` | City listing (superuser only) |
| `CityCreateTests` | City creation + validation |
| `CityDetailTests` | City update/delete operations |
| `CityModelTests` | City model behavior |
| `BranchListTests` | Branch listing (superuser only) |
| `BranchCreateTests` | Branch creation + validation |
| `BranchDetailTests` | Branch update/delete operations |
| `BranchModelTests` | Branch model behavior |
| `DepartmentListTests` | Department listing (superuser only) |
| `DepartmentCreateTests` | Department creation + validation |
| `DepartmentDetailTests` | Department update/delete operations |
| `DepartmentModelTests` | Department model behavior |

---

## Project Structure (High Level)

## 📦 Migration Workflow

### ⚠️ IMPORTANT RULES

1. **NEVER run `makemigrations` inside Docker** — only locally
2. **ALWAYS commit migration files to git** — they are source code
3. **Run `makemigrations` BEFORE pushing** your branch

### Creating Migrations

```bash
cd backend
source .venv/bin/activate

# Check what migrations would be created:
python manage.py makemigrations --dry-run

# Create migrations:
python manage.py makemigrations

# Review the generated files, then commit:
git add */migrations/*.py
git commit -m "Add migration for <description>"
```

### Applying Migrations

```bash
# Locally:
python manage.py migrate

# In Docker (automatic via entrypoint):
docker-compose up
```

### Handling Merge Conflicts in Migrations

When merging branches with conflicting migrations:

```bash
# Option 1: Auto-merge (if Django can resolve it)
python manage.py makemigrations --merge

# Option 2: Nuclear reset (development only!)
# WARNING: This deletes ALL data!
python scripts/delete_migrations.py --dry-run  # preview
python scripts/delete_migrations.py --yes      # delete
python manage.py makemigrations
python manage.py migrate --fake-initial  # or drop DB and migrate fresh
```


### Checking Migration Status

```bash
# Show all migrations and their status:
python manage.py showmigrations

# Show SQL that would be run:
python manage.py sqlmigrate <app_name> <migration_number>
```
