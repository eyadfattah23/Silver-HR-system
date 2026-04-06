#!/usr/bin/env python3
"""Tests for permission utility functions."""

from django.test import TestCase

from permissions.models import Permission, Role, RolePermission, EmployeeRole, EmployeeExtraPermission
from permissions.utils import has_permission, get_user_permissions, get_user_roles, get_giveable_permissions
from core.models import City, Branch, Department
from .helpers import create_test_superuser, create_test_user


class HasPermissionTests(TestCase):
    """Tests for the has_permission utility function."""
    
    def setUp(self):
        self.superuser = create_test_superuser('01')
        self.regular_user = create_test_user('02')
        
        # Create test permission
        self.view_perm, _ = Permission.objects.get_or_create(
            code='test.view',
            defaults={
                'name': 'View Test',
                'resource': 'test',
                'action': 'view',
                'can_be_given': True,
            }
        )
        
        # Create organizational structure
        self.city = City.objects.create(name='Test City', code='TST')
        self.branch = Branch.objects.create(name='Test Branch', city=self.city)
        self.department = Department.objects.create(
            name='Test Department',
            code='DP1',
            branch=self.branch,
        )
        
        # Create role and assign to user
        self.test_role = Role.objects.create(name='Test Role')
        RolePermission.objects.create(role=self.test_role, permission=self.view_perm)
    
    def test_superuser_has_all_permissions(self):
        """Superuser should have all permissions."""
        self.assertTrue(has_permission(self.superuser, 'test.view'))
        self.assertTrue(has_permission(self.superuser, 'any.permission'))
    
    def test_unauthenticated_user_has_no_permissions(self):
        """Unauthenticated users should have no permissions."""
        self.assertFalse(has_permission(None, 'test.view'))
    
    def test_user_without_role_has_no_permissions(self):
        """User without roles should not have permissions."""
        self.assertFalse(has_permission(self.regular_user, 'test.view'))
    
    def test_user_with_global_role_has_permission(self):
        """User with global role should have permission."""
        EmployeeRole.objects.create(
            employee=self.regular_user,
            role=self.test_role,
            granted_by=self.superuser,
        )
        
        self.assertTrue(has_permission(self.regular_user, 'test.view'))
    
    def test_user_with_city_scoped_role_has_permission_without_scope_check(self):
        """User with city-scoped role should have permission when no scope is checked."""
        EmployeeRole.objects.create(
            employee=self.regular_user,
            role=self.test_role,
            granted_by=self.superuser,
            city=self.city,
        )
        
        # Without scope check, should have permission
        self.assertTrue(has_permission(self.regular_user, 'test.view'))
    
    def test_user_with_city_scoped_role_has_permission_in_same_city(self):
        """User with city-scoped role should have permission in that city."""
        EmployeeRole.objects.create(
            employee=self.regular_user,
            role=self.test_role,
            granted_by=self.superuser,
            city=self.city,
        )
        
        self.assertTrue(has_permission(self.regular_user, 'test.view', city=self.city))
    
    def test_user_with_city_scoped_role_no_permission_in_different_city(self):
        """User with city-scoped role should not have permission in different city."""
        other_city = City.objects.create(name='Other City', code='OTH')
        
        EmployeeRole.objects.create(
            employee=self.regular_user,
            role=self.test_role,
            granted_by=self.superuser,
            city=self.city,
        )
        
        self.assertFalse(has_permission(self.regular_user, 'test.view', city=other_city))
    
    def test_user_with_extra_permission(self):
        """User with extra permission should have that permission."""
        EmployeeExtraPermission.objects.create(
            employee=self.regular_user,
            permission=self.view_perm,
            granted_by=self.superuser,
        )
        
        self.assertTrue(has_permission(self.regular_user, 'test.view'))
    
    def test_inactive_role_assignment_not_counted(self):
        """Inactive role assignments should not grant permission."""
        EmployeeRole.objects.create(
            employee=self.regular_user,
            role=self.test_role,
            granted_by=self.superuser,
            is_active=False,
        )
        
        self.assertFalse(has_permission(self.regular_user, 'test.view'))
    
    def test_inactive_role_not_counted(self):
        """Inactive roles should not grant permission."""
        self.test_role.is_active = False
        self.test_role.save()
        
        EmployeeRole.objects.create(
            employee=self.regular_user,
            role=self.test_role,
            granted_by=self.superuser,
        )
        
        self.assertFalse(has_permission(self.regular_user, 'test.view'))


