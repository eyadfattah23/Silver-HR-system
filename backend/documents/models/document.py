#!/usr/bin/python3
"""Documents system models for the Silver HR application."""
import uuid

from django.db import models


class DocumentType(models.Model):
    """Model representing a type of document (e.g. 'Contract', 'Payslip', 'ID Card')."""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = 'Document Type'
        verbose_name_plural = 'Document Types'
    
    def __str__(self):
        return self.name

class Document(models.Model):
    """Model representing a document associated with an employee."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='documents')
    document_type = models.ForeignKey(DocumentType, on_delete=models.CASCADE, related_name='documents')
    
    file_name = models.CharField(max_length=255)
    file_format = models.CharField(max_length=20) # e.g. 'pdf', 'docx', 'jpg'
    file_size = models.PositiveIntegerField() # in bytes
    file_path = models.FileField(upload_to='documents/')
    description = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    expiration_date = models.DateField(null=True, blank=True) # Optional expiration date for the document (e.g. ID card)
    notes = models.TextField(blank=True) # Optional notes about the document
    
    uploaded_by = models.ForeignKey(
        'employees.Employee',
        on_delete=models.PROTECT,
        related_name='documents_uploaded'
    )
    
    class Meta:
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
        indexes = [
            models.Index(fields=['employee']),
            models.Index(fields=['document_type']),
            models.Index(fields=['employee', 'document_type']),
            
        ]
    def __str__(self):
        return f"{self.document_type.name} - {self.employee}"
