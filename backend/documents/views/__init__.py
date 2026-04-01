#!/usr/bin/env python3
"""Views for documents app."""

from .document_type import (
    DocumentTypeListCreateView,
    DocumentTypeDetailView,
    ActiveDocumentTypeListView,
)
from .document import (
    DocumentListCreateView,
    DocumentDetailView,
    EmployeeDocumentListView,
    EmployeeDocumentDetailView,
    ActiveDocumentListView,
    EmployeeDocumentsView,
)

__all__ = [
    'DocumentTypeListCreateView',
    'DocumentTypeDetailView',
    'ActiveDocumentTypeListView',
    'DocumentListCreateView',
    'DocumentDetailView',
    'EmployeeDocumentListView',
    'EmployeeDocumentDetailView',
    'ActiveDocumentListView',
    'EmployeeDocumentsView',
]
