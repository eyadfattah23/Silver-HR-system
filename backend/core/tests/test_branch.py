#!/usr/bin/env python3
"""Tests for Branch API endpoints."""

from django.test import TestCase
from rest_framework import status
import uuid

from .base import BaseTestCase
from ..models import City, Branch


class BranchListTests(BaseTestCase):
    """Tests for Branch listing."""

    def test_superuser_can_list_branches(self):
        """Test superuser can list all branches."""
        self.authenticate_as_superuser()

        response = self.client.get('/api/v1/core/branches/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)  # All branches

    def test_superuser_can_list_active_branches(self):
        """Test superuser can list only active branches."""
        self.authenticate_as_superuser()

        response = self.client.get('/api/v1/core/branches/active/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # Only active branches

    def test_admin_cannot_list_branches(self):
        """Test admin (non-superuser) cannot list branches."""
        self.authenticate_as_admin()

        response = self.client.get('/api/v1/core/branches/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_employee_cannot_list_branches(self):
        """Test regular employee cannot list branches."""
        self.authenticate_as_employee()

        response = self.client.get('/api/v1/core/branches/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_list_branches(self):
        """Test unauthenticated request cannot list branches."""
        response = self.client.get('/api/v1/core/branches/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BranchCreateTests(BaseTestCase):
    """Tests for Branch creation."""

    def test_superuser_can_create_branch(self):
        """Test superuser can create a new branch."""
        self.authenticate_as_superuser()

        response = self.client.post('/api/v1/core/branches/', {
            'name': 'New Branch',
            'description': 'A new branch',
            'city': str(self.city1.id),
            'is_active': True,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Branch')

    def test_superuser_can_create_branch_with_location(self):
        """Test superuser can create branch with location URL."""
        self.authenticate_as_superuser()

        response = self.client.post('/api/v1/core/branches/', {
            'name': 'Branch With Location',
            'city': str(self.city1.id),
            'location': 'https://maps.google.com/example',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['location'], 'https://maps.google.com/example')

    def test_cannot_create_duplicate_branch_name_in_same_city(self):
        """Test cannot create branch with duplicate name in same city."""
        self.authenticate_as_superuser()

        response = self.client.post('/api/v1/core/branches/', {
            'name': 'Main Branch',  # Already exists in city1
            'city': str(self.city1.id),
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_create_same_branch_name_in_different_city(self):
        """Test can create branch with same name in different city."""
        self.authenticate_as_superuser()

        response = self.client.post('/api/v1/core/branches/', {
            'name': 'Main Branch',  # Exists in city1, but creating in city2
            'city': str(self.city2.id),
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_cannot_create_branch_in_inactive_city(self):
        """Test cannot create branch in an inactive city."""
        self.authenticate_as_superuser()

        response = self.client.post('/api/v1/core/branches/', {
            'name': 'Branch in Inactive City',
            'city': str(self.inactive_city.id),
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_cannot_create_branch(self):
        """Test admin (non-superuser) cannot create branches."""
        self.authenticate_as_admin()

        response = self.client.post('/api/v1/core/branches/', {
            'name': 'New Branch',
            'city': str(self.city1.id),
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class BranchDetailTests(BaseTestCase):
    """Tests for Branch detail view."""

    def test_superuser_can_view_branch(self):
        """Test superuser can view branch details."""
        self.authenticate_as_superuser()

        response = self.client.get(f'/api/v1/core/branches/{self.branch1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Main Branch')
        self.assertIn('city_detail', response.data)
        self.assertIn('department_count', response.data)

    def test_superuser_can_update_branch(self):
        """Test superuser can update branch."""
        self.authenticate_as_superuser()

        response = self.client.patch(f'/api/v1/core/branches/{self.branch1.id}/', {
            'description': 'Updated description',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Updated description')

    def test_superuser_can_change_branch_city(self):
        """Test superuser can change branch to different city."""
        self.authenticate_as_superuser()

        response = self.client.patch(f'/api/v1/core/branches/{self.branch2.id}/', {
            'city': str(self.city2.id),
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_superuser_can_deactivate_branch(self):
        """Test superuser can deactivate (soft delete) branch."""
        self.authenticate_as_superuser()

        response = self.client.delete(f'/api/v1/core/branches/{self.branch1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify branch is deactivated, not deleted
        self.branch1.refresh_from_db()
        self.assertFalse(self.branch1.is_active)

    def test_view_nonexistent_branch(self):
        """Test viewing non-existent branch returns 404."""
        self.authenticate_as_superuser()

        fake_uuid = uuid.uuid4()
        response = self.client.get(f'/api/v1/core/branches/{fake_uuid}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_cannot_update_branch(self):
        """Test admin (non-superuser) cannot update branches."""
        self.authenticate_as_admin()

        response = self.client.patch(f'/api/v1/core/branches/{self.branch1.id}/', {
            'name': 'Hacked',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class BranchModelTests(TestCase):
    """Tests for Branch model."""

    @classmethod
    def setUpTestData(cls):
        """Create test city."""
        cls.city = City.objects.create(
            name='Test City',
            code='TC'
        )

    def test_branch_str_representation(self):
        """Test string representation of Branch."""
        branch = Branch.objects.create(
            name='Test Branch',
            city=self.city
        )
        self.assertEqual(str(branch), 'Test Branch - Test City')

    def test_branch_default_is_active(self):
        """Test Branch defaults to is_active=True."""
        branch = Branch.objects.create(
            name='Active Branch',
            city=self.city
        )
        self.assertTrue(branch.is_active)
