#!/usr/bin/env python3
"""
Views for Document management.

Permission Structure:
- Superusers can manage all documents (CRUD)
- Authenticated employees can view their own documents only
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from ..models import Document
from ..serializers import (
    DocumentSerializer,
    DocumentListSerializer,
    DocumentCreateSerializer,
    DocumentUpdateSerializer,
    EmployeeDocumentListSerializer,
)


class IsSuperUser(permissions.BasePermission):
    """Permission class that only allows superusers."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser


class DocumentListCreateView(generics.ListCreateAPIView):
    """
    Super admin-only view.

    GET: List all documents
    POST: Create a new document
    """
    permission_classes = [IsSuperUser]
    
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
    Super admin-only view for managing individual documents.

    GET: Retrieve document details
    PUT/PATCH: Update document data
    DELETE: Deactivate document (soft delete by setting is_active=False)
    """
    queryset = Document.objects.select_related(
        'employee', 'document_type', 'uploaded_by'
    )
    permission_classes = [IsSuperUser]
    
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
    Super admin-only view.

    GET: List only active documents
    """
    permission_classes = [IsSuperUser]
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
    permission_classes = [IsSuperUser]
    serializer_class = DocumentListSerializer
    
    def get_queryset(self):
        employee_id = self.kwargs.get('employee_id')
        return Document.objects.select_related(
            'employee', 'document_type', 'uploaded_by'
        ).filter(employee_id=employee_id).order_by('-created_at')
