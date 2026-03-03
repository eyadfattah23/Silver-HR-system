#!/usr/bin/env python3
"""Tests for admin employee management endpoints."""

from rest_framework import status
from decimal import Decimal
import uuid

from .base import BaseTestCase
from ..models import Gender, MilitaryStatus


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
            'first_name': 'جديد',
            'second_name': 'أحمد',
            'third_name': 'محمد',
            'fourth_name': 'سعيد',
            'date_of_birth': '2000-01-15',
            'gender': 'male',
            'military_status': 'postponed',
            'hire_date': '2025-01-15',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['first_name'], 'جديد')

        # Verify employee exists
        from django.contrib.auth import get_user_model
        Employee = get_user_model()
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
            'first_name': 'كامل',
            'second_name': 'البيانات',
            'third_name': 'للموظف',
            'fourth_name': 'الجديد',
            'date_of_birth': '1995-02-01',
            'gender': 'male',
            'military_status': 'completed',
            'hire_date': '2025-02-01',
            'national_id': '29502011234517',
            'fingerprint_id': 'FPCaITM001',
            'address': '123 Main St, Cairo',
            'marital_status': 'married',
            'employment_type': 'full_time',
            'employment_state': 'active',
            'current_salary': '15000.00',
            'is_attendance_exempt': False,
            'notes': 'Test employee with all fields',
            'job_title': str(self.job_title.id),
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['first_name'], 'كامل')
        self.assertEqual(response.data['marital_status'], 'married')
        self.assertEqual(Decimal(response.data['current_salary']), Decimal('15000.00'))

    def test_admin_can_create_female_employee_auto_military_status(self):
        """Test female employee gets military_status auto-set to not_applicable."""
        self.authenticate_as_admin()

        response = self.client.post('/api/v1/employees/', {
            'phone_number1': '+201033333333',  # Valid Egyptian mobile number
            'password': 'NewEmployee123!',
            're_password': 'NewEmployee123!',
            'first_name': 'سارة',
            'second_name': 'أحمد',
            'third_name': 'محمد',
            'fourth_name': 'حسن',
            'date_of_birth': '1998-03-15',
            'gender': 'female',
            'hire_date': '2025-03-01',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['military_status'], 'not_applicable')

    def test_employee_cannot_create_employee(self):
        """Test regular employee cannot create employees."""
        self.authenticate_as_employee()

        response = self.client.post('/api/v1/employees/', {
            'phone_number1': '+201044444444',
            'password': 'NewEmployee123!',
            're_password': 'NewEmployee123!',
            'first_name': 'غير',
            'second_name': 'مصرح',
            'third_name': 'بإنشاء',
            'fourth_name': 'موظف',
            'date_of_birth': '1990-01-15',
            'gender': 'male',
            'military_status': 'completed',
            'hire_date': '2025-01-15',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_employee_duplicate_phone(self):
        """Test cannot create employee with duplicate phone number."""
        self.authenticate_as_admin()

        response = self.client.post('/api/v1/employees/', {
            'phone_number1': '+201000000002',  # Already exists
            'password': 'NewEmployee123!',
            're_password': 'NewEmployee123!',
            'first_name': 'مكرر',
            'second_name': 'الهاتف',
            'third_name': 'رقم',
            'fourth_name': 'موظف',
            'date_of_birth': '1990-01-15',
            'gender': 'male',
            'military_status': 'completed',
            'hire_date': '2025-01-15',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_employee_invalid_egyptian_phone(self):
        """Test validation of Egyptian phone number format."""
        self.authenticate_as_admin()

        response = self.client.post('/api/v1/employees/', {
            'phone_number1': '+1234567890',  # Not Egyptian
            'password': 'NewEmployee123!',
            're_password': 'NewEmployee123!',
            'first_name': 'خطأ',
            'second_name': 'في',
            'third_name': 'رقم',
            'fourth_name': 'الهاتف',
            'date_of_birth': '1990-01-15',
            'gender': 'male',
            'military_status': 'completed',
            'hire_date': '2025-01-15',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_employee_invalid_nid(self):
        """Test validation of Egyptian National ID format."""
        self.authenticate_as_admin()

        response = self.client.post('/api/v1/employees/', {
            'phone_number1': '+201055555555',  # Valid Egyptian mobile
            'password': 'NewEmployee123!',
            're_password': 'NewEmployee123!',
            'first_name': 'خطأ',
            'second_name': 'في',
            'third_name': 'الرقم',
            'fourth_name': 'القومي',
            'date_of_birth': '1990-01-15',
            'gender': 'male',
            'military_status': 'completed',
            'hire_date': '2025-01-15',
            'national_id': '12345',  # Invalid NID
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_employee_password_mismatch(self):
        """Test password and re_password must match."""
        self.authenticate_as_admin()

        response = self.client.post('/api/v1/employees/', {
            'phone_number1': '+201066666666',  # Valid Egyptian mobile
            'password': 'Password123!',
            're_password': 'DifferentPass123!',
            'first_name': 'كلمة',
            'second_name': 'المرور',
            'third_name': 'غير',
            'fourth_name': 'متطابقة',
            'date_of_birth': '1990-01-15',
            'gender': 'male',
            'military_status': 'completed',
            'hire_date': '2025-01-15',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AdminEmployeeDetailTests(BaseTestCase):
    """Tests for admin viewing employee details."""

    def test_admin_can_view_employee_detail(self):
        """Test admin can view any employee's details."""
        self.authenticate_as_admin()

        response = self.client.get(f'/api/v1/employees/{self.employee.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'فاطمة')
        self.assertEqual(response.data['full_name'], 'فاطمة أحمد محمود سعيد')

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
            'first_name': 'تحديث',
            'current_salary': '20000.00',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'تحديث')
        self.assertEqual(Decimal(response.data['current_salary']), Decimal('20000.00'))

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

    def test_admin_can_change_employment_state(self):
        """Test admin can change employee employment state."""
        self.authenticate_as_admin()

        response = self.client.patch(f'/api/v1/employees/{self.employee.id}/', {
            'employment_state': 'on_leave',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['employment_state'], 'on_leave')

    def test_admin_can_assign_job_title(self):
        """Test admin can assign job title to employee."""
        self.authenticate_as_admin()

        response = self.client.patch(f'/api/v1/employees/{self.employee2.id}/', {
            'job_title': str(self.job_title2.id),
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data['job_title']), str(self.job_title2.id))

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

        response = self.client.delete(f'/api/v1/employees/{self.employee2.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminEmployeeActivateTests(BaseTestCase):
    """Tests for admin activating employees."""

    def test_admin_can_activate_employee(self):
        """Test admin can reactivate a deactivated employee."""
        # First deactivate
        self.employee.is_active = False
        self.employee.save()

        self.authenticate_as_admin()

        response = self.client.post(f'/api/v1/employees/{self.employee.id}/activate/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify employee is active
        self.employee.refresh_from_db()
        self.assertTrue(self.employee.is_active)

    def test_employee_cannot_activate_employees(self):
        """Test regular employee cannot activate employees."""
        self.employee2.is_active = False
        self.employee2.save()

        self.authenticate_as_employee()

        response = self.client.post(f'/api/v1/employees/{self.employee2.id}/activate/')
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
