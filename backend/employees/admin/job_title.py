#!/usr/bin/env python3
"""Admin configuration for the JobTitle model."""

from django.contrib import admin

from ..models import JobTitle


@admin.register(JobTitle)
class JobTitleAdmin(admin.ModelAdmin):
    """Admin configuration for JobTitle model."""
    
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('name',)
