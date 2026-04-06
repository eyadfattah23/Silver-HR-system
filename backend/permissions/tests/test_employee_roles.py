#!/usr/bin/env python3
"""Tests for Employee Role endpoints."""

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from permissions.models import Permission, Role, RolePermission, EmployeeRole
from core.models import City, Branch, Department
from .helpers import create_test_superuser, create_test_user


class EmployeeRoleListCreateTests(TestCase):
    """Tests for the employee role list/create endpoint."""
    
    def setUp(self):
        self.client = APIClient()
        
        self.superuser = create_test_superuser('01')
        self.regular_user = create_test_user('02', first_name='Regular')
        self.target_user = create_test_user('03', first_name='Target')
        
        # Create organizational structure
        self.city = City.objects.create(
            name='Test City',
            code='TST',
        )
        
        self.branch = Branch.objects.create(
            name='Test Branch',
            city=self.city,
        )
        
        self.department = Department.objects.create(
            name='Test Department',
            code='DP1',
            branch=self.branch,
        )
        
        # Create test role
        self.test_role = Role.objects.create(
            name='Test Role',
            description='A test role',
        )
        
        # Create permissions
        self.assign_roles_perm, _ = Permission.objects.get_or_create(
            code='permissions.assign_roles',
            defaults={
                'name': 'Assign Roles',
                'resource': 'permissions',
                'action': 'assign_roles',
                'can_be_given': True,
            }
        )
    
    def test_superuser_can_list_employee_roles(self):
        """Superuser should be able to list all employee roles."""
        EmployeeRole.objects.create(
            employee=self.target_user,
            role=self.test_role,
            granted_by=self.superuser,
        )
        
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(reverse('permissions:employee-role-list'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_superuser_can_assign_role_to_employee(self):
        """Superuser should be able to assign a role to an employee (global scope)."""
        self.client.force_authenticate(user=self.superuser)
        response = self.client.post(
            reverse('permissions:employee-role-list'),
            {
                'employee_id': str(self.target_user.id),
                'role_id': str(self.test_role.id),
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            EmployeeRole.objects.filter(
                employee=self.target_user,
                role=self.test_role,
            ).exists()
        )
    
    def test_superuser_can_assign_role_with_city_scope(self):
        """Superuser should be able to assign a role with city scope."""
        self.client.force_authenticate(user=self.superuser)
        response = self.client.post(
            reverse('permissions:employee-role-list'),
            {
                'employee_id': str(self.target_user.id),
                'role_id': str(self.test_role.id),
                'city_id': str(self.city.id),
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        employee_role = EmployeeRole.objects.get(
            employee=self.target_user,
            role=self.test_role,
        )
        self.assertEqual(employee_role.city, self.city)
    
    def test_superuser_can_assign_role_with_branch_scope(self):
        """Superuser should be able to assign a role with branch scope."""
        self.client.force_authenticate(user=self.superuser)
        response = self.client.post(
            reverse('permissions:employee-role-list'),
            {
                'employee_id': str(self.target_user.id),
                'role_id': str(self.test_role.id),
                'branch_id': str(self.branch.id),
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        employee_role = EmployeeRole.objects.get(
            employee=self.target_user,
            role=self.test_role,
        )
        self.assertEqual(employee_role.branch, self.branch)
    
    def test_regular_user_cannot_assign_roles(self):
        """Regular user without permission cannot assign roles."""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post(
            reverse('permissions:employee-role-list'),
            {
                'employee_id': str(self.target_user.id),
                'role_id': str(self.test_role.id),
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_filter_by_employee(self):
        """Should be able to filter employee roles by employee."""
        EmployeeRole.objects.create(
            employee=self.target_user,
            role=self.test_role,
            granted_by=self.superuser,
        )
        
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(
            reverse('permissions:employee-role-list'),
            {'employee': str(self.target_user.id)}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # List view uses compact serializer with employee_email instead of full employee object
        for item in response.data:
            self.assertEqual(item['employee_email'], self.target_user.email)


class EmployeeRoleDetailTests(TestCase):
    """Tests for the employee role detail endpoint."""
    
    def setUp(self):
        self.client = APIClient()
        
        self.superuser = create_test_superuser('01')
        self.target_user = create_test_user('03', first_name='Target')
        
        self.city = City.objects.create(
            name='Test City',
            code='TST',
        )
        
        self.test_role = Role.objects.create(
            name='Test Role',
            description='A test role',
        )
        
        # Create employee role without scope (global)
        self.employee_role = EmployeeRole.objects.create(
            employee=self.target_user,
            role=self.test_role,
            granted_by=self.superuser,
        )
    
    def test_superuser_can_get_employee_role_detail(self):
        """Superuser should be able to get employee role details."""
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(
            reverse('permissions:employee-role-detail', kwargs={'pk': self.employee_role.id})
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # employee is a nested object with 'id' field
        self.assertEqual(str(response.data['employee']['id']), str(self.target_user.id))
    
    def test_superuser_can_update_employee_role_scope(self):
        """Superuser should be able to update an employee role's scope to city."""
        self.client.force_authenticate(user=self.superuser)
        response = self.client.patch(
            reverse('permissions:employee-role-detail', kwargs={'pk': self.employee_role.id}),
            {
                'city_id': str(self.city.id),
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.employee_role.refresh_from_db()
        self.assertEqual(self.employee_role.city, self.city)
    
    def test_superuser_can_delete_employee_role(self):
        """Superuser should be able to revoke a role from an employee (soft delete)."""
        self.client.force_authenticate(user=self.superuser)
        response = self.client.delete(
            reverse('permissions:employee-role-detail', kwargs={'pk': self.employee_role.id})
        )
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # The view does soft delete (revoke), so the object still exists but is inactive
        self.employee_role.refresh_from_db()
        self.assertFalse(self.employee_role.is_active)
    
    def test_duplicate_role_assignment_with_same_scope_creates_separate_record(self):
        """Creating another role assignment with same scope is allowed by database.
        
        Note: Due to SQL's NULL != NULL behavior, multiple global (all NULL scope) 
        assignments are allowed by the database unique constraint.
        """
        self.client.force_authenticate(user=self.superuser)
        response = self.client.post(
            reverse('permissions:employee-role-list'),
            {
                'employee_id': str(self.target_user.id),
                'role_id': str(self.test_role.id),
            },
            format='json'
        )
        
        # Due to NULL handling in SQL, this creates a new record
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
