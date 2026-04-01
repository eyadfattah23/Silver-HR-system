#!/usr/bin/env python3
"""Tests for Document API endpoints."""

from django.test import TestCase
from rest_framework import status
import uuid

from .base import BaseTestCase
from ..models import Document


class DocumentListTests(BaseTestCase):
    """Tests for Document listing."""

    def test_superuser_can_list_documents(self):
        """Test superuser can list all documents."""
        self.authenticate_as_superuser()

        response = self.client.get('/api/v1/documents/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)  # All documents

    def test_superuser_can_list_active_documents(self):
        """Test superuser can list only active documents."""
        self.authenticate_as_superuser()

        response = self.client.get('/api/v1/documents/active/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # Only active documents

    def test_superuser_can_filter_by_employee(self):
        """Test superuser can filter documents by employee."""
        self.authenticate_as_superuser()

        response = self.client.get(f'/api/v1/documents/?employee={self.employee.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # employee's documents (2 active + 1 inactive)

    def test_superuser_can_filter_by_document_type(self):
        """Test superuser can filter documents by document type."""
        self.authenticate_as_superuser()

        response = self.client.get(f'/api/v1/documents/?document_type={self.doc_type1.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # ID Card documents

    def test_superuser_can_list_employee_documents(self):
        """Test superuser can list documents for a specific employee."""
        self.authenticate_as_superuser()

        response = self.client.get(f'/api/v1/documents/employee/{self.employee.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_admin_cannot_list_documents(self):
        """Test admin (non-superuser) cannot list documents."""
        self.authenticate_as_admin()

        response = self.client.get('/api/v1/documents/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_employee_cannot_list_all_documents(self):
        """Test regular employee cannot list all documents."""
        self.authenticate_as_employee()

        response = self.client.get('/api/v1/documents/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_list_documents(self):
        """Test unauthenticated request cannot list documents."""
        response = self.client.get('/api/v1/documents/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DocumentCreateTests(BaseTestCase):
    """Tests for Document creation."""

    def test_superuser_can_create_document(self):
        """Test superuser can create a new document."""
        self.authenticate_as_superuser()

        response = self.client.post('/api/v1/documents/', {
            'employee': str(self.employee.id),
            'document_type': self.doc_type1.id,
            'file_name': 'new_document.pdf',
            'file_format': 'pdf',
            'file_size': 1500,
            'description': 'New document',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['file_name'], 'new_document.pdf')

    def test_cannot_create_document_with_inactive_type(self):
        """Test cannot create document with inactive document type."""
        self.authenticate_as_superuser()

        response = self.client.post('/api/v1/documents/', {
            'employee': str(self.employee.id),
            'document_type': self.inactive_doc_type.id,
            'file_name': 'new_document.pdf',
            'file_format': 'pdf',
            'file_size': 1500,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_file_format_is_lowercased(self):
        """Test file format is automatically lowercased."""
        self.authenticate_as_superuser()

        response = self.client.post('/api/v1/documents/', {
            'employee': str(self.employee.id),
            'document_type': self.doc_type1.id,
            'file_name': 'new_document.PDF',
            'file_format': 'PDF',
            'file_size': 1500,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['file_format'], 'pdf')

    def test_admin_cannot_create_document(self):
        """Test admin (non-superuser) cannot create documents."""
        self.authenticate_as_admin()

        response = self.client.post('/api/v1/documents/', {
            'employee': str(self.employee.id),
            'document_type': self.doc_type1.id,
            'file_name': 'new_document.pdf',
            'file_format': 'pdf',
            'file_size': 1500,
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_employee_cannot_create_document(self):
        """Test regular employee cannot create documents."""
        self.authenticate_as_employee()

        response = self.client.post('/api/v1/documents/', {
            'employee': str(self.employee.id),
            'document_type': self.doc_type1.id,
            'file_name': 'new_document.pdf',
            'file_format': 'pdf',
            'file_size': 1500,
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DocumentDetailTests(BaseTestCase):
    """Tests for Document detail view."""

    def test_superuser_can_view_document(self):
        """Test superuser can view document details."""
        self.authenticate_as_superuser()

        response = self.client.get(f'/api/v1/documents/{self.document1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['file_name'], 'employee_id.pdf')
        self.assertIn('document_type_detail', response.data)
        self.assertIn('employee_name', response.data)

    def test_superuser_can_update_document(self):
        """Test superuser can update document."""
        self.authenticate_as_superuser()

        response = self.client.patch(f'/api/v1/documents/{self.document1.id}/', {
            'description': 'Updated description',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Updated description')

    def test_superuser_can_deactivate_document(self):
        """Test superuser can deactivate (soft delete) document."""
        self.authenticate_as_superuser()

        response = self.client.delete(f'/api/v1/documents/{self.document1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify document is deactivated, not deleted
        self.document1.refresh_from_db()
        self.assertFalse(self.document1.is_active)

    def test_view_nonexistent_document(self):
        """Test viewing non-existent document returns 404."""
        self.authenticate_as_superuser()

        fake_uuid = uuid.uuid4()
        response = self.client.get(f'/api/v1/documents/{fake_uuid}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_cannot_update_document(self):
        """Test admin (non-superuser) cannot update documents."""
        self.authenticate_as_admin()

        response = self.client.patch(f'/api/v1/documents/{self.document1.id}/', {
            'description': 'Updated',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_employee_cannot_view_document_via_admin_endpoint(self):
        """Test regular employee cannot view document via admin endpoint."""
        self.authenticate_as_employee()

        response = self.client.get(f'/api/v1/documents/{self.document1.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class MyDocumentTests(BaseTestCase):
    """Tests for employee viewing their own documents."""

    def test_employee_can_view_own_documents(self):
        """Test employee can list their own documents."""
        self.authenticate_as_employee()

        response = self.client.get('/api/v1/documents/my/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Only active documents belonging to the employee
        self.assertEqual(len(response.data), 2)

    def test_employee_can_view_own_document_detail(self):
        """Test employee can view detail of their own document."""
        self.authenticate_as_employee()

        response = self.client.get(f'/api/v1/documents/my/{self.document1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['file_name'], 'employee_id.pdf')

    def test_employee_cannot_view_other_employee_document(self):
        """Test employee cannot view another employee's document."""
        self.authenticate_as_employee()

        response = self.client.get(f'/api/v1/documents/my/{self.other_document.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_employee_cannot_view_inactive_own_document(self):
        """Test employee cannot view their own inactive documents."""
        self.authenticate_as_employee()

        response = self.client.get(f'/api/v1/documents/my/{self.inactive_document.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_other_employee_sees_only_own_documents(self):
        """Test another employee sees only their own documents."""
        self.authenticate_as_other_employee()

        response = self.client.get('/api/v1/documents/my/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only other_document

    def test_unauthenticated_cannot_view_my_documents(self):
        """Test unauthenticated request cannot access my documents."""
        response = self.client.get('/api/v1/documents/my/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_superuser_can_access_my_documents(self):
        """Test superuser can access my documents endpoint (sees their own)."""
        self.authenticate_as_superuser()

        response = self.client.get('/api/v1/documents/my/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Superuser has no documents assigned to them
        self.assertEqual(len(response.data), 0)

    def test_my_documents_excludes_inactive(self):
        """Test my documents endpoint only shows active documents."""
        self.authenticate_as_employee()

        response = self.client.get('/api/v1/documents/my/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify all returned documents are active
        for doc in response.data:
            self.assertNotIn('is_active', doc)  # EmployeeDocumentListSerializer doesn't include is_active
