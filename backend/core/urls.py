#!/usr/bin/env python3
"""URL routes for Core API endpoints (City, Branch, Department)."""

from django.urls import path

from .views import (
    # City views
    CityListCreateView,
    CityDetailView,
    ActiveCityListView,
    # Branch views
    BranchListCreateView,
    BranchDetailView,
    ActiveBranchListView,
    # Department views
    DepartmentListCreateView,
    DepartmentDetailView,
    ActiveDepartmentListView,
)

app_name = 'core'

urlpatterns = [
    # ==========================================================================
    # Cities (superuser only)
    # ==========================================================================
    # List all cities / Create new city
    path('cities/', CityListCreateView.as_view(), name='city-list-create'),
    
    # List active cities only
    path('cities/active/', ActiveCityListView.as_view(), name='city-active-list'),
    
    # Get / Update / Delete specific city
    path('cities/<uuid:pk>/', CityDetailView.as_view(), name='city-detail'),

    # ==========================================================================
    # Branches (superuser only)
    # ==========================================================================
    # List all branches / Create new branch
    path('branches/', BranchListCreateView.as_view(), name='branch-list-create'),
    
    # List active branches only
    path('branches/active/', ActiveBranchListView.as_view(), name='branch-active-list'),
    
    # Get / Update / Delete specific branch
    path('branches/<uuid:pk>/', BranchDetailView.as_view(), name='branch-detail'),

    # ==========================================================================
    # Departments (superuser only)
    # ==========================================================================
    # List all departments / Create new department
    path('departments/', DepartmentListCreateView.as_view(), name='department-list-create'),
    
    # List active departments only
    path('departments/active/', ActiveDepartmentListView.as_view(), name='department-active-list'),
    
    # Get / Update / Delete specific department
    path('departments/<uuid:pk>/', DepartmentDetailView.as_view(), name='department-detail'),
]
