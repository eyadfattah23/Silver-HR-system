#!/usr/bin/env python3
"""Tests for DocumentType API endpoints."""

from django.test import TestCase
from rest_framework import status

from .base import BaseTestCase
from ..models import DocumentType


class DocumentTypeListTests(BaseTestCase):
    """Tests for DocumentType listing."""

    def test_superuser_can_list_document_types(self):
        """Test superuser can list all document types."""
        self.authenticate_as_superuser()

        response = self.client.get('/api/v1/documents/types/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # 2 active + 1 inactive

    def test_superuser_can_list_active_document_types(self):
        """Test superuser can list only active document types."""
        self.authenticate_as_superuser()

        response = self.client.get('/api/v1/documents/types/active/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Only active types

    def test_admin_cannot_list_document_types(self):
        """Test admin (non-superuser) cannot list document types."""
        self.authenticate_as_admin()

        response = self.client.get('/api/v1/documents/types/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_employee_cannot_list_document_types(self):
        """Test regular employee cannot list document types."""
        self.authenticate_as_employee()

        response = self.client.get('/api/v1/documents/types/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_list_document_types(self):
        """Test unauthenticated request cannot list document types."""
        response = self.client.get('/api/v1/documents/types/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DocumentTypeCreateTests(BaseTestCase):
    """Tests for DocumentType creation."""

    def test_superuser_can_create_document_type(self):
        """Test superuser can create a new document type."""
        self.authenticate_as_superuser()

        response = self.client.post('/api/v1/documents/types/', {
            'name': 'Driver License',
            'description': 'Driver License document',
            'is_active': True,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Driver License')

    def test_cannot_create_duplicate_document_type_name(self):
        """Test cannot create document type with duplicate name."""
        self.authenticate_as_superuser()

        response = self.client.post('/api/v1/documents/types/', {
            'name': 'ID Card',  # Already exists
            'description': 'Duplicate',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_create_duplicate_name_case_insensitive(self):
        """Test name uniqueness is case-insensitive."""
        self.authenticate_as_superuser()

        response = self.client.post('/api/v1/documents/types/', {
            'name': 'id card',  # Different case
            'description': 'Duplicate',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_cannot_create_document_type(self):
        """Test admin (non-superuser) cannot create document types."""
        self.authenticate_as_admin()

        response = self.client.post('/api/v1/documents/types/', {
            'name': 'Driver License',
            'description': 'Driver License document',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DocumentTypeDetailTests(BaseTestCase):
    """Tests for DocumentType detail view."""

    def test_superuser_can_view_document_type(self):
        """Test superuser can view document type details."""
        self.authenticate_as_superuser()

        response = self.client.get(f'/api/v1/documents/types/{self.doc_type1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'ID Card')
        self.assertIn('document_count', response.data)

    def test_superuser_can_update_document_type(self):
        """Test superuser can update document type."""
        self.authenticate_as_superuser()

        response = self.client.patch(f'/api/v1/documents/types/{self.doc_type1.id}/', {
            'name': 'National ID Card',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'National ID Card')

    def test_superuser_can_deactivate_document_type(self):
        """Test superuser can deactivate (soft delete) document type."""
        self.authenticate_as_superuser()

        response = self.client.delete(f'/api/v1/documents/types/{self.doc_type1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify document type is deactivated, not deleted
        self.doc_type1.refresh_from_db()
        self.assertFalse(self.doc_type1.is_active)

    def test_view_nonexistent_document_type(self):
        """Test viewing non-existent document type returns 404."""
        self.authenticate_as_superuser()

        response = self.client.get('/api/v1/documents/types/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_cannot_update_document_type(self):
        """Test admin (non-superuser) cannot update document types."""
        self.authenticate_as_admin()

        response = self.client.patch(f'/api/v1/documents/types/{self.doc_type1.id}/', {
            'name': 'Updated Name',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_employee_cannot_view_document_type(self):
        """Test regular employee cannot view document type details."""
        self.authenticate_as_employee()

        response = self.client.get(f'/api/v1/documents/types/{self.doc_type1.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
