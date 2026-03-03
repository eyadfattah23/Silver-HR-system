#!/usr/bin/env python3
"""Tests for JWT authentication endpoints."""

from rest_framework import status

from .base import BaseTestCase


class AuthenticationTests(BaseTestCase):
    """Tests for JWT authentication endpoints."""

    def test_login_with_valid_credentials(self):
        """Test successful login returns JWT tokens."""
        response = self.client.post('/api/v1/auth/jwt/create/', {
            'phone_number1': '+201000000001',
            'password': 'AdminPass123!',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_with_invalid_password(self):
        """Test login with wrong password fails."""
        response = self.client.post('/api/v1/auth/jwt/create/', {
            'phone_number1': '+201000000001',
            'password': 'WrongPassword!',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_with_nonexistent_user(self):
        """Test login with non-existent phone number fails."""
        response = self.client.post('/api/v1/auth/jwt/create/', {
            'phone_number1': '+201999999999',
            'password': 'SomePassword!',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_with_inactive_user(self):
        """Test login with deactivated user fails."""
        self.employee.is_active = False
        self.employee.save()

        response = self.client.post('/api/v1/auth/jwt/create/', {
            'phone_number1': '+201000000002',
            'password': 'EmployeePass123!',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        """Test refreshing access token with valid refresh token."""
        tokens = self.get_tokens('+201000000001', 'AdminPass123!')

        response = self.client.post('/api/v1/auth/jwt/refresh/', {
            'refresh': tokens['refresh'],
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_token_refresh_with_invalid_token(self):
        """Test refreshing with invalid token fails."""
        response = self.client.post('/api/v1/auth/jwt/refresh/', {
            'refresh': 'invalid-token',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
