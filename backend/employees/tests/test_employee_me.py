#!/usr/bin/env python3
"""Tests for employee self-service endpoints (/me/, password change)."""

from rest_framework import status

from .base import BaseTestCase


class EmployeeMeViewTests(BaseTestCase):
    """Tests for the /employees/me/ endpoint."""

    def test_get_own_profile_authenticated(self):
        """Test authenticated employee can view their own profile."""
        self.authenticate_as_employee()

        response = self.client.get('/api/v1/employees/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone_number1'], '+201000000002')
        self.assertEqual(response.data['first_name'], 'فاطمة')
        self.assertEqual(response.data['fourth_name'], 'سعيد')

    def test_get_own_profile_unauthenticated(self):
        """Test unauthenticated request is rejected."""
        response = self.client.get('/api/v1/employees/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_update_own_profile(self):
        """Test employee cannot update their own profile via /me/ endpoint."""
        self.authenticate_as_employee()

        # PUT should not be allowed (RetrieveAPIView only)
        response = self.client.put('/api/v1/employees/me/', {
            'first_name': 'Hacked',
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # PATCH should not be allowed
        response = self.client.patch('/api/v1/employees/me/', {
            'first_name': 'Hacked',
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class EmployeePasswordChangeTests(BaseTestCase):
    """Tests for employee password change via Djoser."""

    def test_employee_can_change_own_password(self):
        """Test employee can change their own password."""
        self.authenticate_as_employee()

        response = self.client.post('/api/v1/auth/users/set_password/', {
            'current_password': 'EmployeePass123!',
            'new_password': 'NewSecurePass456!',
            're_new_password': 'NewSecurePass456!',
        })
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify can login with new password
        self.client.credentials()  # Clear auth
        tokens = self.get_tokens('+201000000002', 'NewSecurePass456!')
        self.assertIn('access', tokens)

    def test_password_change_wrong_current_password(self):
        """Test password change fails with wrong current password."""
        self.authenticate_as_employee()

        response = self.client.post('/api/v1/auth/users/set_password/', {
            'current_password': 'WrongPassword!',
            'new_password': 'NewSecurePass456!',
            're_new_password': 'NewSecurePass456!',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_change_mismatched_passwords(self):
        """Test password change fails when new passwords don't match."""
        self.authenticate_as_employee()

        response = self.client.post('/api/v1/auth/users/set_password/', {
            'current_password': 'EmployeePass123!',
            'new_password': 'NewSecurePass456!',
            're_new_password': 'DifferentPass789!',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
