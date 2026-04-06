#!/usr/bin/env python3
"""Tests for permission models and their methods."""

from django.test import TestCase
from django.utils import timezone

from permissions.models import Permission, Role, RolePermission, EmployeeRole, EmployeeExtraPermission
from core.models import City, Branch, Department
from .helpers import create_test_superuser, create_test_user


class PermissionModelTests(TestCase):
    """Tests for the Permission model."""
    
    def test_permission_str(self):
        """Permission string representation should be resource.action."""
        perm = Permission.objects.create(
            code='test.view',
            name='View Test',
            resource='test',
            action='view',
        )
        
        self.assertEqual(str(perm), 'test.view')


class RoleModelTests(TestCase):
    """Tests for the Role model."""
    
    def setUp(self):
        self.role = Role.objects.create(
            name='Test Role',
            description='A test role',
        )
        
        self.perm1, _ = Permission.objects.get_or_create(
            code='test.view',
            defaults={'name': 'View Test', 'resource': 'test', 'action': 'view'}
        )
        self.perm2, _ = Permission.objects.get_or_create(
            code='test.create',
            defaults={'name': 'Create Test', 'resource': 'test', 'action': 'create'}
        )
    
    def test_role_str(self):
        """Role string representation should be the name."""
        self.assertEqual(str(self.role), 'Test Role')
    
    def test_has_permission(self):
        """Role.has_permission should check if role has a permission."""
        RolePermission.objects.create(role=self.role, permission=self.perm1)
        
        self.assertTrue(self.role.has_permission('test.view'))
        self.assertFalse(self.role.has_permission('test.create'))
    
    def test_has_resource_action(self):
        """Role.has_resource_action should check resource and action."""
        RolePermission.objects.create(role=self.role, permission=self.perm1)
        
        self.assertTrue(self.role.has_resource_action('test', 'view'))
        self.assertFalse(self.role.has_resource_action('test', 'create'))
    
    def test_get_active_permissions(self):
        """Role.get_active_permissions should return only active permissions."""
        rp1 = RolePermission.objects.create(role=self.role, permission=self.perm1)
        rp2 = RolePermission.objects.create(role=self.role, permission=self.perm2, is_active=False)
        
        active_perms = self.role.get_active_permissions()
        codes = [p.code for p in active_perms]
        
        self.assertIn('test.view', codes)
        self.assertNotIn('test.create', codes)


class EmployeeRoleModelTests(TestCase):
    """Tests for the EmployeeRole model."""
    
    def setUp(self):
        self.superuser = create_test_superuser('01')
        self.user = create_test_user('02')
        self.role = Role.objects.create(name='Test Role')
        
        self.city = City.objects.create(name='Test City', code='TST')
        self.city2 = City.objects.create(name='Other City', code='OTH')
        self.branch = Branch.objects.create(name='Test Branch', city=self.city)
        self.branch2 = Branch.objects.create(name='Other Branch', city=self.city2)
        self.department = Department.objects.create(name='Test Dept', code='DP1', branch=self.branch)
        self.department2 = Department.objects.create(name='Other Dept', code='DP2', branch=self.branch2)
    
    def test_employee_role_str_global(self):
        """Global EmployeeRole string representation."""
        er = EmployeeRole.objects.create(
            employee=self.user,
            role=self.role,
            granted_by=self.superuser,
        )
        
        self.assertIn('Global', str(er))
    
    def test_employee_role_str_city(self):
        """City-scoped EmployeeRole string representation."""
        er = EmployeeRole.objects.create(
            employee=self.user,
            role=self.role,
            granted_by=self.superuser,
            city=self.city,
        )
        
        self.assertIn('City', str(er))
    
    def test_scope_level_global(self):
        """scope_level should return 'global' for no scope."""
        er = EmployeeRole.objects.create(
            employee=self.user,
            role=self.role,
            granted_by=self.superuser,
        )
        
        self.assertEqual(er.scope_level, 'global')
    
    def test_scope_level_city(self):
        """scope_level should return 'city' for city scope."""
        er = EmployeeRole.objects.create(
            employee=self.user,
            role=self.role,
            granted_by=self.superuser,
            city=self.city,
        )
        
        self.assertEqual(er.scope_level, 'city')
    
    def test_scope_level_branch(self):
        """scope_level should return 'branch' for branch scope."""
        er = EmployeeRole.objects.create(
            employee=self.user,
            role=self.role,
            granted_by=self.superuser,
            branch=self.branch,
        )
        
        self.assertEqual(er.scope_level, 'branch')
    
    def test_scope_level_department(self):
        """scope_level should return 'department' for department scope."""
        er = EmployeeRole.objects.create(
            employee=self.user,
            role=self.role,
            granted_by=self.superuser,
            department=self.department,
        )
        
        self.assertEqual(er.scope_level, 'department')
    
    def test_applies_to_global_applies_everywhere(self):
        """Global role should apply everywhere."""
        er = EmployeeRole.objects.create(
            employee=self.user,
            role=self.role,
            granted_by=self.superuser,
        )
        
        self.assertTrue(er.applies_to())
        self.assertTrue(er.applies_to(city=self.city))
        self.assertTrue(er.applies_to(branch=self.branch))
        self.assertTrue(er.applies_to(department=self.department))
    
    def test_applies_to_city_scope(self):
        """City-scoped role should apply to city and its branches/departments."""
        er = EmployeeRole.objects.create(
            employee=self.user,
            role=self.role,
            granted_by=self.superuser,
            city=self.city,
        )
        
        # Applies to same city
        self.assertTrue(er.applies_to(city=self.city))
        # Does not apply to different city
        self.assertFalse(er.applies_to(city=self.city2))
        # Applies to branch in same city
        self.assertTrue(er.applies_to(branch=self.branch))
        # Does not apply to branch in different city
        self.assertFalse(er.applies_to(branch=self.branch2))
    
    def test_applies_to_branch_scope(self):
        """Branch-scoped role should apply to branch and its departments."""
        er = EmployeeRole.objects.create(
            employee=self.user,
            role=self.role,
            granted_by=self.superuser,
            branch=self.branch,
        )
        
        self.assertTrue(er.applies_to(branch=self.branch))
        self.assertFalse(er.applies_to(branch=self.branch2))
        self.assertTrue(er.applies_to(department=self.department))
        self.assertFalse(er.applies_to(department=self.department2))
    
    def test_applies_to_department_scope(self):
        """Department-scoped role should apply only to that department."""
        er = EmployeeRole.objects.create(
            employee=self.user,
            role=self.role,
            granted_by=self.superuser,
            department=self.department,
        )
        
        self.assertTrue(er.applies_to(department=self.department))
        self.assertFalse(er.applies_to(department=self.department2))
    
    def test_revoke(self):
        """revoke() should deactivate and set revoked fields."""
        er = EmployeeRole.objects.create(
            employee=self.user,
            role=self.role,
            granted_by=self.superuser,
        )
        
        er.revoke(self.superuser)
        er.refresh_from_db()
        
        self.assertFalse(er.is_active)
        self.assertEqual(er.revoked_by, self.superuser)
        self.assertIsNotNone(er.revoked_at)


