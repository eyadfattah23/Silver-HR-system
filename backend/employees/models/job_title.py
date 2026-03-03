#!/usr/bin/env python3
"""JobTitle model for employee job positions."""
import uuid
from django.db import models


class JobTitle(models.Model):
    """Lookup table for job titles."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, help_text='Job title in Arabic')
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Job Title'
        verbose_name_plural = 'Job Titles'
        ordering = ['name']

    def __str__(self):
        return self.name
