#!/usr/bin/env python3
"""Branch model and all related functionalities for the Silver HR application."""
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from .city import City

class Branch(models.Model):
    """
    Model representing a branch.
    Physical branch locations within a city.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100) # Branch name
    description = models.TextField(blank=True, null=True) # Branch description
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='branches') # Associated city
    is_active = models.BooleanField(default=True) # Active status for soft deletion
    location = models.URLField(max_length=512, blank=True, null=True) # Branch location URL (e.g., Google Maps link)
    created_at = models.DateTimeField(auto_now_add=True) # Timestamp for creation
    updated_at = models.DateTimeField(auto_now=True) # Timestamp for last update
    
    class Meta:
        unique_together = ('name', 'city') # Ensure branch names are unique within a city
        verbose_name = _("Branch")
        verbose_name_plural = _("Branches")
    def __str__(self):
        return f"{self.name} - {self.city.name}"
    
    