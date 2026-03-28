#!/usr/bin/env python3
"""
Base test case for the core app.

Provides common setup and helper methods for all test classes.
"""

from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from datetime import date

from ..models import City, Branch, Department

Employee = get_user_model()


class BaseTestCase(APITestCase):
    """Base test case with common setup for all core tests."""

    @classmethod
    def setUpTestData(cls):
        """Create test data for all tests."""
        # Create cities
        cls.city1 = City.objects.create(
            name='Cairo',
            code='CA',
            is_active=True
        )
        cls.city2 = City.objects.create(
            name='Alexandria',
            code='AX',
            is_active=True
        )
        cls.inactive_city = City.objects.create(
            name='Inactive City',
            code='IC',
            is_active=False
        )

        # Create branches
        cls.branch1 = Branch.objects.create(
            name='Main Branch',
            description='Main Cairo branch',
            city=cls.city1,
            is_active=True
        )
        cls.branch2 = Branch.objects.create(
            name='Secondary Branch',
            description='Secondary branch',
            city=cls.city1,
            is_active=True
        )
        cls.alex_branch = Branch.objects.create(
            name='Alexandria Main',
            city=cls.city2,
            is_active=True
        )
        cls.inactive_branch = Branch.objects.create(
            name='Inactive Branch',
            city=cls.city1,
            is_active=False
        )

        # Create departments
        cls.department1 = Department.objects.create(
            name='IT Department',
            code='IT',
            description='Information Technology',
            branch=cls.branch1,
            is_active=True
        )
        cls.department2 = Department.objects.create(
            name='HR Department',
            code='HR',
            description='Human Resources',
            branch=cls.branch1,
            is_active=True
        )
        cls.inactive_department = Department.objects.create(
            name='Inactive Department',
            code='ID',
            branch=cls.branch1,
            is_active=False
        )

    def setUp(self):
        """Create test users - a superuser, admin, and regular employee."""
        # Superuser (can manage cities, branches, departments)
        self.superuser = Employee.objects.create_user(
            phone_number1='+201000000001',
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
            phone_number1='+201000000002',
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
            phone_number1='+201000000003',
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
        tokens = self.get_tokens('+201000000001', 'SuperPass123!')
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {tokens["access"]}')

    def authenticate_as_admin(self):
        """Authenticate client as admin (staff but not superuser)."""
        tokens = self.get_tokens('+201000000002', 'AdminPass123!')
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {tokens["access"]}')

    def authenticate_as_employee(self):
        """Authenticate client as regular employee."""
        tokens = self.get_tokens('+201000000003', 'EmployeePass123!')
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {tokens["access"]}')
