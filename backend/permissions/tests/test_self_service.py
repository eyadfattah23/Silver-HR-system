#!/usr/bin/env python3
"""Tests for self-service permission endpoints."""

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from permissions.models import (
    Permission, Role, RolePermission, EmployeeRole, EmployeeExtraPermission
)
from core.models import City, Branch, Department
from .helpers import create_test_superuser, create_test_user


class MyPermissionsTests(TestCase):
    """Tests for the my-permissions endpoint."""
    
    def setUp(self):
        self.client = APIClient()
        
        self.superuser = create_test_superuser('01')
        self.regular_user = create_test_user('02')
        
        # Create permissions
        self.view_perm, _ = Permission.objects.get_or_create(
            code='test.view',
            defaults={
                'name': 'View Test',
                'resource': 'test',
                'action': 'view',
                'can_be_given': True,
            }
        )
        self.create_perm, _ = Permission.objects.get_or_create(
            code='test.create',
            defaults={
                'name': 'Create Test',
                'resource': 'test',
                'action': 'create',
                'can_be_given': True,
            }
        )
        
        # Create role with permission
        self.test_role = Role.objects.create(
            name='Test Role',
            description='A test role',
        )
        RolePermission.objects.create(role=self.test_role, permission=self.view_perm)
        
        # Assign role to user
        EmployeeRole.objects.create(
            employee=self.regular_user,
            role=self.test_role,
            granted_by=self.superuser,
        )
        
        # Add extra permission
        EmployeeExtraPermission.objects.create(
            employee=self.regular_user,
            permission=self.create_perm,
            granted_by=self.superuser,
        )
    
    def test_authenticated_user_can_get_permissions(self):
        """Authenticated user should be able to get their permissions."""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(reverse('permissions:my-permissions'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should have both role-based and extra permissions
        # Response is {'permissions': [...], 'by_resource': {...}, ...}
        permission_codes = [p['code'] for p in response.data['permissions']]
        self.assertIn('test.view', permission_codes)
        self.assertIn('test.create', permission_codes)
    
    def test_unauthenticated_user_cannot_access(self):
        """Unauthenticated user should not be able to access my-permissions."""
        response = self.client.get(reverse('permissions:my-permissions'))
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_superuser_sees_all_permissions(self):
        """Superuser should see all permissions."""
        # Create more permissions
        Permission.objects.get_or_create(
            code='another.perm',
            defaults={
                'name': 'Another Permission',
                'resource': 'another',
                'action': 'perm',
                'can_be_given': True,
            }
        )
        
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(reverse('permissions:my-permissions'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Superuser should get all permissions
        self.assertGreaterEqual(len(response.data), 3)


class MyRolesTests(TestCase):
    """Tests for the my-roles endpoint."""
    
    def setUp(self):
        self.client = APIClient()
        
        self.superuser = create_test_superuser('01')
        self.regular_user = create_test_user('02')
        
        self.city = City.objects.create(
            name='Test City',
            code='TST',
        )
        
        # Create roles
        self.role1 = Role.objects.create(name='Role One')
        self.role2 = Role.objects.create(name='Role Two')
        
        # Assign roles with different scopes (global and city)
        EmployeeRole.objects.create(
            employee=self.regular_user,
            role=self.role1,
            granted_by=self.superuser,
        )
        EmployeeRole.objects.create(
            employee=self.regular_user,
            role=self.role2,
            granted_by=self.superuser,
            city=self.city,
        )
    
    def test_authenticated_user_can_get_roles(self):
        """Authenticated user should be able to get their roles."""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(reverse('permissions:my-roles'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Response is {'roles': [...], 'total_count': ...}
        # Each role has 'role_name' not nested 'role' object
        self.assertEqual(len(response.data['roles']), 2)
        
        role_names = [r['role_name'] for r in response.data['roles']]
        self.assertIn('Role One', role_names)
        self.assertIn('Role Two', role_names)
    
    def test_unauthenticated_user_cannot_access(self):
        """Unauthenticated user should not be able to access my-roles."""
        response = self.client.get(reverse('permissions:my-roles'))
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class GiveablePermissionsTests(TestCase):
    """Tests for the giveable permissions endpoint."""
    
    def setUp(self):
        self.client = APIClient()
        
        self.superuser = create_test_superuser('01')
        self.regular_user = create_test_user('02')
        
        self.city = City.objects.create(
            name='Test City',
            code='TST',
        )
        
        # Create permissions
        self.give_perm, _ = Permission.objects.get_or_create(
            code='permissions.give_own',
            defaults={
                'name': 'Give Own Permissions',
                'resource': 'permissions',
                'action': 'give_own',
                'can_be_given': False,
            }
        )
        
        self.giveable_perm, _ = Permission.objects.get_or_create(
            code='test.view',
            defaults={
                'name': 'View Test',
                'resource': 'test',
                'action': 'view',
                'can_be_given': True,
            }
        )
        
        self.non_giveable_perm, _ = Permission.objects.get_or_create(
            code='test.admin',
            defaults={
                'name': 'Admin Test',
                'resource': 'test',
                'action': 'admin',
                'can_be_given': False,
            }
        )
        
        # Create role with permissions and give ability
        self.test_role = Role.objects.create(name='Test Role')
        RolePermission.objects.create(role=self.test_role, permission=self.give_perm)
        RolePermission.objects.create(role=self.test_role, permission=self.giveable_perm)
        
        # Assign role to user with city scope
        EmployeeRole.objects.create(
            employee=self.regular_user,
            role=self.test_role,
            granted_by=self.superuser,
            city=self.city,
        )
    
    def test_user_can_see_giveable_permissions(self):
        """User with give_own permission should see their giveable permissions."""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(reverse('permissions:giveable-permissions'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Response is {'permissions': [...], 'can_give': True, 'total_count': ...}
        perm_codes = [p['code'] for p in response.data['permissions']]
        self.assertIn('test.view', perm_codes)
        # Should NOT see non-giveable permissions
        self.assertNotIn('test.admin', perm_codes)
        self.assertNotIn('permissions.give_own', perm_codes)
    
    def test_superuser_sees_all_giveable_permissions(self):
        """Superuser should see all giveable permissions."""
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(reverse('permissions:giveable-permissions'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Response is {'permissions': [...], 'can_give': True, 'total_count': ...}
        perm_codes = [p['code'] for p in response.data['permissions']]
        self.assertIn('test.view', perm_codes)


class GivePermissionTests(TestCase):
    """Tests for the give permission endpoint."""
    
    def setUp(self):
        self.client = APIClient()
        
        self.superuser = create_test_superuser('01')
        self.granter = create_test_user('02', first_name='Granter')
        self.recipient = create_test_user('03', first_name='Recipient')
        
        self.city = City.objects.create(
            name='Test City',
            code='TST',
        )
        
        self.branch = Branch.objects.create(
            name='Test Branch',
            city=self.city,
        )
        
        # Create permissions
        self.give_perm, _ = Permission.objects.get_or_create(
            code='permissions.give_own',
            defaults={
                'name': 'Give Own Permissions',
                'resource': 'permissions',
                'action': 'give_own',
                'can_be_given': False,
            }
        )
        
        self.giveable_perm, _ = Permission.objects.get_or_create(
            code='test.view',
            defaults={
                'name': 'View Test',
                'resource': 'test',
                'action': 'view',
                'can_be_given': True,
            }
        )
        
        # Create role with give_own permission
        self.test_role = Role.objects.create(name='Test Role')
        RolePermission.objects.create(role=self.test_role, permission=self.give_perm)
        RolePermission.objects.create(role=self.test_role, permission=self.giveable_perm)
        
        # Assign role to granter with branch scope
        EmployeeRole.objects.create(
            employee=self.granter,
            role=self.test_role,
            granted_by=self.superuser,
            branch=self.branch,
        )
    
    def test_superuser_can_give_permission(self):
        """Superuser should be able to give any permission."""
        self.client.force_authenticate(user=self.superuser)
        response = self.client.post(
            reverse('permissions:give-permission'),
            {
                'recipient_id': str(self.recipient.id),
                'permission_code': self.giveable_perm.code,
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            EmployeeExtraPermission.objects.filter(
                employee=self.recipient,
                permission=self.giveable_perm,
            ).exists()
        )
    
    def test_granter_can_give_their_permission(self):
        """User with give_own can give their own giveable permissions."""
        self.client.force_authenticate(user=self.granter)
        response = self.client.post(
            reverse('permissions:give-permission'),
            {
                'recipient_id': str(self.recipient.id),
                'permission_code': self.giveable_perm.code,
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Permission should be granted with granter's scope
        extra_perm = EmployeeExtraPermission.objects.get(
            employee=self.recipient,
            permission=self.giveable_perm,
        )
        self.assertEqual(extra_perm.granted_by, self.granter)
        self.assertEqual(extra_perm.branch, self.branch)
    
    def test_user_without_permission_cannot_give(self):
        """User without give_own permission cannot give permissions."""
        plain_user = create_test_user('04', first_name='Plain')
        
        self.client.force_authenticate(user=plain_user)
        response = self.client.post(
            reverse('permissions:give-permission'),
            {
                'recipient_id': str(self.recipient.id),
                'permission_code': self.giveable_perm.code,
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_cannot_give_non_giveable_permission(self):
        """Should not be able to give a non-giveable permission."""
        self.client.force_authenticate(user=self.granter)
        response = self.client.post(
            reverse('permissions:give-permission'),
            {
                'recipient_id': str(self.recipient.id),
                'permission_code': self.give_perm.code,  # give_own is not giveable
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ExtraPermissionTests(TestCase):
    """Tests for extra permission management endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        
        self.superuser = create_test_superuser('01')
        self.target_user = create_test_user('03', first_name='Target')
        
        self.test_perm, _ = Permission.objects.get_or_create(
            code='test.view',
            defaults={
                'name': 'View Test',
                'resource': 'test',
                'action': 'view',
                'can_be_given': True,
            }
        )
        
        self.extra_perm = EmployeeExtraPermission.objects.create(
            employee=self.target_user,
            permission=self.test_perm,
            granted_by=self.superuser,
        )
    
    def test_superuser_can_list_extra_permissions(self):
        """Superuser should be able to list all extra permissions."""
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(reverse('permissions:extra-permission-list'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_superuser_can_delete_extra_permission(self):
        """Superuser should be able to delete an extra permission."""
        self.client.force_authenticate(user=self.superuser)
        response = self.client.delete(
            reverse('permissions:extra-permission-detail', kwargs={'pk': self.extra_perm.id})
        )
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            EmployeeExtraPermission.objects.filter(id=self.extra_perm.id).exists()
        )
    
    def test_filter_by_employee(self):
        """Should be able to filter extra permissions by employee."""
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(
            reverse('permissions:extra-permission-list'),
            {'employee': str(self.target_user.id)}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # List view uses compact serializer with employee_email
        for item in response.data:
            self.assertEqual(item['employee_email'], self.target_user.email)
    
    def test_superuser_can_create_extra_permission(self):
        """Superuser should be able to create extra permissions."""
        another_perm, _ = Permission.objects.get_or_create(
            code='test.create',
            defaults={
                'name': 'Create Test',
                'resource': 'test',
                'action': 'create',
                'can_be_given': True,
            }
        )
        
        self.client.force_authenticate(user=self.superuser)
        response = self.client.post(
            reverse('permissions:extra-permission-list'),
            {
                'employee_id': str(self.target_user.id),
                'permission_id': str(another_perm.id),
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            EmployeeExtraPermission.objects.filter(
                employee=self.target_user,
                permission=another_perm,
            ).exists()
        )
    
    def test_superuser_can_update_extra_permission(self):
        """Superuser should be able to update extra permission scope."""
        city = City.objects.create(name='Test City', code='TST2')
        
        self.client.force_authenticate(user=self.superuser)
        response = self.client.patch(
            reverse('permissions:extra-permission-detail', kwargs={'pk': self.extra_perm.id}),
            {
                'city_id': str(city.id),
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.extra_perm.refresh_from_db()
        self.assertEqual(self.extra_perm.city, city)
    
    def test_filter_by_permission_code(self):
        """Should be able to filter extra permissions by permission code."""
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(
            reverse('permissions:extra-permission-list'),
            {'permission_code': 'test.view'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data:
            self.assertEqual(item['permission_code'], 'test.view')
    
    def test_regular_user_cannot_create_extra_permission(self):
        """Regular user without permission cannot create extra permissions."""
        regular_user = create_test_user('05', first_name='Regular')
        
        self.client.force_authenticate(user=regular_user)
        response = self.client.post(
            reverse('permissions:extra-permission-list'),
            {
                'employee_id': str(self.target_user.id),
                'permission_id': str(self.test_perm.id),
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
