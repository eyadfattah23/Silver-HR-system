#!/usr/bin/env python3
"""Core models for the Silver HR application. (City, Branch, Department)"""

import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from .branch import Branch

class Department(models.Model):
    """
    Model representing a department.
    Departments within the company (e.g., HR, Sales, IT).
    Note: Cannot be nested.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='departments') # Associated branch
    name = models.CharField(max_length=100, unique=True) # Department name
    code = models.CharField(max_length=10, unique=True) # Department code (e.g., "HR":"HR", "Sales":"SA", "IT":"IT")
    description = models.TextField(blank=True, null=True) # Department description
    is_active = models.BooleanField(default=True) # Active status for soft deletion
    created_at = models.DateTimeField(auto_now_add=True) # Timestamp for creation
    updated_at = models.DateTimeField(auto_now=True) # Timestamp for last update
    
    
    class Meta:
        unique_together = ('name', 'branch') # Unique department name per branch
        unique_together = ('code', 'branch') # Unique department code per branch
    def __str__(self):
        return f"{self.name} - {self.branch.name}"
