#!/usr/bin/env python3
"""Tests for Employee and JobTitle model validations."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date

from ..models import (
    JobTitle,
    Gender,
    MilitaryStatus,
    EmploymentState,
)

Employee = get_user_model()


class EmployeeModelTests(TestCase):
    """Tests for Employee model validations."""

    @classmethod
    def setUpTestData(cls):
        """Create JobTitle for tests."""
        cls.job_title = JobTitle.objects.create(
            name='Test Job',
            is_active=True
        )

    def test_nid_extracts_dob_and_gender_male(self):
        """Test DOB and gender are auto-extracted from Egyptian NID (male)."""
        employee = Employee.objects.create_user(
            phone_number1='+201012345678',
            password='TestPass123!',
            first_name='اختبار',
            second_name='الرقم',
            third_name='القومي',
            fourth_name='ذكر',
            hire_date=date(2024, 1, 1),
            military_status=MilitaryStatus.COMPLETED,
            # Male (13th digit=1 is odd), born Jan 15, 1995
            national_id='29501151234517',
        )

        self.assertEqual(employee.date_of_birth, date(1995, 1, 15))
        self.assertEqual(employee.gender, Gender.MALE)

    def test_nid_extracts_dob_and_gender_female(self):
        """Test DOB and gender are auto-extracted from Egyptian NID (female)."""
        employee = Employee.objects.create_user(
            phone_number1='+201123456789',
            password='TestPass123!',
            first_name='اختبار',
            second_name='الرقم',
            third_name='القومي',
            fourth_name='أنثى',
            hire_date=date(2024, 1, 1),
            military_status=MilitaryStatus.NOT_APPLICABLE,
            national_id='29501151234528',  # Female (13th digit=2 is even)
        )

        self.assertEqual(employee.date_of_birth, date(1995, 1, 15))
        self.assertEqual(employee.gender, Gender.FEMALE)

    def test_full_name_property(self):
        """Test full_name property returns all four name parts."""
        employee = Employee.objects.create_user(
            phone_number1='+201234567893',
            password='TestPass123!',
            first_name='أحمد',
            second_name='محمد',
            third_name='علي',
            fourth_name='حسن',
            date_of_birth=date(1990, 1, 1),
            gender=Gender.MALE,
            military_status=MilitaryStatus.COMPLETED,
            hire_date=date(2024, 1, 1),
        )

        self.assertEqual(employee.full_name, 'أحمد محمد علي حسن')

    def test_multiple_employees_without_national_id(self):
        """Test multiple employees can have no national_id (NULL)."""
        Employee.objects.create_user(
            phone_number1='+201111111112',
            password='TestPass123!',
            first_name='بدون',
            second_name='رقم',
            third_name='قومي',
            fourth_name='أول',
            date_of_birth=date(1990, 1, 1),
            gender=Gender.MALE,
            military_status=MilitaryStatus.COMPLETED,
            hire_date=date(2024, 1, 1),
        )

        # Should not raise unique constraint error
        Employee.objects.create_user(
            phone_number1='+201111111113',
            password='TestPass123!',
            first_name='بدون',
            second_name='رقم',
            third_name='قومي',
            fourth_name='ثاني',
            date_of_birth=date(1990, 1, 1),
            gender=Gender.MALE,
            military_status=MilitaryStatus.COMPLETED,
            hire_date=date(2024, 1, 1),
        )

    def test_employment_state_choices(self):
        """Test employment state field accepts valid choices."""
        employee = Employee.objects.create_user(
            phone_number1='+201222222224',
            password='TestPass123!',
            first_name='حالة',
            second_name='العمل',
            third_name='اختبار',
            fourth_name='موظف',
            date_of_birth=date(1990, 1, 1),
            gender=Gender.MALE,
            military_status=MilitaryStatus.COMPLETED,
            hire_date=date(2024, 1, 1),
            employment_state=EmploymentState.SUSPENDED,
        )

        self.assertEqual(employee.employment_state, EmploymentState.SUSPENDED)


class JobTitleModelTests(TestCase):
    """Tests for JobTitle model."""

    def test_job_title_str_representation(self):
        """Test string representation of JobTitle."""
        job_title = JobTitle.objects.create(
            name='مهندس برمجيات',
            description='يطور تطبيقات البرمجيات'
        )
        self.assertEqual(str(job_title), 'مهندس برمجيات')

    def test_job_title_default_is_active(self):
        """Test JobTitle defaults to is_active=True."""
        job_title = JobTitle.objects.create(name='وظيفة جديدة')
        self.assertTrue(job_title.is_active)
