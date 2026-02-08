#!/usr/bin/env python3
"""
Comprehensive tests for the Employee API.

Test Categories:
1. Authentication Tests (JWT)
2. Employee Self-Service Tests
3. Admin Employee Management Tests
4. Validation Tests
5. Permission Tests
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from datetime import date
import uuid

Employee = get_user_model()


class BaseTestCase(APITestCase):
    """Base test case with common setup for all tests."""

    def setUp(self):
        """Create test users - an admin and a regular employee."""
        # Admin user
        self.admin = Employee.objects.create_user(
            phone_number1='+201000000001',
            password='AdminPass123!',
            first_name='Admin',
            rest_of_name='User',
            date_joined=date(2024, 1, 1),
            identity_type='nid',
            identity_number='29001011234567',
            is_staff=True,
            is_superuser=True,
        )

        # Regular employee
        self.employee = Employee.objects.create_user(
            phone_number1='+201000000002',
            password='EmployeePass123!',
            first_name='Regular',
            rest_of_name='Employee',
            date_joined=date(2024, 6, 1),
            identity_type='nid',
            identity_number='29506151234567',
            is_staff=False,
        )

        # Another employee for testing
        self.employee2 = Employee.objects.create_user(
            phone_number1='+201000000003',
            password='Employee2Pass123!',
            first_name='Another',
            rest_of_name='Employee',
            date_joined=date(2024, 7, 1),
            identity_type='passport',
            identity_number='A12345678',
            is_staff=False,
        )

        self.client = APIClient()

    def get_tokens(self, phone_number, password):
        """Helper to get JWT tokens for a user."""
        response = self.client.post('/api/v1/auth/jwt/create/', {
            'phone_number1': phone_number,
            'password': password,
        })
        return response.data

    def authenticate_as_admin(self):
        """Authenticate client as admin user."""
        tokens = self.get_tokens('+201000000001', 'AdminPass123!')
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {tokens["access"]}')

    def authenticate_as_employee(self):
        """Authenticate client as regular employee."""
        tokens = self.get_tokens('+201000000002', 'EmployeePass123!')
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {tokens["access"]}')


# =============================================================================
# Authentication Tests
# =============================================================================

class AuthenticationTests(BaseTestCase):
    """Tests for JWT authentication endpoints."""

    def test_login_with_valid_credentials(self):
        """Test successful login returns JWT tokens."""
        response = self.client.post('/api/v1/auth/jwt/create/', {
            'phone_number1': '+201000000001',
            'password': 'AdminPass123!',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_with_invalid_password(self):
        """Test login with wrong password fails."""
        response = self.client.post('/api/v1/auth/jwt/create/', {
            'phone_number1': '+201000000001',
            'password': 'WrongPassword!',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_with_nonexistent_user(self):
        """Test login with non-existent phone number fails."""
        response = self.client.post('/api/v1/auth/jwt/create/', {
            'phone_number1': '+201999999999',
            'password': 'SomePassword!',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_with_inactive_user(self):
        """Test login with deactivated user fails."""
        self.employee.is_active = False
        self.employee.save()

        response = self.client.post('/api/v1/auth/jwt/create/', {
            'phone_number1': '+201000000002',
            'password': 'EmployeePass123!',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        """Test refreshing access token with valid refresh token."""
        tokens = self.get_tokens('+201000000001', 'AdminPass123!')

        response = self.client.post('/api/v1/auth/jwt/refresh/', {
            'refresh': tokens['refresh'],
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_token_refresh_with_invalid_token(self):
        """Test refreshing with invalid token fails."""
        response = self.client.post('/api/v1/auth/jwt/refresh/', {
            'refresh': 'invalid-token',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# =============================================================================
# Employee Self-Service Tests
# =============================================================================

class EmployeeMeViewTests(BaseTestCase):
    """Tests for the /employees/me/ endpoint."""

    def test_get_own_profile_authenticated(self):
        """Test authenticated employee can view their own profile."""
        self.authenticate_as_employee()

        response = self.client.get('/api/v1/employees/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone_number1'], '+201000000002')
        self.assertEqual(response.data['first_name'], 'Regular')

    def test_get_own_profile_unauthenticated(self):
        """Test unauthenticated request is rejected."""
        response = self.client.get('/api/v1/employees/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_update_own_profile(self):
        """Test employee cannot update their own profile via /me/ endpoint."""
        self.authenticate_as_employee()

        # PUT should not be allowed (RetrieveAPIView only)
        response = self.client.put('/api/v1/employees/me/', {
            'first_name': 'Hacked',
        })
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

        # PATCH should not be allowed
        response = self.client.patch('/api/v1/employees/me/', {
            'first_name': 'Hacked',
        })
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)


class EmployeePasswordChangeTests(BaseTestCase):
    """Tests for employee password change via Djoser."""

    def test_employee_can_change_own_password(self):
        """Test employee can change their own password."""
        self.authenticate_as_employee()

        response = self.client.post('/api/v1/auth/users/set_password/', {
            'current_password': 'EmployeePass123!',
            'new_password': 'NewSecurePass456!',
            're_new_password': 'NewSecurePass456!',
        })
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify can login with new password
        self.client.credentials()  # Clear auth
        tokens = self.get_tokens('+201000000002', 'NewSecurePass456!')
        self.assertIn('access', tokens)

    def test_password_change_wrong_current_password(self):
        """Test password change fails with wrong current password."""
        self.authenticate_as_employee()

        response = self.client.post('/api/v1/auth/users/set_password/', {
            'current_password': 'WrongPassword!',
            'new_password': 'NewSecurePass456!',
            're_new_password': 'NewSecurePass456!',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_change_mismatched_passwords(self):
        """Test password change fails when new passwords don't match."""
        self.authenticate_as_employee()

        response = self.client.post('/api/v1/auth/users/set_password/', {
            'current_password': 'EmployeePass123!',
            'new_password': 'NewSecurePass456!',
            're_new_password': 'DifferentPass789!',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# =============================================================================
# Admin Employee List & Create Tests
# =============================================================================

class AdminEmployeeListTests(BaseTestCase):
    """Tests for admin listing employees."""

    def test_admin_can_list_employees(self):
        """Test admin can list all employees."""
        self.authenticate_as_admin()

        response = self.client.get('/api/v1/employees/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # admin + 2 employees

    def test_employee_cannot_list_employees(self):
        """Test regular employee cannot list employees."""
        self.authenticate_as_employee()

        response = self.client.get('/api/v1/employees/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_list_employees(self):
        """Test unauthenticated request cannot list employees."""
        response = self.client.get('/api/v1/employees/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AdminEmployeeCreateTests(BaseTestCase):
    """Tests for admin creating employees."""

    def test_admin_can_create_employee(self):
        """Test admin can create a new employee."""
        self.authenticate_as_admin()

        response = self.client.post('/api/v1/employees/', {
            'phone_number1': '+201111111111',
            'password': 'NewEmployee123!',
            're_password': 'NewEmployee123!',
            'first_name': 'New',
            'rest_of_name': 'Employee',
            'date_joined': '2025-01-15',
            'identity_type': 'nid',
            'identity_number': '30001151234567',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['first_name'], 'New')

        # Verify employee exists
        self.assertTrue(Employee.objects.filter(
            phone_number1='+201111111111').exists())

    def test_admin_can_create_employee_with_all_fields(self):
        """Test admin can create employee with all optional fields."""
        self.authenticate_as_admin()

        response = self.client.post('/api/v1/employees/', {
            'phone_number1': '+201222222222',
            'phone_number2': '+201222222223',
            'password': 'NewEmployee123!',
            're_password': 'NewEmployee123!',
            'first_name': 'Full',
            'rest_of_name': 'Employee Data',
            'email': 'full@example.com',
            'date_joined': '2025-02-01',
            'identity_type': 'nid',
            'identity_number': '30002011234567',
            'address': '123 Main St, Cairo',
            'location': 'https://maps.google.com/123',
            'role': 'employee',
            'is_staff': False,
            'is_verified': True,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], 'full@example.com')
        self.assertEqual(response.data['role'], 'employee')

    def test_employee_cannot_create_employee(self):
        """Test regular employee cannot create employees."""
        self.authenticate_as_employee()

        response = self.client.post('/api/v1/employees/', {
            'phone_number1': '+201333333333',
            'password': 'NewEmployee123!',
            're_password': 'NewEmployee123!',
            'first_name': 'Unauthorized',
            'rest_of_name': 'Creation',
            'date_joined': '2025-01-15',
            'identity_type': 'passport',
            'identity_number': 'B12345678',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_employee_duplicate_phone(self):
        """Test cannot create employee with duplicate phone number."""
        self.authenticate_as_admin()

        response = self.client.post('/api/v1/employees/', {
            'phone_number1': '+201000000002',  # Already exists
            'password': 'NewEmployee123!',
            're_password': 'NewEmployee123!',
            'first_name': 'Duplicate',
            'rest_of_name': 'Phone',
            'date_joined': '2025-01-15',
            'identity_type': 'passport',
            'identity_number': 'C12345678',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_employee_invalid_egyptian_phone(self):
        """Test validation of Egyptian phone number format."""
        self.authenticate_as_admin()

        response = self.client.post('/api/v1/employees/', {
            'phone_number1': '+1234567890',  # Not Egyptian
            'password': 'NewEmployee123!',
            're_password': 'NewEmployee123!',
            'first_name': 'Invalid',
            'rest_of_name': 'Phone',
            'date_joined': '2025-01-15',
            'identity_type': 'passport',
            'identity_number': 'D12345678',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_employee_invalid_nid(self):
        """Test validation of Egyptian National ID format."""
        self.authenticate_as_admin()

        response = self.client.post('/api/v1/employees/', {
            'phone_number1': '+201444444444',
            'password': 'NewEmployee123!',
            're_password': 'NewEmployee123!',
            'first_name': 'Invalid',
            'rest_of_name': 'NID',
            'date_joined': '2025-01-15',
            'identity_type': 'nid',
            'identity_number': '12345',  # Invalid NID
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_employee_password_mismatch(self):
        """Test password and re_password must match."""
        self.authenticate_as_admin()

        response = self.client.post('/api/v1/employees/', {
            'phone_number1': '+201555555555',
            'password': 'Password123!',
            're_password': 'DifferentPass123!',
            'first_name': 'Password',
            'rest_of_name': 'Mismatch',
            'date_joined': '2025-01-15',
            'identity_type': 'passport',
            'identity_number': 'E12345678',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# =============================================================================
# Admin Employee Detail/Update/Delete Tests
# =============================================================================

class AdminEmployeeDetailTests(BaseTestCase):
    """Tests for admin viewing employee details."""

    def test_admin_can_view_employee_detail(self):
        """Test admin can view any employee's details."""
        self.authenticate_as_admin()

        response = self.client.get(f'/api/v1/employees/{self.employee.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Regular')

    def test_employee_cannot_view_other_employee_detail(self):
        """Test regular employee cannot view other employees."""
        self.authenticate_as_employee()

        response = self.client.get(f'/api/v1/employees/{self.employee2.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_view_nonexistent_employee(self):
        """Test viewing non-existent employee returns 404."""
        self.authenticate_as_admin()

        fake_uuid = uuid.uuid4()
        response = self.client.get(f'/api/v1/employees/{fake_uuid}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AdminEmployeeUpdateTests(BaseTestCase):
    """Tests for admin updating employees."""

    def test_admin_can_update_employee(self):
        """Test admin can update employee data."""
        self.authenticate_as_admin()

        response = self.client.patch(f'/api/v1/employees/{self.employee.id}/', {
            'first_name': 'Updated',
            'role': 'Manager',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertEqual(response.data['role'], 'Manager')

    def test_admin_can_update_employee_phone(self):
        """Test admin can update employee phone number."""
        self.authenticate_as_admin()

        response = self.client.patch(f'/api/v1/employees/{self.employee.id}/', {
            'phone_number1': '+201012345679',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone_number1'], '+201012345679')

    def test_admin_can_toggle_staff_status(self):
        """Test admin can promote/demote employee."""
        self.authenticate_as_admin()

        # Promote to staff
        response = self.client.patch(f'/api/v1/employees/{self.employee.id}/', {
            'is_staff': True,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_staff'])

        # Demote from staff
        response = self.client.patch(f'/api/v1/employees/{self.employee.id}/', {
            'is_staff': False,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_staff'])

    def test_employee_cannot_update_other_employee(self):
        """Test regular employee cannot update other employees."""
        self.authenticate_as_employee()

        response = self.client.patch(f'/api/v1/employees/{self.employee2.id}/', {
            'first_name': 'Hacked',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_employee_cannot_update_self_via_detail(self):
        """Test regular employee cannot update self via detail endpoint."""
        self.authenticate_as_employee()

        response = self.client.patch(f'/api/v1/employees/{self.employee.id}/', {
            'first_name': 'SelfUpdate',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminEmployeeDeleteTests(BaseTestCase):
    """Tests for admin deleting (deactivating) employees."""

    def test_admin_can_deactivate_employee(self):
        """Test admin can deactivate employee (soft delete)."""
        self.authenticate_as_admin()

        response = self.client.delete(f'/api/v1/employees/{self.employee.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify employee is deactivated, not deleted
        self.employee.refresh_from_db()
        self.assertFalse(self.employee.is_active)

    def test_employee_cannot_delete_employees(self):
        """Test regular employee cannot deactivate employees."""
        self.authenticate_as_employee()

        response = self.client.delete(
            f'/api/v1/employees/{self.employee2.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminEmployeeActivateTests(BaseTestCase):
    """Tests for admin activating employees."""

    def test_admin_can_activate_employee(self):
        """Test admin can reactivate a deactivated employee."""
        # First deactivate
        self.employee.is_active = False
        self.employee.save()

        self.authenticate_as_admin()

        response = self.client.post(
            f'/api/v1/employees/{self.employee.id}/activate/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify employee is active
        self.employee.refresh_from_db()
        self.assertTrue(self.employee.is_active)

    def test_employee_cannot_activate_employees(self):
        """Test regular employee cannot activate employees."""
        self.employee2.is_active = False
        self.employee2.save()

        self.authenticate_as_employee()

        response = self.client.post(
            f'/api/v1/employees/{self.employee2.id}/activate/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_activate_nonexistent_employee(self):
        """Test activating non-existent employee returns 404."""
        self.authenticate_as_admin()

        fake_uuid = uuid.uuid4()
        response = self.client.post(f'/api/v1/employees/{fake_uuid}/activate/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AdminSetPasswordTests(BaseTestCase):
    """Tests for admin resetting employee passwords."""

    def test_admin_can_reset_employee_password(self):
        """Test admin can reset any employee's password."""
        self.authenticate_as_admin()

        response = self.client.post(f'/api/v1/employees/{self.employee.id}/set-password/', {
            'new_password': 'AdminResetPass123!',
            're_new_password': 'AdminResetPass123!',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify can login with new password
        self.client.credentials()
        tokens = self.get_tokens('+201000000002', 'AdminResetPass123!')
        self.assertIn('access', tokens)

    def test_admin_reset_password_mismatch(self):
        """Test password reset fails when passwords don't match."""
        self.authenticate_as_admin()

        response = self.client.post(f'/api/v1/employees/{self.employee.id}/set-password/', {
            'new_password': 'Password1!',
            're_new_password': 'Password2!',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_reset_password_missing_field(self):
        """Test password reset fails when password is missing."""
        self.authenticate_as_admin()

        response = self.client.post(f'/api/v1/employees/{self.employee.id}/set-password/', {
            're_new_password': 'SomePassword!',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_employee_cannot_reset_other_password(self):
        """Test regular employee cannot reset other's password."""
        self.authenticate_as_employee()

        response = self.client.post(f'/api/v1/employees/{self.employee2.id}/set-password/', {
            'new_password': 'HackedPass123!',
            're_new_password': 'HackedPass123!',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reset_nonexistent_employee_password(self):
        """Test resetting non-existent employee's password returns 404."""
        self.authenticate_as_admin()

        fake_uuid = uuid.uuid4()
        response = self.client.post(f'/api/v1/employees/{fake_uuid}/set-password/', {
            'new_password': 'SomePass123!',
            're_new_password': 'SomePass123!',
        })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# =============================================================================
# Model Validation Tests
# =============================================================================

class EmployeeModelTests(TestCase):
    """Tests for Employee model validations."""

    def test_nid_extracts_dob_and_gender(self):
        """Test DOB and gender are auto-extracted from Egyptian NID."""
        employee = Employee.objects.create_user(
            phone_number1='+201012345678',
            password='TestPass123!',
            first_name='NID',
            rest_of_name='Test',
            date_joined=date(2024, 1, 1),
            identity_type='nid',
            # Male (13th digit=1 is odd), born Jan 15, 1995
            identity_number='29501151234517',
        )

        self.assertEqual(employee.dob, date(1995, 1, 15))
        self.assertEqual(employee.gender, 'male')

    def test_nid_female_gender_extraction(self):
        """Test female gender extracted from NID (even 13th digit)."""
        employee = Employee.objects.create_user(
            phone_number1='+201123456789',
            password='TestPass123!',
            first_name='Female',
            rest_of_name='Test',
            date_joined=date(2024, 1, 1),
            identity_type='nid',
            identity_number='29501151234528',  # Female (13th digit=2 is even)
        )

        self.assertEqual(employee.gender, 'female')

    def test_empty_email_saved_as_null(self):
        """Test empty email is saved as NULL, not empty string."""
        employee = Employee.objects.create_user(
            phone_number1='+201234567893',
            password='TestPass123!',
            first_name='No',
            rest_of_name='Email',
            date_joined=date(2024, 1, 1),
            identity_type='passport',
            identity_number='F12345678',
            email='',
        )

        # Refetch from database to check actual stored value
        employee.refresh_from_db()
        self.assertIsNone(employee.email)

    def test_multiple_employees_without_email(self):
        """Test multiple employees can have no email (NULL)."""
        Employee.objects.create_user(
            phone_number1='+201111111112',
            password='TestPass123!',
            first_name='No',
            rest_of_name='Email1',
            date_joined=date(2024, 1, 1),
            identity_type='passport',
            identity_number='G12345678',
        )

        # Should not raise unique constraint error
        Employee.objects.create_user(
            phone_number1='+201111111113',
            password='TestPass123!',
            first_name='No',
            rest_of_name='Email2',
            date_joined=date(2024, 1, 1),
            identity_type='passport',
            identity_number='H12345678',
        )
