#!/usr/bin/env python3
"""Helper functions for permission tests."""
from datetime import date
from django.contrib.auth import get_user_model

Employee = get_user_model()


def create_test_superuser(phone_suffix='01'):
    """Helper to create a test superuser with all required fields."""
    return Employee.objects.create_superuser(
        phone_number1=f'+20100000{phone_suffix}',
        password='testpass123',
        first_name='Admin',
        second_name='Test',
        third_name='User',
        fourth_name='Super',
        date_of_birth=date(1990, 1, 1),
        gender='male',
        military_status='completed',
        hire_date=date(2020, 1, 1),
    )


def create_test_user(phone_suffix='02', first_name='Regular'):
    """Helper to create a regular test user with all required fields."""
    return Employee.objects.create_user(
        phone_number1=f'+20100000{phone_suffix}',
        password='testpass123',
        first_name=first_name,
        second_name='Test',
        third_name='User',
        fourth_name='Normal',
        date_of_birth=date(1995, 5, 15),
        gender='female',
        military_status='not_applicable',
        hire_date=date(2021, 6, 1),
    )
