#!/usr/bin/env python3
"""Tests for JobTitle management endpoints."""

from rest_framework import status

from .base import BaseTestCase


class JobTitleListTests(BaseTestCase):
    """Tests for JobTitle listing."""

    def test_admin_can_list_job_titles(self):
        """Test admin can list all job titles."""
        self.authenticate_as_admin()

        response = self.client.get('/api/v1/employees/job-titles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_employee_cannot_list_job_titles(self):
        """Test regular employee cannot list job titles."""
        self.authenticate_as_employee()

        response = self.client.get('/api/v1/employees/job-titles/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class JobTitleCreateTests(BaseTestCase):
    """Tests for JobTitle creation."""

    def test_admin_can_create_job_title(self):
        """Test admin can create a new job title."""
        self.authenticate_as_admin()

        response = self.client.post('/api/v1/employees/job-titles/', {
            'name': 'Senior Developer',
            'description': 'Senior software developer',
            'is_active': True,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Senior Developer')

    def test_cannot_create_duplicate_job_title(self):
        """Test cannot create job title with duplicate name."""
        self.authenticate_as_admin()

        response = self.client.post('/api/v1/employees/job-titles/', {
            'name': 'Software Engineer',  # Already exists
            'description': 'Duplicate',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class JobTitleDetailTests(BaseTestCase):
    """Tests for JobTitle detail view."""

    def test_admin_can_view_job_title(self):
        """Test admin can view job title details."""
        self.authenticate_as_admin()

        response = self.client.get(f'/api/v1/employees/job-titles/{self.job_title.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Software Engineer')

    def test_admin_can_update_job_title(self):
        """Test admin can update job title."""
        self.authenticate_as_admin()

        response = self.client.patch(f'/api/v1/employees/job-titles/{self.job_title.id}/', {
            'description': 'Updated description',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Updated description')

    def test_admin_can_deactivate_job_title(self):
        """Test admin can deactivate job title."""
        self.authenticate_as_admin()

        response = self.client.patch(f'/api/v1/employees/job-titles/{self.job_title.id}/', {
            'is_active': False,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_active'])
