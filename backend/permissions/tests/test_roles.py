#!/usr/bin/env python3
"""Tests for Role endpoints."""

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from permissions.models import Permission, Role, RolePermission, EmployeeRole
from .helpers import create_test_superuser, create_test_user


class RoleListCreateTests(TestCase):
    """Tests for the role list/create endpoint."""
    
    def setUp(self):
        self.client = APIClient()
        
        self.superuser = create_test_superuser('01')
        self.regular_user = create_test_user('02')
        
        # Create permissions for role management
        self.view_roles_perm, _ = Permission.objects.get_or_create(
            code='permissions.view_roles',
            defaults={
                'name': 'View Roles',
                'resource': 'permissions',
                'action': 'view_roles',
                'can_be_given': True,
            }
        )
        self.manage_roles_perm, _ = Permission.objects.get_or_create(
            code='permissions.manage_roles',
            defaults={
                'name': 'Manage Roles',
                'resource': 'permissions',
                'action': 'manage_roles',
                'can_be_given': False,
            }
        )
        
        # Create a test role
        self.test_role = Role.objects.create(
            name='Test Role',
            description='A test role',
        )
    
    def test_superuser_can_list_roles(self):
        """Superuser should be able to list all roles."""
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(reverse('permissions:role-list'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_superuser_can_create_role(self):
        """Superuser should be able to create a role."""
        self.client.force_authenticate(user=self.superuser)
        response = self.client.post(
            reverse('permissions:role-list'),
            {
                'name': 'New Role',
                'description': 'A new test role',
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Role.objects.filter(name='New Role').exists())
    
    def test_regular_user_cannot_list_roles(self):
        """Regular user without permission cannot list roles."""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(reverse('permissions:role-list'))
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_user_with_view_roles_can_list(self):
        """User with view_roles permission can list roles."""
        # Create role with view_roles permission
        viewer_role = Role.objects.create(name='Role Viewer')
        RolePermission.objects.create(role=viewer_role, permission=self.view_roles_perm)
        EmployeeRole.objects.create(
            employee=self.regular_user,
            role=viewer_role,
            granted_by=self.superuser,
        )
        
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(reverse('permissions:role-list'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_with_view_roles_cannot_create(self):
        """User with only view_roles permission cannot create roles."""
        viewer_role = Role.objects.create(name='Role Viewer')
        RolePermission.objects.create(role=viewer_role, permission=self.view_roles_perm)
        EmployeeRole.objects.create(
            employee=self.regular_user,
            role=viewer_role,
            granted_by=self.superuser,
        )
        
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post(
            reverse('permissions:role-list'),
            {'name': 'New Role', 'description': 'Test'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_role_with_permissions(self):
        """Should be able to create a role with permissions."""
        test_perm, _ = Permission.objects.get_or_create(
            code='test.action',
            defaults={
                'name': 'Test Action',
                'resource': 'test',
                'action': 'action',
                'can_be_given': True,
            }
        )
        
        self.client.force_authenticate(user=self.superuser)
        response = self.client.post(
            reverse('permissions:role-list'),
            {
                'name': 'Role With Perms',
                'description': 'Has permissions',
                'permission_ids': [str(test_perm.id)],
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        role = Role.objects.get(name='Role With Perms')
        self.assertTrue(role.permissions.filter(id=test_perm.id).exists())


class RoleDetailTests(TestCase):
    """Tests for the role detail endpoint."""
    
    def setUp(self):
        self.client = APIClient()
        
        self.superuser = create_test_superuser('01')
        
        self.test_role = Role.objects.create(
            name='Test Role',
            description='A test role',
        )
        
        self.system_role = Role.objects.create(
            name='System Role',
            description='A system role',
            is_system_role=True,
        )
    
    def test_superuser_can_get_role_detail(self):
        """Superuser should be able to get role details."""
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(
            reverse('permissions:role-detail', kwargs={'pk': self.test_role.id})
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Role')
    
    def test_superuser_can_update_role(self):
        """Superuser should be able to update a role."""
        self.client.force_authenticate(user=self.superuser)
        response = self.client.patch(
            reverse('permissions:role-detail', kwargs={'pk': self.test_role.id}),
            {'description': 'Updated description'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.test_role.refresh_from_db()
        self.assertEqual(self.test_role.description, 'Updated description')
    
    def test_superuser_can_delete_non_system_role(self):
        """Superuser should be able to delete a non-system role."""
        self.client.force_authenticate(user=self.superuser)
        response = self.client.delete(
            reverse('permissions:role-detail', kwargs={'pk': self.test_role.id})
        )
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Role.objects.filter(id=self.test_role.id).exists())
    
    def test_cannot_delete_system_role(self):
        """Should not be able to delete a system role."""
        self.client.force_authenticate(user=self.superuser)
        response = self.client.delete(
            reverse('permissions:role-detail', kwargs={'pk': self.system_role.id})
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Role.objects.filter(id=self.system_role.id).exists())


class RolePermissionTests(TestCase):
    """Tests for adding/removing permissions from roles."""
    
    def setUp(self):
        self.client = APIClient()
        
        self.superuser = create_test_superuser('01')
        
        self.test_role = Role.objects.create(
            name='Test Role',
            description='A test role',
        )
        
        self.test_perm, _ = Permission.objects.get_or_create(
            code='test.action',
            defaults={
                'name': 'Test Action',
                'resource': 'test',
                'action': 'action',
                'can_be_given': True,
            }
        )
    
    def test_superuser_can_add_permission_to_role(self):
        """Superuser should be able to add a permission to a role."""
        self.client.force_authenticate(user=self.superuser)
        response = self.client.post(
            reverse('permissions:role-permission-add', kwargs={'pk': self.test_role.id}),
            {'permission_id': str(self.test_perm.id)}
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            RolePermission.objects.filter(
                role=self.test_role,
                permission=self.test_perm
            ).exists()
        )
    
    def test_superuser_can_remove_permission_from_role(self):
        """Superuser should be able to remove a permission from a role."""
        RolePermission.objects.create(role=self.test_role, permission=self.test_perm)
        
        self.client.force_authenticate(user=self.superuser)
        response = self.client.delete(
            reverse(
                'permissions:role-permission-remove',
                kwargs={'pk': self.test_role.id, 'permission_id': self.test_perm.id}
            )
        )
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            RolePermission.objects.filter(
                role=self.test_role,
                permission=self.test_perm
            ).exists()
        )
    
    def test_cannot_add_duplicate_permission(self):
        """Should not be able to add the same permission twice."""
        RolePermission.objects.create(role=self.test_role, permission=self.test_perm)
        
        self.client.force_authenticate(user=self.superuser)
        response = self.client.post(
            reverse('permissions:role-permission-add', kwargs={'pk': self.test_role.id}),
            {'permission_id': str(self.test_perm.id)}
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_reactivate_inactive_permission(self):
        """Adding inactive permission should reactivate it."""
        rp = RolePermission.objects.create(
            role=self.test_role,
            permission=self.test_perm,
            is_active=False,
        )
        
        self.client.force_authenticate(user=self.superuser)
        response = self.client.post(
            reverse('permissions:role-permission-add', kwargs={'pk': self.test_role.id}),
            {'permission_id': str(self.test_perm.id)}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rp.refresh_from_db()
        self.assertTrue(rp.is_active)


class RoleFilterTests(TestCase):
    """Tests for filtering roles."""
    
    def setUp(self):
        self.client = APIClient()
        self.superuser = create_test_superuser('01')
        
        self.active_role = Role.objects.create(
            name='Active Role',
            is_active=True,
        )
        self.inactive_role = Role.objects.create(
            name='Inactive Role',
            is_active=False,
        )
        self.system_role = Role.objects.create(
            name='System Role',
            is_system_role=True,
        )
    
    def test_filter_by_is_active_true(self):
        """Should filter roles by is_active=true."""
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(
            reverse('permissions:role-list'),
            {'is_active': 'true'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for role in response.data:
            self.assertTrue(role['is_active'])
    
    def test_filter_by_is_active_false(self):
        """Should filter roles by is_active=false."""
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(
            reverse('permissions:role-list'),
            {'is_active': 'false'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for role in response.data:
            self.assertFalse(role['is_active'])
    
    def test_filter_by_is_system_role(self):
        """Should filter roles by is_system_role."""
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(
            reverse('permissions:role-list'),
            {'is_system_role': 'true'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for role in response.data:
            self.assertTrue(role['is_system_role'])


class RoleDeleteConstraintsTests(TestCase):
    """Tests for role deletion constraints."""
    
    def setUp(self):
        self.client = APIClient()
        self.superuser = create_test_superuser('01')
        self.user = create_test_user('02')
        
        self.role_with_assignment = Role.objects.create(
            name='Role With Assignment',
        )
        
        EmployeeRole.objects.create(
            employee=self.user,
            role=self.role_with_assignment,
            granted_by=self.superuser,
        )
    
    def test_cannot_delete_role_with_active_assignments(self):
        """Should not be able to delete a role with active assignments."""
        self.client.force_authenticate(user=self.superuser)
        response = self.client.delete(
            reverse('permissions:role-detail', kwargs={'pk': self.role_with_assignment.id})
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Role.objects.filter(id=self.role_with_assignment.id).exists())
