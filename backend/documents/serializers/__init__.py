#!/usr/bin/env python3
"""Serializers for documents app."""

from .document_type import (
    DocumentTypeSerializer,
    DocumentTypeListSerializer,
    DocumentTypeCreateUpdateSerializer,
)
from .document import (
    DocumentSerializer,
    DocumentListSerializer,
    DocumentCreateSerializer,
    DocumentUpdateSerializer,
    EmployeeDocumentListSerializer,
)

__all__ = [
    'DocumentTypeSerializer',
    'DocumentTypeListSerializer',
    'DocumentTypeCreateUpdateSerializer',
    'DocumentSerializer',
    'DocumentListSerializer',
    'DocumentCreateSerializer',
    'DocumentUpdateSerializer',
    'EmployeeDocumentListSerializer',
]
