#!/usr/bin/env python3
"""
Views for DocumentType management.

Permission Structure:
- Only superusers can manage document types (CRUD)
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from ..models import DocumentType
from ..serializers import (
    DocumentTypeSerializer,
    DocumentTypeListSerializer,
    DocumentTypeCreateUpdateSerializer,
)


class IsSuperUser(permissions.BasePermission):
    """Permission class that only allows superusers."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser


class DocumentTypeListCreateView(generics.ListCreateAPIView):
    """
    Super admin-only view.

    GET: List all document types
    POST: Create a new document type
    """
    queryset = DocumentType.objects.all().order_by('name')
    permission_classes = [IsSuperUser]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DocumentTypeCreateUpdateSerializer
        return DocumentTypeListSerializer


class DocumentTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Super admin-only view for managing individual document types.

    GET: Retrieve document type details
    PUT/PATCH: Update document type data
    DELETE: Deactivate document type (soft delete by setting is_active=False)
    """
    queryset = DocumentType.objects.all()
    permission_classes = [IsSuperUser]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return DocumentTypeCreateUpdateSerializer
        return DocumentTypeSerializer

    def destroy(self, request, *args, **kwargs):
        """Soft delete: set is_active to False instead of deleting."""
        document_type = self.get_object()
        document_type.is_active = False
        document_type.save()
        return Response(
            {'detail': 'Document type deactivated successfully.'},
            status=status.HTTP_200_OK
        )


class ActiveDocumentTypeListView(generics.ListAPIView):
    """
    Super admin-only view.

    GET: List only active document types
    """
    queryset = DocumentType.objects.filter(is_active=True).order_by('name')
    permission_classes = [IsSuperUser]
    serializer_class = DocumentTypeListSerializer
