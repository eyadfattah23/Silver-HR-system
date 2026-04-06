#!/usr/bin/env python3
"""
Views for Document management.

Permission Structure:
- Users with documents.view: Can view all documents (within their scope)
- Users with documents.create: Can create documents
- Users with documents.update: Can update documents (within their scope)
- Users with documents.delete: Can deactivate documents (within their scope)
- Users with documents.view_own: Can view their own documents
- Superusers: Full access
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from permissions.utils import has_permission, IsSuperUserOrHasPermission

from ..models import Document
from ..serializers import (
    DocumentSerializer,
    DocumentListSerializer,
    DocumentCreateSerializer,
    DocumentUpdateSerializer,
    EmployeeDocumentListSerializer,
)


class HasDocumentPermission(permissions.BasePermission):
    """
    Permission class for document endpoints.
    Maps HTTP methods to permission codes.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        # Map methods to permissions
        method_permission_map = {
            'GET': 'documents.view',
            'POST': 'documents.create',
            'PUT': 'documents.update',
            'PATCH': 'documents.update',
            'DELETE': 'documents.delete',
        }
        
        required_permission = method_permission_map.get(request.method)
        if not required_permission:
            return False
        
        return has_permission(request.user, required_permission)


class DocumentListCreateView(generics.ListCreateAPIView):
    """
    View for listing and creating documents.

    GET: List all documents (requires documents.view)
    POST: Create a new document (requires documents.create)
    """
    permission_classes = [HasDocumentPermission]
    
    def get_queryset(self):
        queryset = Document.objects.select_related(
            'employee', 'document_type', 'uploaded_by'
        ).order_by('-created_at')
        
        # Filter by employee if provided
        employee_id = self.request.query_params.get('employee')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        # Filter by document type if provided
        document_type_id = self.request.query_params.get('document_type')
        if document_type_id:
            queryset = queryset.filter(document_type_id=document_type_id)
        
        # Filter by active status if provided
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DocumentCreateSerializer
        return DocumentListSerializer


class DocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for managing individual documents.

    GET: Retrieve document details (requires documents.view)
    PUT/PATCH: Update document data (requires documents.update)
    DELETE: Deactivate document (requires documents.delete)
    """
    queryset = Document.objects.select_related(
        'employee', 'document_type', 'uploaded_by'
    )
    permission_classes = [HasDocumentPermission]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return DocumentUpdateSerializer
        return DocumentSerializer

    def destroy(self, request, *args, **kwargs):
        """Soft delete: set is_active to False instead of deleting."""
        document = self.get_object()
        document.is_active = False
        document.save()
        return Response(
            {'detail': 'Document deactivated successfully.'},
            status=status.HTTP_200_OK
        )


class EmployeeDocumentListView(generics.ListAPIView):
    """
    Authenticated employee view.

    GET: List only the authenticated employee's own documents
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EmployeeDocumentListSerializer
    
    def get_queryset(self):
        return Document.objects.select_related('document_type').filter(
            employee=self.request.user,
            is_active=True,
        ).order_by('-created_at')


class EmployeeDocumentDetailView(generics.RetrieveAPIView):
    """
    Authenticated employee view.

    GET: Retrieve details of the employee's own document
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EmployeeDocumentListSerializer
    
    def get_queryset(self):
        return Document.objects.select_related('document_type').filter(
            employee=self.request.user,
            is_active=True,
        )


class ActiveDocumentListView(generics.ListAPIView):
    """
    View for listing active documents.

    GET: List only active documents (requires documents.view)
    """
    permission_classes = [HasDocumentPermission]
    serializer_class = DocumentListSerializer
    
    def get_queryset(self):
        queryset = Document.objects.select_related(
            'employee', 'document_type', 'uploaded_by'
        ).filter(is_active=True).order_by('-created_at')
        
        # Filter by employee if provided
        employee_id = self.request.query_params.get('employee')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        # Filter by document type if provided
        document_type_id = self.request.query_params.get('document_type')
        if document_type_id:
            queryset = queryset.filter(document_type_id=document_type_id)
        
        return queryset


class EmployeeDocumentsView(generics.ListAPIView):
    """
    Super admin-only view.

    GET: List all documents for a specific employee (by employee ID in URL)
    """
    permission_classes = [IsSuperUserOrHasPermission]
    required_permission = 'documents.view'
    serializer_class = DocumentListSerializer
    
    def get_queryset(self):
        employee_id = self.kwargs.get('employee_id')
        return Document.objects.select_related(
            'employee', 'document_type', 'uploaded_by'
        ).filter(employee_id=employee_id).order_by('-created_at')
