#!/usr/bin/env python3
"""
Base test case for the documents app.

Provides common setup and helper methods for all test classes.
"""

from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date, timedelta

from ..models import DocumentType, Document

Employee = get_user_model()


class BaseTestCase(APITestCase):
    """Base test case with common setup for all documents tests."""

    @classmethod
    def setUpTestData(cls):
        """Create test data for all tests."""
        # Create document types
        cls.doc_type1 = DocumentType.objects.create(
            name='ID Card',
            description='National ID Card',
            is_active=True
        )
        cls.doc_type2 = DocumentType.objects.create(
            name='Passport',
            description='International Passport',
            is_active=True
        )
        cls.inactive_doc_type = DocumentType.objects.create(
            name='Inactive Type',
            description='Inactive document type',
            is_active=False
        )

    def setUp(self):
        """Create test users and documents for each test."""
        # Superuser (can manage all documents)
        self.superuser = Employee.objects.create_user(
            phone_number1='+201100000001',
            password='SuperPass123!',
            first_name='سوبر',
            second_name='أدمن',
            third_name='المدير',
            fourth_name='العام',
            date_of_birth=date(1985, 1, 1),
            gender='male',
            military_status='completed',
            hire_date=date(2020, 1, 1),
            is_staff=True,
            is_superuser=True,
        )

        # Admin user (staff but not superuser)
        self.admin = Employee.objects.create_user(
            phone_number1='+201100000002',
            password='AdminPass123!',
            first_name='أدمن',
            second_name='محمد',
            third_name='علي',
            fourth_name='حسن',
            date_of_birth=date(1990, 1, 1),
            gender='male',
            military_status='completed',
            hire_date=date(2022, 1, 1),
            is_staff=True,
            is_superuser=False,
        )

        # Regular employee
        self.employee = Employee.objects.create_user(
            phone_number1='+201100000003',
            password='EmployeePass123!',
            first_name='موظف',
            second_name='عادي',
            third_name='محمد',
            fourth_name='سعيد',
            date_of_birth=date(1995, 6, 15),
            gender='male',
            military_status='completed',
            hire_date=date(2024, 6, 1),
            is_staff=False,
        )

        # Another employee (for testing view own restriction)
        self.other_employee = Employee.objects.create_user(
            phone_number1='+201100000004',
            password='OtherPass123!',
            first_name='موظف',
            second_name='آخر',
            third_name='أحمد',
            fourth_name='محمود',
            date_of_birth=date(1992, 3, 20),
            gender='male',
            military_status='completed',
            hire_date=date(2023, 3, 1),
            is_staff=False,
        )

        # Create documents
        self.document1 = Document.objects.create(
            employee=self.employee,
            document_type=self.doc_type1,
            file_name='employee_id.pdf',
            file_format='pdf',
            file_size=1024,
            description='Employee ID Card',
            expiration_date=date.today() + timedelta(days=365),
            uploaded_by=self.superuser,
            is_active=True,
        )

        self.document2 = Document.objects.create(
            employee=self.employee,
            document_type=self.doc_type2,
            file_name='employee_passport.pdf',
            file_format='pdf',
            file_size=2048,
            description='Employee Passport',
            expiration_date=date.today() + timedelta(days=730),
            uploaded_by=self.superuser,
            is_active=True,
        )

        self.other_document = Document.objects.create(
            employee=self.other_employee,
            document_type=self.doc_type1,
            file_name='other_id.pdf',
            file_format='pdf',
            file_size=1024,
            description='Other Employee ID Card',
            expiration_date=date.today() + timedelta(days=365),
            uploaded_by=self.superuser,
            is_active=True,
        )

        self.inactive_document = Document.objects.create(
            employee=self.employee,
            document_type=self.doc_type1,
            file_name='inactive_doc.pdf',
            file_format='pdf',
            file_size=512,
            description='Inactive Document',
            uploaded_by=self.superuser,
            is_active=False,
        )

        self.client = APIClient()

    def get_tokens(self, phone_number, password):
        """Helper to get JWT tokens for a user."""
        response = self.client.post('/api/v1/auth/jwt/create/', {
            'phone_number1': phone_number,
            'password': password,
        })
        return response.data

    def authenticate_as_superuser(self):
        """Authenticate client as superuser."""
        tokens = self.get_tokens('+201100000001', 'SuperPass123!')
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {tokens["access"]}')

    def authenticate_as_admin(self):
        """Authenticate client as admin (staff but not superuser)."""
        tokens = self.get_tokens('+201100000002', 'AdminPass123!')
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {tokens["access"]}')

    def authenticate_as_employee(self):
        """Authenticate client as regular employee."""
        tokens = self.get_tokens('+201100000003', 'EmployeePass123!')
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {tokens["access"]}')

    def authenticate_as_other_employee(self):
        """Authenticate client as another employee."""
        tokens = self.get_tokens('+201100000004', 'OtherPass123!')
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {tokens["access"]}')
