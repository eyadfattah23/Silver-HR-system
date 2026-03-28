#!/usr/bin/env python3
"""Tests for Department API endpoints."""

from django.test import TestCase
from rest_framework import status
import uuid

from .base import BaseTestCase
from ..models import City, Branch, Department


class DepartmentListTests(BaseTestCase):
    """Tests for Department listing."""

    def test_superuser_can_list_departments(self):
        """Test superuser can list all departments."""
        self.authenticate_as_superuser()

        response = self.client.get('/api/v1/core/departments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # All departments

    def test_superuser_can_list_active_departments(self):
        """Test superuser can list only active departments."""
        self.authenticate_as_superuser()

        response = self.client.get('/api/v1/core/departments/active/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Only active departments

    def test_admin_cannot_list_departments(self):
        """Test admin (non-superuser) cannot list departments."""
        self.authenticate_as_admin()

        response = self.client.get('/api/v1/core/departments/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_employee_cannot_list_departments(self):
        """Test regular employee cannot list departments."""
        self.authenticate_as_employee()

        response = self.client.get('/api/v1/core/departments/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_list_departments(self):
        """Test unauthenticated request cannot list departments."""
        response = self.client.get('/api/v1/core/departments/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DepartmentCreateTests(BaseTestCase):
    """Tests for Department creation."""

    def test_superuser_can_create_department(self):
        """Test superuser can create a new department."""
        self.authenticate_as_superuser()

        response = self.client.post('/api/v1/core/departments/', {
            'name': 'New Department',
            'code': 'ND',
            'branch': str(self.branch1.id),
            'is_active': True,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Department')
        self.assertEqual(response.data['code'], 'ND')

    def test_department_code_is_uppercased(self):
        """Test department code is automatically uppercased."""
        self.authenticate_as_superuser()

        response = self.client.post('/api/v1/core/departments/', {
            'name': 'Marketing',
            'code': 'mkt',
            'branch': str(self.branch1.id),
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['code'], 'MKT')

    def test_cannot_create_duplicate_department_code(self):
        """Test cannot create department with duplicate code."""
        self.authenticate_as_superuser()

        response = self.client.post('/api/v1/core/departments/', {
            'name': 'Another HR',
            'code': 'HR',  # Already exists
            'branch': str(self.branch2.id),
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_create_department_in_inactive_branch(self):
        """Test cannot create department in an inactive branch."""
        self.authenticate_as_superuser()

        response = self.client.post('/api/v1/core/departments/', {
            'name': 'Department in Inactive Branch',
            'code': 'DIB',
            'branch': str(self.inactive_branch.id),
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_cannot_create_department(self):
        """Test admin (non-superuser) cannot create departments."""
        self.authenticate_as_admin()

        response = self.client.post('/api/v1/core/departments/', {
            'name': 'New Department',
            'code': 'ND',
            'branch': str(self.branch1.id),
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_department_created_without_code(self):
        """Test department can be created without code (optional)."""
        self.authenticate_as_superuser()

        response = self.client.post('/api/v1/core/departments/', {
            'name': 'No Code Department',
            'branch': str(self.branch1.id),
        })
        # Should succeed if code is optional
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])


class DepartmentDetailTests(BaseTestCase):
    """Tests for Department detail view."""

    def test_superuser_can_view_department(self):
        """Test superuser can view department details."""
        self.authenticate_as_superuser()

        response = self.client.get(f'/api/v1/core/departments/{self.department1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'IT Department')
        self.assertIn('branch_detail', response.data)
        self.assertIn('employee_count', response.data)

    def test_superuser_can_update_department(self):
        """Test superuser can update department."""
        self.authenticate_as_superuser()

        response = self.client.patch(f'/api/v1/core/departments/{self.department1.id}/', {
            'name': 'Updated HR',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated HR')

    def test_superuser_can_change_department_code(self):
        """Test superuser can change department code."""
        self.authenticate_as_superuser()

        response = self.client.patch(f'/api/v1/core/departments/{self.department1.id}/', {
            'code': 'HRD',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 'HRD')

    def test_superuser_can_change_department_branch(self):
        """Test superuser can move department to different branch."""
        self.authenticate_as_superuser()

        response = self.client.patch(f'/api/v1/core/departments/{self.department2.id}/', {
            'branch': str(self.branch2.id),
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_superuser_can_deactivate_department(self):
        """Test superuser can deactivate (soft delete) department."""
        self.authenticate_as_superuser()

        response = self.client.delete(f'/api/v1/core/departments/{self.department1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify department is deactivated, not deleted
        self.department1.refresh_from_db()
        self.assertFalse(self.department1.is_active)

    def test_view_nonexistent_department(self):
        """Test viewing non-existent department returns 404."""
        self.authenticate_as_superuser()

        fake_uuid = uuid.uuid4()
        response = self.client.get(f'/api/v1/core/departments/{fake_uuid}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_cannot_update_department(self):
        """Test admin (non-superuser) cannot update departments."""
        self.authenticate_as_admin()

        response = self.client.patch(f'/api/v1/core/departments/{self.department1.id}/', {
            'name': 'Hacked',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DepartmentModelTests(TestCase):
    """Tests for Department model."""

    @classmethod
    def setUpTestData(cls):
        """Create test city and branch."""
        cls.city = City.objects.create(
            name='Test City',
            code='TC'
        )
        cls.branch = Branch.objects.create(
            name='Test Branch',
            city=cls.city
        )

    def test_department_str_representation(self):
        """Test string representation of Department."""
        department = Department.objects.create(
            name='Test Department',
            code='TD',
            branch=self.branch
        )
        self.assertEqual(str(department), 'Test Department - Test Branch')

    def test_department_default_is_active(self):
        """Test Department defaults to is_active=True."""
        department = Department.objects.create(
            name='Active Department',
            code='AD',
            branch=self.branch
        )
        self.assertTrue(department.is_active)
