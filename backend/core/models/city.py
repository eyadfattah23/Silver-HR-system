#!/usr/bin/env python3
"""City model and all related functionalities for the Silver HR application."""
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

class City(models.Model):
    """
    Model representing a city.
    Cities where branches are located. Used for HR jurisdiction.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True) # City name
    code = models.CharField(max_length=10, unique=True) # City code (e.g., "Cairo":"Ca", "Ismailia":"Is")
    is_active = models.BooleanField(default=True) # Active status for soft deletion
    created_at = models.DateTimeField(auto_now_add=True) # Timestamp for creation
    updated_at = models.DateTimeField(auto_now=True) # Timestamp for last update
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _("City")
        verbose_name_plural = _("Cities")
