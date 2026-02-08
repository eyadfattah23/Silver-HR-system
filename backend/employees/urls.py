#!/usr/bin/env python3
"""URL routes for Employee API endpoints."""

from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    # ==========================================================================
    # Employee Self-Service (authenticated employees)
    # ==========================================================================
    # GET own profile (read-only)
    path('me/', views.EmployeeMeView.as_view(), name='employee-me'),

    # ==========================================================================
    # Admin Dashboard API (admin only)
    # ==========================================================================
    # List all employees / Create new employee
    path('', views.EmployeeListCreateView.as_view(), name='employee-list-create'),

    # Get / Update / Delete (deactivate) specific employee
    path('<uuid:pk>/', views.EmployeeDetailView.as_view(), name='employee-detail'),

    # Activate a deactivated employee
    path('<uuid:pk>/activate/', views.EmployeeActivateView.as_view(),
         name='employee-activate'),

    # Admin reset employee password
    path('<uuid:pk>/set-password/', views.EmployeeSetPasswordView.as_view(),
         name='employee-set-password'),
]
