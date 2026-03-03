#!/usr/bin/env python3
"""URL routes for Employee API endpoints."""

from django.urls import path
from .views import (
    # Employee views
    EmployeeMeView,
    EmployeeListCreateView,
    EmployeeDetailView,
    EmployeeActivateView,
    EmployeeSetPasswordView,
    # JobTitle views
    JobTitleListCreateView,
    JobTitleDetailView,
    ActiveJobTitleListView,
)

app_name = 'employees'

urlpatterns = [
    # ==========================================================================
    # Employee Self-Service (authenticated employees)
    # ==========================================================================
    # GET own profile (read-only)
    path('me/', EmployeeMeView.as_view(), name='employee-me'),

    # ==========================================================================
    # Admin Dashboard API - Employees (admin only)
    # ==========================================================================
    # List all employees / Create new employee
    path('', EmployeeListCreateView.as_view(), name='employee-list-create'),

    # Get / Update / Delete (deactivate) specific employee
    path('<uuid:pk>/', EmployeeDetailView.as_view(), name='employee-detail'),

    # Activate a deactivated employee
    path('<uuid:pk>/activate/', EmployeeActivateView.as_view(),
         name='employee-activate'),

    # Admin reset employee password
    path('<uuid:pk>/set-password/', EmployeeSetPasswordView.as_view(),
         name='employee-set-password'),

    # ==========================================================================
    # Admin Dashboard API - Job Titles (admin only)
    # ==========================================================================
    # List all job titles / Create new job title
    path('job-titles/', JobTitleListCreateView.as_view(), name='job-title-list-create'),

    # Get / Update / Delete specific job title
    path('job-titles/<uuid:pk>/', JobTitleDetailView.as_view(), name='job-title-detail'),

    # List active job titles (for dropdowns, authenticated users)
    path('job-titles/active/', ActiveJobTitleListView.as_view(), name='job-title-active-list'),
]