class EmployeeExtraPermissionModelTests(TestCase):
    """Tests for the EmployeeExtraPermission model."""
    
    def setUp(self):
        self.superuser = create_test_superuser('01')
        self.user = create_test_user('02')
        self.perm, _ = Permission.objects.get_or_create(
            code='test.view',
            defaults={'name': 'View Test', 'resource': 'test', 'action': 'view'}
        )
        
        self.city = City.objects.create(name='Test City', code='TST')
        self.branch = Branch.objects.create(name='Test Branch', city=self.city)
        self.department = Department.objects.create(name='Test Dept', code='DP1', branch=self.branch)
    
    def test_extra_permission_str(self):
        """EmployeeExtraPermission string representation."""
        ep = EmployeeExtraPermission.objects.create(
            employee=self.user,
            permission=self.perm,
            granted_by=self.superuser,
        )
        
        self.assertIn('test.view', str(ep))
    
    def test_scope_level_property(self):
        """scope_level should return correct level."""
        ep = EmployeeExtraPermission.objects.create(
            employee=self.user,
            permission=self.perm,
            granted_by=self.superuser,
        )
        self.assertEqual(ep.scope_level, 'global')
        
        ep2 = EmployeeExtraPermission.objects.create(
            employee=self.superuser,  # Different user to avoid unique constraint
            permission=self.perm,
            granted_by=self.superuser,
            city=self.city,
        )
        self.assertEqual(ep2.scope_level, 'city')
    
    def test_applies_to_no_scope_always_true(self):
        """applies_to with no parameters should return True."""
        ep = EmployeeExtraPermission.objects.create(
            employee=self.user,
            permission=self.perm,
            granted_by=self.superuser,
            city=self.city,
        )
        
        # No scope check - should always return True
        self.assertTrue(ep.applies_to())


class RolePermissionModelTests(TestCase):
    """Tests for the RolePermission model."""
    
    def setUp(self):
        self.role = Role.objects.create(name='Test Role')
        self.perm, _ = Permission.objects.get_or_create(
            code='test.view',
            defaults={'name': 'View Test', 'resource': 'test', 'action': 'view'}
        )
    
    def test_role_permission_str(self):
        """RolePermission string representation."""
        rp = RolePermission.objects.create(role=self.role, permission=self.perm)
        
        self.assertIn('Test Role', str(rp))
        self.assertIn('test.view', str(rp))
    
    def test_unique_together(self):
        """Should not allow duplicate role-permission combinations."""
        RolePermission.objects.create(role=self.role, permission=self.perm)
        
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            RolePermission.objects.create(role=self.role, permission=self.perm)
