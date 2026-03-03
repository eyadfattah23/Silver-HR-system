#!/usr/bin/env python3
"""
Base test case for the employees app.

Provides common setup and helper methods for all test classes.
"""

from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from datetime import date

from ..models import JobTitle, Gender, MilitaryStatus

Employee = get_user_model()


class BaseTestCase(APITestCase):
    """Base test case with common setup for all tests."""

    @classmethod
    def setUpTestData(cls):
        """Create JobTitle for use across tests."""
        cls.job_title = JobTitle.objects.create(
            name='Software Engineer',
            description='Develops software applications',
            is_active=True
        )
        cls.job_title2 = JobTitle.objects.create(
            name='Manager',
            description='Manages team',
            is_active=True
        )

    def setUp(self):
        """Create test users - an admin and a regular employee."""
        # Admin user
        self.admin = Employee.objects.create_user(
            phone_number1='+201000000001',
            password='AdminPass123!',
            first_name='أحمد',
            second_name='محمد',
            third_name='علي',
            fourth_name='حسن',
            date_of_birth=date(1990, 1, 1),
            gender=Gender.MALE,
            military_status=MilitaryStatus.COMPLETED,
            hire_date=date(2024, 1, 1),
            national_id='29001011234567',
            is_staff=True,
            is_superuser=True,
        )

        # Regular employee
        self.employee = Employee.objects.create_user(
            phone_number1='+201000000002',
            password='EmployeePass123!',
            first_name='فاطمة',
            second_name='أحمد',
            third_name='محمود',
            fourth_name='سعيد',
            date_of_birth=date(1995, 6, 15),
            gender=Gender.FEMALE,
            military_status=MilitaryStatus.NOT_APPLICABLE,
            hire_date=date(2024, 6, 1),
            national_id='29506151234528',
            job_title=self.job_title,
            is_staff=False,
        )

        # Another employee for testing
        self.employee2 = Employee.objects.create_user(
            phone_number1='+201000000003',
            password='Employee2Pass123!',
            first_name='محمود',
            second_name='حسين',
            third_name='إبراهيم',
            fourth_name='خالد',
            date_of_birth=date(2000, 7, 1),
            gender=Gender.MALE,
            military_status=MilitaryStatus.POSTPONED,
            hire_date=date(2024, 7, 1),
            is_staff=False,
        )

        self.client = APIClient()

    def get_tokens(self, phone_number, password):
        """Helper to get JWT tokens for a user."""
        response = self.client.post('/api/v1/auth/jwt/create/', {
            'phone_number1': phone_number,
            'password': password,
        })
        return response.data

    def authenticate_as_admin(self):
        """Authenticate client as admin user."""
        tokens = self.get_tokens('+201000000001', 'AdminPass123!')
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {tokens["access"]}')

    def authenticate_as_employee(self):
        """Authenticate client as regular employee."""
        tokens = self.get_tokens('+201000000002', 'EmployeePass123!')
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {tokens["access"]}')
