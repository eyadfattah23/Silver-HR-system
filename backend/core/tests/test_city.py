#!/usr/bin/env python3
"""Tests for City API endpoints."""

from django.test import TestCase
from rest_framework import status
import uuid

from .base import BaseTestCase
from ..models import City


class CityListTests(BaseTestCase):
    """Tests for City listing."""

    def test_superuser_can_list_cities(self):
        """Test superuser can list all cities."""
        self.authenticate_as_superuser()

        response = self.client.get('/api/v1/core/cities/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # 2 active + 1 inactive

    def test_superuser_can_list_active_cities(self):
        """Test superuser can list only active cities."""
        self.authenticate_as_superuser()

        response = self.client.get('/api/v1/core/cities/active/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Only active cities

    def test_admin_cannot_list_cities(self):
        """Test admin (non-superuser) cannot list cities."""
        self.authenticate_as_admin()

        response = self.client.get('/api/v1/core/cities/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_employee_cannot_list_cities(self):
        """Test regular employee cannot list cities."""
        self.authenticate_as_employee()

        response = self.client.get('/api/v1/core/cities/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_list_cities(self):
        """Test unauthenticated request cannot list cities."""
        response = self.client.get('/api/v1/core/cities/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CityCreateTests(BaseTestCase):
    """Tests for City creation."""

    def test_superuser_can_create_city(self):
        """Test superuser can create a new city."""
        self.authenticate_as_superuser()

        response = self.client.post('/api/v1/core/cities/', {
            'name': 'Giza',
            'code': 'GZ',
            'is_active': True,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Giza')
        self.assertEqual(response.data['code'], 'GZ')

    def test_city_code_is_uppercased(self):
        """Test city code is automatically uppercased."""
        self.authenticate_as_superuser()

        response = self.client.post('/api/v1/core/cities/', {
            'name': 'Port Said',
            'code': 'ps',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['code'], 'PS')

    def test_cannot_create_duplicate_city_name(self):
        """Test cannot create city with duplicate name."""
        self.authenticate_as_superuser()

        response = self.client.post('/api/v1/core/cities/', {
            'name': 'Cairo',  # Already exists
            'code': 'CA2',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_create_duplicate_city_code(self):
        """Test cannot create city with duplicate code."""
        self.authenticate_as_superuser()

        response = self.client.post('/api/v1/core/cities/', {
            'name': 'New Cairo',
            'code': 'CA',  # Already exists
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_cannot_create_city(self):
        """Test admin (non-superuser) cannot create cities."""
        self.authenticate_as_admin()

        response = self.client.post('/api/v1/core/cities/', {
            'name': 'Giza',
            'code': 'GZ',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CityDetailTests(BaseTestCase):
    """Tests for City detail view."""

    def test_superuser_can_view_city(self):
        """Test superuser can view city details."""
        self.authenticate_as_superuser()

        response = self.client.get(f'/api/v1/core/cities/{self.city1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Cairo')
        self.assertIn('branch_count', response.data)

    def test_superuser_can_update_city(self):
        """Test superuser can update city."""
        self.authenticate_as_superuser()

        response = self.client.patch(f'/api/v1/core/cities/{self.city1.id}/', {
            'name': 'Greater Cairo',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Greater Cairo')

    def test_superuser_can_deactivate_city(self):
        """Test superuser can deactivate (soft delete) city."""
        self.authenticate_as_superuser()

        response = self.client.delete(f'/api/v1/core/cities/{self.city1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify city is deactivated, not deleted
        self.city1.refresh_from_db()
        self.assertFalse(self.city1.is_active)

    def test_view_nonexistent_city(self):
        """Test viewing non-existent city returns 404."""
        self.authenticate_as_superuser()

        fake_uuid = uuid.uuid4()
        response = self.client.get(f'/api/v1/core/cities/{fake_uuid}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_cannot_update_city(self):
        """Test admin (non-superuser) cannot update cities."""
        self.authenticate_as_admin()

        response = self.client.patch(f'/api/v1/core/cities/{self.city1.id}/', {
            'name': 'Hacked',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CityModelTests(TestCase):
    """Tests for City model."""

    def test_city_str_representation(self):
        """Test string representation of City."""
        city = City.objects.create(
            name='Test City',
            code='TC'
        )
        self.assertEqual(str(city), 'Test City')

    def test_city_default_is_active(self):
        """Test City defaults to is_active=True."""
        city = City.objects.create(
            name='Active City',
            code='AC'
        )
        self.assertTrue(city.is_active)