class GetUserPermissionsTests(TestCase):
    """Tests for get_user_permissions utility function."""
    
    def setUp(self):
        self.superuser = create_test_superuser('01')
        self.regular_user = create_test_user('02')
        
        self.perm1, _ = Permission.objects.get_or_create(
            code='test.view',
            defaults={'name': 'View Test', 'resource': 'test', 'action': 'view', 'can_be_given': True}
        )
        self.perm2, _ = Permission.objects.get_or_create(
            code='test.create',
            defaults={'name': 'Create Test', 'resource': 'test', 'action': 'create', 'can_be_given': True}
        )
        
        self.test_role = Role.objects.create(name='Test Role')
        RolePermission.objects.create(role=self.test_role, permission=self.perm1)
    
    def test_user_gets_role_permissions(self):
        """User should get permissions from their assigned roles."""
        EmployeeRole.objects.create(
            employee=self.regular_user,
            role=self.test_role,
            granted_by=self.superuser,
        )
        
        perms = get_user_permissions(self.regular_user)
        codes = [p['code'] for p in perms]
        
        self.assertIn('test.view', codes)
    
    def test_user_gets_extra_permissions(self):
        """User should get their extra permissions."""
        EmployeeExtraPermission.objects.create(
            employee=self.regular_user,
            permission=self.perm2,
            granted_by=self.superuser,
        )
        
        perms = get_user_permissions(self.regular_user)
        codes = [p['code'] for p in perms]
        
        self.assertIn('test.create', codes)
    
    def test_permissions_include_source_info(self):
        """Permissions should include source information."""
        EmployeeRole.objects.create(
            employee=self.regular_user,
            role=self.test_role,
            granted_by=self.superuser,
        )
        
        perms = get_user_permissions(self.regular_user)
        role_perms = [p for p in perms if p.get('source') == 'role']
        
        self.assertGreater(len(role_perms), 0)
        self.assertEqual(role_perms[0]['role_name'], 'Test Role')


class GetUserRolesTests(TestCase):
    """Tests for get_user_roles utility function."""
    
    def setUp(self):
        self.superuser = create_test_superuser('01')
        self.regular_user = create_test_user('02')
        
        self.role1 = Role.objects.create(name='Role One')
        self.role2 = Role.objects.create(name='Role Two')
    
    def test_user_gets_their_roles(self):
        """User should get their assigned roles."""
        EmployeeRole.objects.create(
            employee=self.regular_user,
            role=self.role1,
            granted_by=self.superuser,
        )
        EmployeeRole.objects.create(
            employee=self.regular_user,
            role=self.role2,
            granted_by=self.superuser,
        )
        
        roles = get_user_roles(self.regular_user)
        names = [r['role_name'] for r in roles]
        
        self.assertIn('Role One', names)
        self.assertIn('Role Two', names)
    
    def test_inactive_roles_not_returned(self):
        """Inactive role assignments should not be returned."""
        EmployeeRole.objects.create(
            employee=self.regular_user,
            role=self.role1,
            granted_by=self.superuser,
            is_active=False,
        )
        
        roles = get_user_roles(self.regular_user)
        
        self.assertEqual(len(roles), 0)


class GetGiveablePermissionsTests(TestCase):
    """Tests for get_giveable_permissions utility function."""
    
    def setUp(self):
        self.superuser = create_test_superuser('01')
        self.regular_user = create_test_user('02')
        
        self.give_perm, _ = Permission.objects.get_or_create(
            code='permissions.give_own',
            defaults={'name': 'Give Own', 'resource': 'permissions', 'action': 'give_own', 'can_be_given': False}
        )
        self.giveable_perm, _ = Permission.objects.get_or_create(
            code='test.view',
            defaults={'name': 'View Test', 'resource': 'test', 'action': 'view', 'can_be_given': True}
        )
        self.non_giveable_perm, _ = Permission.objects.get_or_create(
            code='test.admin',
            defaults={'name': 'Admin Test', 'resource': 'test', 'action': 'admin', 'can_be_given': False}
        )
        
        self.test_role = Role.objects.create(name='Test Role')
        RolePermission.objects.create(role=self.test_role, permission=self.give_perm)
        RolePermission.objects.create(role=self.test_role, permission=self.giveable_perm)
        RolePermission.objects.create(role=self.test_role, permission=self.non_giveable_perm)
    
    def test_user_without_give_own_gets_empty(self):
        """User without give_own permission should get empty list."""
        perms = get_giveable_permissions(self.regular_user)
        
        self.assertEqual(len(perms), 0)
    
    def test_user_with_give_own_gets_giveable_permissions(self):
        """User with give_own should get their giveable permissions."""
        EmployeeRole.objects.create(
            employee=self.regular_user,
            role=self.test_role,
            granted_by=self.superuser,
        )
        
        perms = get_giveable_permissions(self.regular_user)
        codes = [p['code'] for p in perms]
        
        self.assertIn('test.view', codes)
        self.assertNotIn('test.admin', codes)  # Not giveable
        self.assertNotIn('permissions.give_own', codes)  # Not giveable
    
    def test_superuser_gets_all_giveable_permissions(self):
        """Superuser should get all giveable permissions."""
        perms = get_giveable_permissions(self.superuser)
        codes = [p['code'] for p in perms]
        
        self.assertIn('test.view', codes)
        self.assertNotIn('test.admin', codes)  # Not giveable even for superuser
