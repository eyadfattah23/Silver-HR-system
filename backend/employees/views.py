#!/usr/bin/env python3
"""
Custom views for Employee management.

Permission Structure:
- Normal employees: Can only view their own profile and change their password (via Djoser)
- Admins: Full CRUD access to all employees via API
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model

from .serializers import (
    EmployeeSerializer,
    EmployeeListSerializer,
    EmployeeCreateSerializer,
    EmployeeAdminUpdateSerializer,
)

Employee = get_user_model()


# =============================================================================
# Employee Self-Service Views (Read-only, password change via Djoser)
# =============================================================================

class EmployeeMeView(generics.RetrieveAPIView):
    """
    GET: Retrieve current employee's own profile (read-only).

    Employees cannot update their own data - only admins can.
    Password change is handled via Djoser: POST /api/v1/auth/users/set_password/
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EmployeeSerializer

    def get_object(self):
        return self.request.user


# =============================================================================
# Admin Dashboard API Views
# =============================================================================

class EmployeeListCreateView(generics.ListCreateAPIView):
    """
    Admin-only view.

    GET: List all employees
    POST: Create a new employee
    """
    queryset = Employee.objects.all().order_by('-created_at')
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EmployeeCreateSerializer
        return EmployeeListSerializer


class EmployeeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Admin-only view for managing individual employees.

    GET: Retrieve employee details
    PUT/PATCH: Update employee data
    DELETE: Deactivate employee (soft delete by setting is_active=False)
    """
    queryset = Employee.objects.all()
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return EmployeeAdminUpdateSerializer
        return EmployeeSerializer

    def destroy(self, request, *args, **kwargs):
        """Soft delete - deactivate the employee instead of deleting."""
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=['is_active'])
        return Response(
            {"detail": "Employee deactivated successfully."},
            status=status.HTTP_200_OK
        )


class EmployeeActivateView(APIView):
    """
    Admin-only view to reactivate a deactivated employee.

    POST: Activate employee
    """
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        try:
            employee = Employee.objects.get(pk=pk)
        except Employee.DoesNotExist:
            return Response(
                {"detail": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        employee.is_active = True
        employee.save(update_fields=['is_active'])
        return Response(
            {"detail": "Employee activated successfully."},
            status=status.HTTP_200_OK
        )


class EmployeeSetPasswordView(APIView):
    """
    Admin-only view to reset an employee's password.

    POST: Set new password for employee
    Body: {"new_password": "...", "re_new_password": "..."}
    """
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        try:
            employee = Employee.objects.get(pk=pk)
        except Employee.DoesNotExist:
            return Response(
                {"detail": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        new_password = request.data.get('new_password')
        re_new_password = request.data.get('re_new_password')

        if not new_password:
            return Response(
                {"new_password": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        if new_password != re_new_password:
            return Response(
                {"re_new_password": ["Passwords do not match."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        employee.set_password(new_password)
        employee.save(update_fields=['password'])

        return Response(
            {"detail": "Password updated successfully."},
            status=status.HTTP_200_OK
        )
