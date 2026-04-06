#!/usr/bin/env python3
"""
Views for DocumentType management.

Permission Structure:
- Users with document_types.view: Can view document types
- Users with document_types.manage: Can create, update, delete document types
- Superusers: Full access
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from permissions.utils import has_permission

from ..models import DocumentType
from ..serializers import (
    DocumentTypeSerializer,
    DocumentTypeListSerializer,
    DocumentTypeCreateUpdateSerializer,
)


class HasDocumentTypePermission(permissions.BasePermission):
    """
    Permission class for document type endpoints.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        # Safe methods require view permission
        if request.method in permissions.SAFE_METHODS:
            return has_permission(request.user, 'document_types.view')
        
        # Unsafe methods require manage permission
        return has_permission(request.user, 'document_types.manage')


class DocumentTypeListCreateView(generics.ListCreateAPIView):
    """
    View for listing and creating document types.

    GET: List all document types (requires document_types.view)
    POST: Create a new document type (requires document_types.manage)
    """
    queryset = DocumentType.objects.all().order_by('name')
    permission_classes = [HasDocumentTypePermission]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DocumentTypeCreateUpdateSerializer
        return DocumentTypeListSerializer


class DocumentTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for managing individual document types.

    GET: Retrieve document type details (requires document_types.view)
    PUT/PATCH: Update document type data (requires document_types.manage)
    DELETE: Deactivate document type (requires document_types.manage)
    """
    queryset = DocumentType.objects.all()
    permission_classes = [HasDocumentTypePermission]
    
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
    View for listing active document types.

    GET: List only active document types (requires document_types.view)
    """
    queryset = DocumentType.objects.filter(is_active=True).order_by('name')
    permission_classes = [HasDocumentTypePermission]
    serializer_class = DocumentTypeListSerializer
