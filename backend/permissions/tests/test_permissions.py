#!/usr/bin/env python3
"""Tests for Permission endpoints (read-only)."""

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from permissions.models import Permission, Role, RolePermission, EmployeeRole
from .helpers import create_test_superuser, create_test_user


class PermissionListTests(TestCase):
    """Tests for the permission list endpoint."""
    
    def setUp(self):
        self.client = APIClient()
        
        self.superuser = create_test_superuser('01')
        self.regular_user = create_test_user('02')
        
        # Create test permissions
        self.permission1, _ = Permission.objects.get_or_create(
            code='test.view',
            defaults={
                'name': 'Test View',
                'description': 'Test permission',
                'resource': 'test',
                'action': 'view',
                'can_be_given': True,
            }
        )
        self.permission2, _ = Permission.objects.get_or_create(
            code='test.create',
            defaults={
                'name': 'Test Create',
                'description': 'Test create permission',
                'resource': 'test',
                'action': 'create',
                'can_be_given': True,
            }
        )
        
        # Create view_permissions permission and give it to regular user
        self.view_perm, _ = Permission.objects.get_or_create(
            code='permissions.view',
            defaults={
                'name': 'View Permissions',
                'resource': 'permissions',
                'action': 'view',
                'can_be_given': True,
            }
        )
    
    def test_superuser_can_list_permissions(self):
        """Superuser should be able to list all permissions."""
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(reverse('permissions:permission-list'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)
    
    def test_unauthenticated_cannot_list_permissions(self):
        """Unauthenticated user should not be able to list permissions."""
        response = self.client.get(reverse('permissions:permission-list'))
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_regular_user_without_permission_cannot_list(self):
        """Regular user without view permission cannot list permissions."""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(reverse('permissions:permission-list'))
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_user_with_view_permission_can_list(self):
        """User with permissions.view can list permissions."""
        # Create role with view permission
        role = Role.objects.create(name='Permission Viewer')
        RolePermission.objects.create(role=role, permission=self.view_perm)
        EmployeeRole.objects.create(
            employee=self.regular_user,
            role=role,
            granted_by=self.superuser,
        )
        
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(reverse('permissions:permission-list'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_can_filter_by_resource(self):
        """Should be able to filter permissions by resource."""
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(
            reverse('permissions:permission-list'),
            {'resource': 'test'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for perm in response.data:
            self.assertEqual(perm['resource'], 'test')
    
    def test_can_filter_by_can_be_given(self):
        """Should be able to filter giveable permissions."""
        Permission.objects.get_or_create(
            code='test.admin',
            defaults={
                'name': 'Test Admin',
                'resource': 'test',
                'action': 'admin',
                'can_be_given': False,
            }
        )
        
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(
            reverse('permissions:permission-list'),
            {'can_be_given': 'true'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for perm in response.data:
            self.assertTrue(perm['can_be_given'])


class PermissionDetailTests(TestCase):
    """Tests for the permission detail endpoint."""
    
    def setUp(self):
        self.client = APIClient()
        
        self.superuser = create_test_superuser('01')
        
        self.permission, _ = Permission.objects.get_or_create(
            code='test.view',
            defaults={
                'name': 'Test View',
                'description': 'Test permission',
                'resource': 'test',
                'action': 'view',
                'can_be_given': True,
            }
        )
    
    def test_superuser_can_get_permission_detail(self):
        """Superuser should be able to get permission details."""
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(
            reverse('permissions:permission-detail', kwargs={'pk': self.permission.id})
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 'test.view')
    
    def test_post_not_allowed(self):
        """POST should not be allowed on permissions (read-only)."""
        self.client.force_authenticate(user=self.superuser)
        response = self.client.post(
            reverse('permissions:permission-list'),
            {'code': 'test.new', 'name': 'New Permission'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
