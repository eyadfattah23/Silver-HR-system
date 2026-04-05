#!/usr/bin/python3
"""Permission model for the Silver HR application."""
import uuid
from django.db import models


class Permission(models.Model):
    """Model representing a permission that can be assigned to roles."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=100, unique=True) # e.g. 'view_employee', 'edit_employee', etc.
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    resource = models.CharField(max_length=50) # e.g. 'employees', 'documents', 'attendance', 'salary'
    action = models.CharField(max_length=50) # e.g. 'create', 'read', 'update', 'delete', 'approve', 'delegate'
    can_be_given = models.BooleanField(default=True) # Can this permission be delegated to others?
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['resource', 'action']),
            models.Index(fields=['code'])
        ]
    
    def __str__(self):
        """String representation of the permission."""
        return f"{self.resource}.{self.action}"
