#!/usr/bin/env python3
"""Department admin configuration for the Silver HR application."""

from django.contrib import admin
from ..models import Department

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Admin configuration for the Department model."""
    list_display = ('name', 'branch', 'code', 'is_active')
    list_filter = ('branch', 'is_active')
    search_fields = ('name', 'code', 'branch__name', 'branch__city__name')
    readonly_fields = ('created_at', 'updated_at')
    list_select_related =  ('branch', 'branch__city')
    ordering = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name', 'branch', 'code', 'description', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )   
