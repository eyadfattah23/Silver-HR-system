#!/usr/bin/env python3
"""
Custom views for Employee management.

Permission Structure:
- Normal employees: Can view their own profile (employees.view_own)
- Users with employees.view: Can view employees (within their scope)
- Users with employees.create: Can create employees
- Users with employees.update: Can update employees (within their scope)
- Users with employees.delete: Can deactivate employees (within their scope)
- Superusers: Full access
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model

from permissions.utils import has_permission

from ..serializers import (
    EmployeeSerializer,
    EmployeeListSerializer,
    EmployeeCreateSerializer,
    EmployeeAdminUpdateSerializer,
)

Employee = get_user_model()


class HasEmployeePermission(permissions.BasePermission):
    """
    Permission class for employee endpoints.
    Maps HTTP methods to permission codes.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        # Map methods to permissions
        method_permission_map = {
            'GET': 'employees.view',
            'POST': 'employees.create',
            'PUT': 'employees.update',
            'PATCH': 'employees.update',
            'DELETE': 'employees.delete',
        }
        
        required_permission = method_permission_map.get(request.method)
        if not required_permission:
            return False
        
        return has_permission(request.user, required_permission)


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
    View for listing and creating employees.

    GET: List employees (requires employees.view)
    POST: Create a new employee (requires employees.create)
    """
    queryset = Employee.objects.all().order_by('-created_at')
    permission_classes = [HasEmployeePermission]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EmployeeCreateSerializer
        return EmployeeListSerializer

    def perform_create(self, serializer):
        """Set created_by to current user."""
        serializer.save(created_by=self.request.user)


class EmployeeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for managing individual employees.

    GET: Retrieve employee details (requires employees.view)
    PUT/PATCH: Update employee data (requires employees.update)
    DELETE: Deactivate employee (requires employees.delete)
    """
    queryset = Employee.objects.all()
    permission_classes = [HasEmployeePermission]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return EmployeeAdminUpdateSerializer
        return EmployeeSerializer

    def destroy(self, request, *args, **kwargs):
        """Soft delete - deactivate the employee instead of deleting."""
        instance = self.get_object()
        instance.is_active = False
        instance.updated_by = request.user
        instance.save(update_fields=['is_active', 'updated_by'])
        return Response(
            {"detail": "Employee deactivated successfully."},
            status=status.HTTP_200_OK
        )


class EmployeeActivateView(APIView):
    """
    View to reactivate a deactivated employee.

    POST: Activate employee (requires employees.update)
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        # Check permission
        if not request.user.is_superuser and not has_permission(request.user, 'employees.update'):
            return Response(
                {"detail": "You do not have permission to activate employees."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            employee = Employee.objects.get(pk=pk)
        except Employee.DoesNotExist:
            return Response(
                {"detail": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        employee.is_active = True
        employee.updated_by = request.user
        employee.save(update_fields=['is_active', 'updated_by'])
        return Response(
            {"detail": "Employee activated successfully."},
            status=status.HTTP_200_OK
        )


class EmployeeSetPasswordView(APIView):
    """
    View to reset an employee's password.

    POST: Set new password for employee (requires employees.update)
    Body: {"new_password": "...", "re_new_password": "..."}
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        # Check permission
        if not request.user.is_superuser and not has_permission(request.user, 'employees.update'):
            return Response(
                {"detail": "You do not have permission to reset employee passwords."},
                status=status.HTTP_403_FORBIDDEN
            )
        
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
        employee.updated_by = request.user
        employee.save(update_fields=['password', 'updated_by'])

        return Response(
            {"detail": "Password updated successfully."},
            status=status.HTTP_200_OK
        )
