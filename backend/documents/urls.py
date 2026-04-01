#!/usr/bin/env python3
"""URL configuration for documents app."""

from django.urls import path

from .views import (
    DocumentTypeListCreateView,
    DocumentTypeDetailView,
    ActiveDocumentTypeListView,
    DocumentListCreateView,
    DocumentDetailView,
    EmployeeDocumentListView,
    EmployeeDocumentDetailView,
    ActiveDocumentListView,
    EmployeeDocumentsView,
)

app_name = 'documents'

urlpatterns = [
    # Document Types - Superuser only
    path('types/', DocumentTypeListCreateView.as_view(), name='document-type-list'),
    path('types/active/', ActiveDocumentTypeListView.as_view(), name='document-type-active'),
    path('types/<int:pk>/', DocumentTypeDetailView.as_view(), name='document-type-detail'),
    
    # Documents - Superuser only
    path('', DocumentListCreateView.as_view(), name='document-list'),
    path('active/', ActiveDocumentListView.as_view(), name='document-active'),
    path('<uuid:pk>/', DocumentDetailView.as_view(), name='document-detail'),
    path('employee/<uuid:employee_id>/', EmployeeDocumentsView.as_view(), name='employee-documents'),
    
    # My Documents - Authenticated employees (view own only)
    path('my/', EmployeeDocumentListView.as_view(), name='my-document-list'),
    path('my/<uuid:pk>/', EmployeeDocumentDetailView.as_view(), name='my-document-detail'),
]
